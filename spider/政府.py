import requests
import re
from pypinyin import pinyin, lazy_pinyin, Style
import json
from pathlib import Path

# import jieba
# import jieba.analyse


"""获取城市名称"""


def get_city(filepath: str):
    fdata = open(filepath, "r", encoding="utf8")
    city_data = json.loads(fdata.read())
    fdata.close()
    city_list = []
    for item in city_data:
        # print(list(jieba.tokenize(item["name"])))
        # print(list(jieba.analyse.extract_tags(item["name"])))
        replace_list = ["省", "市", "区", "自治区", "维吾尔", "壮族", "自治", "回族"]
        for i in replace_list:
            item["name"] = item["name"].replace(i, "")
        name = item["name"]
        city_list.append(name)

    return city_list


def get_url(city_list):
    """生成地址"""
    urls = []
    for city_name in city_list:
        name = ""
        py = pinyin(city_name, style=Style.FIRST_LETTER)
        name = "".join(map(lambda item: item[0], py))
        url = f"http://www.{name}.gov.cn"
        urls.append({"city_name": city_name, "url": url})

        url = f"http://www.{name}zf.gov.cn"
        urls.append({"city_name": city_name, "url": url})

        py = lazy_pinyin(city_name)
        name = "".join(py)
        url = f"http://www.{name}.gov.cn"
        urls.append({"city_name": city_name, "url": url})

    return urls


def check_urls(urls):
    url_list = []
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    }
    for item in urls:
        url = item["url"]
        try:

            res = requests.get(url, headers=head, timeout=5)
            res.encoding = "utf-8"
        except Exception as e:
            continue

        if res.status_code >= 500:
            print(url, item["city_name"], res.status_code)
            continue
        # data = re.findall(r".{2}人民政府", res.text)
        # print(data)

        url_list.append(item)

    return url_list


def update_province(item_list):
    res = requests.post("")
    print(res.text)


def post_payload(params):
    res = requests.post("http://localhost:7001/web/add_department", json=params)
    print(res.status_code, res.text)


def main():

    # city_list = get_city("./provinces.json")
    filePath = Path(__file__).parent.joinpath('组织.json')
    department_list = json.load(open(filePath, encoding="utf8"))
    # urls = get_url(city_list)
    # urls = check_urls(urls)
    # print(json.dumps(urls))
    urls = json.loads(
        """[
            {"city_name": "\u5317\u4eac", "url": "http://www.beijing.gov.cn"}, 
            {"city_name": "\u5929\u6d25", "url": "http://www.tj.gov.cn"}, 
            {"city_name": "\u6cb3\u5317", "url": "http://www.hebei.gov.cn"}, 
            {"city_name": "\u5c71\u897f", "url": "http://www.shanxi.gov.cn"}, 
            {"city_name": "\u5185\u8499\u53e4", "url": "http://www.nmg.gov.cn"}, 
            {"city_name": "\u8fbd\u5b81", "url": "http://www.ln.gov.cn"}, 
            {"city_name": "\u5409\u6797", "url": "http://www.jl.gov.cn"}, 
            {"city_name": "\u9ed1\u9f99\u6c5f", "url": "http://www.hlj.gov.cn"}, 
            {"city_name": "\u4e0a\u6d77", "url": "http://www.shanghai.gov.cn"}, 
            {"city_name": "\u6c5f\u82cf", "url": "http://www.jiangsu.gov.cn"}, 
            {"city_name": "\u6d59\u6c5f", "url": "http://www.zj.gov.cn"}, 
            {"city_name": "\u5b89\u5fbd", "url": "http://www.ah.gov.cn"}, 
            {"city_name": "\u798f\u5efa", "url": "http://www.fujian.gov.cn"}, 
            {"city_name": "\u6c5f\u897f", "url": "http://www.jiangxi.gov.cn"}, 
            {"city_name": "\u5c71\u4e1c", "url": "http://www.sd.gov.cn"}, 
            {"city_name": "\u5c71\u4e1c", "url": "http://www.shandong.gov.cn"}, 
            {"city_name": "\u6cb3\u5357", "url": "http://www.henan.gov.cn"}, 
            {"city_name": "\u6e56\u5317", "url": "http://www.hubei.gov.cn"}, 
            {"city_name": "\u6e56\u5357", "url": "http://www.hunan.gov.cn"}, 
            {"city_name": "\u5e7f\u4e1c", "url": "http://www.gd.gov.cn"}, 
            {"city_name": "\u5e7f\u897f", "url": "http://www.gxzf.gov.cn"}, 
            {"city_name": "\u6d77\u5357", "url": "http://www.hainan.gov.cn"}, 
            {"city_name": "\u91cd\u5e86", "url": "http://www.cq.gov.cn"}, 
            {"city_name": "\u56db\u5ddd", "url": "http://www.sc.gov.cn"}, 
            {"city_name": "\u8d35\u5dde", "url": "http://www.gzzf.gov.cn"}, 
            {"city_name": "\u8d35\u5dde", "url": "http://www.guizhou.gov.cn"}, 
            {"city_name": "\u4e91\u5357", "url": "http://www.yn.gov.cn"}, 
            {"city_name": "\u897f\u85cf", "url": "http://www.xizang.gov.cn"}, 
            {"city_name": "\u9655\u897f", "url": "http://www.shanxi.gov.cn"}, 
            {"city_name": "\u7518\u8083", "url": "http://www.gansu.gov.cn"}, 
            {"city_name": "\u9752\u6d77", "url": "http://www.qinghai.gov.cn"},
             {"city_name": "\u5b81\u590f", "url": "http://www.nx.gov.cn"}, 
             {"city_name": "\u65b0\u7586", "url": "http://www.xj.gov.cn"}
             ]"""
    )
    print(urls)
    # tt = set(map(lambda item: item["city_name"], urls))
    # sub = set(city_list) - tt
    # print(sub)
    for item in department_list:
        post_payload(
            {
                "department_name": item,
                "department_superior": 0,
                "department_website": "",
            }
        )


if __name__ == "__main__":
    main()
