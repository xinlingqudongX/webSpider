import requests
import re
from lxml import etree
import jieba
import jieba.posseg as pseg
import jieba.analyse

HOST_URL = 'http://district.ce.cn/zt/rwk/sf/sx/index.shtml'
# jieba.enable_parallel()


def get_renwu():
    res = requests.get(HOST_URL)
    res.encoding = 'gbk'

    # with open('./data.html', 'a+', encoding='utf-8') as f:
    #     f.write(res.text)
    datas = re.findall(
        r'<td.*?href="(.*?)".*?>([\u4e00-\u9fa5、]+)<.*?>([\u4e00-\u9fa5、，]+)<.*?/td>',
        res.text,
        re.S,
    )
    # print(datas)

    for [jianli_url, name, job] in datas:
        get_jianli({"url": jianli_url, "name": name})
        # break


def get_jianli(params):
    url = params.get('url')
    name = params.get('name')
    res = requests.get(url)
    res.encoding = 'gbk'

    tree = etree.HTML(res.text, etree.HTMLParser())
    data = tree.xpath('//*[@id="articleText"]//div[@class="TRS_Editor"]//text()')
    img = tree.xpath('//*[@id="articleText"]//div[@class="TRS_Editor"]//img/@src')
    if len(data) <= 0:
        with open(f'./{name}.html', 'a+', encoding='utf-8') as f:
            f.write(res.text)
    print(data)
    # for i in data:
    #     cut_fenci(i)


def cut_fenci(words: str):
    data = jieba.analyse.extract_tags(words.strip())
    print(data)
    # for word, flag in data:
    #     print('%s %s'.format(word, flag))


def main():
    get_renwu()


if __name__ == '__main__':
    main()
