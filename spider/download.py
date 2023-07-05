# 导入requests和re模块
import requests
import re
from typing import Set, List
from pathlib import Path
from time import sleep
import atexit
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from json import dumps, loads

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
# 定义目标网址
ssl_verify = False
start_domain = 'https://www.gov.cn'
# start_domain = 'https://www.gov.cn/2016public/bottom.htm'
# start_domain = 'http://www.cppcc.gov.cn/'
exclude_suffix = ['jpg','png','web','js','css']
check_set:Set[str] = set()
download_set:Set[str] = set()
domain_set: Set[str] = set()
# 中文正则
reg = re.compile(r'([\u4e00-\u9fa5]+)')

check_file = 'check_links.txt'
download_file = 'download_links.txt'
domain_file = 'domain.txt'
domain_json = 'domain.json'
domain_obj = {}

def extra_url(nowUrl:str, content:str):
    scheme = urlparse(nowUrl)
    domain = f'{scheme.scheme}://{scheme.hostname}'
    protocol = scheme.scheme
    links = []
    domain_set.add(domain)
    html = BeautifulSoup(content,'html.parser')
    titleElement = html.find('title')
    if titleElement and titleElement.text.strip():
        title = reg.findall(titleElement.text)
        if title:
            domain_obj.setdefault(scheme.hostname,title[0])
            requests.post('http://localhost:7001/web/add_department',json={'department_name':title[0],'department_website':scheme.hostname})
        else:
            domain_obj.setdefault(scheme.hostname,titleElement.text.strip())
            requests.post('http://localhost:7001/web/add_department',json={'department_name':titleElement.text.strip(),'department_website':scheme.hostname})

    linkQuery = html.findAll(['a','iframe'])
    for link in linkQuery:
        url = ''
        if link.has_attr('href'):
            # print(link['href'])
            url:str = link['href']
            url = url.strip()
            if any([url.startswith('http'),url.startswith('/'),url.startswith('//'), url.startswith('..'), url.startswith('.')]):
                if url.startswith('/'):
                    url = domain + url
                if url.startswith('//'):
                    url = f'{protocol}:{url}'
                if url.startswith('..') or url.startswith('.'):
                    url = urljoin(nowUrl,url)
                    print(url)

            else:
                print(url,'特殊格式',nowUrl)
                if 'http' in url:
                    print('1')
                continue

        if link.has_attr('src'):
            # print(link['src'])
            url:str = link['src']
            if url.startswith('/'):
                url = domain + url
            if url.startswith('//'):
                url = f'{protocol}:{url}'

        if url:
            links.append(url)

    # pattern = r"https?://[\w./?&=-]+"
    # all_links = re.findall(pattern, content)
    # pattern = r'href="(/.*?)"'
    # href_links:List[str] = re.findall(pattern, content)
    # for index in range(len(href_links)):
    #     if href_links[index].startswith('/') and not href_links[index].startswith('//'):
    #         href_links[index] = nowUrl + href_links[index]
    # href_links = list(filter(lambda item:item.startswith('http'),href_links))
    # links = [*href_links,*all_links]
    return links

def downloadData(downloadUrl:str):
    urlData = urlparse(downloadUrl)
    print('正在请求:',downloadUrl)
    header = {
        'Cookie':'arialoadData=true; ariawapChangeViewPort=true; Hm_lvt_b4ae0087f7b17481d650cc0a8574f040=1682603867; insert_cookie=37836164; Hm_lpvt_b4ae0087f7b17481d650cc0a8574f040=1682605043',
        'Host':urlData.hostname,
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Accept-Encoding': 'identity'
    }
    try:
        response = requests.get(downloadUrl, verify=ssl_verify, headers=header, proxies={'http':'','https':''}, timeout=5)
    except Exception as err:
        print(downloadUrl, '错误',err)
        return
    if response.status_code in [500,403,404]:
        print(downloadUrl, '无法请求')
        return
    check_set.add(urlData.hostname)
    # pos = response.text.find('charset')
    # vals = re.findall(r'charset="?([a-zA-Z0-9-]+)',response.text[pos:pos + 40])
    # if vals:
    #     charset = vals[0]
    # else:
    #     charset = 'utf-8'
    charset = checkCharset(response.content) or 'utf-8'
    try:

        content = response.content.decode(charset)
    except Exception as err:
        return
    urls = extra_url(downloadUrl, content)
    for url in urls:
        if not checkValidUrl(url):
            continue
        urlDatas = urlparse(url)

        checkUrl = Path(url)
        if checkUrl.suffix.strip('.') in exclude_suffix:
            continue
        
        if urlDatas.hostname in check_set or 'gov' not in urlDatas.hostname :
            continue
        else:
            download_set.add(url)

def main():
    load_data()
    if len(download_set) <= 0:
        download_set.add(start_domain)

    while len(download_set) > 0:
        download_url = download_set.pop()
        downloadData(download_url)
        sleep(0.2)
        
    print('下载结束')

def save_data():
    with open(check_file,'w',encoding='utf8') as f:
        f.write('\n'.join(list(check_set)))
    with open(download_file,'w',encoding='utf8') as f:
        f.write('\n'.join(list(download_set)))
    with open(domain_file,'w',encoding='utf8') as f:
        f.write('\n'.join(list(domain_set)))
    with open(domain_json,'w',encoding='utf8') as f:
        f.write(dumps(domain_obj))

def load_data():
    global check_set
    global download_set
    if Path(check_file).exists():
        with open(check_file,encoding='utf8') as f:
            check_set = set(f.readlines())
    if Path(download_file).exists():
        with open(download_file,encoding='utf8') as f:
            download_links = map(lambda item:item.strip(),f.readlines())
            download_set = set(download_links)

def checkValidUrl(url) -> bool:
    urlData = urlparse(url)
    if not urlData.hostname or not urlData.scheme or not urlData.path:
        return False
    return True

def checkCharset(content:bytes):
    charsets = ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']
    charset = None
    for c in charsets:
        try:
            content.decode(c)
        except:
            continue
    return charset

if __name__ == '__main__':
    atexit.register(save_data)
    main()