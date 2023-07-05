import requests
import re
from requests import Session
from typing import List, Tuple, TypedDict
import jieba

HOST_URL = "http://district.ce.cn/zt/rwk/index.shtml"


def get_main():
    """获取主要入口数据"""
    data = requests.get(HOST_URL)
    data.encoding = "gbk"
    city_list = re.findall(
        r'<a href="(.*?)" target="_blank"><font color="#0066FF"><b>(.*?)</b></font></a>',
        data.text,
    )

    for [href, area_name] in city_list:
        # data = requests.get(href)
        # data.encoding = "gbk"
        # # 获取主要人物
        # renwu = re.findall(
        #     r'<div class="renwu"><a href=".*?".*?><img src="(.*?)".*?></a><br/><a href="(.*?)".*?>(.*?)</a></div>',
        #     data.text,
        # )
        # print(renwu)
        get_renwu(
            {
                'renwu_url': href,
                'area_name': area_name,
            }
        )
        # break

    pass


def get_renwu(params: dict):
    renwu_url = params.get('renwu_url', '')
    area_name = params.get('area_name', '')
    res = requests.get(renwu_url)
    res.encoding = 'gbk'

    # with open('./data.html', 'a+', encoding='utf-8') as f:
    #     f.write(res.text)
    datas: List[Tuple[str, str, str]] = re.findall(
        r'<td.*?href="(.*?)".*?>([\u4e00-\u9fa5、]+)<.*?>([\u4e00-\u9fa5、，]+)<.*?/td>',
        res.text,
        re.S,
    )
    print(datas)
    for jianli_url, user_name, job_str in datas:
        job_list = re.split(r'，|、', job_str.strip())

        jobss = []
        if len(job_list) > 1:
            print(user_name, job_list)
        for job in job_list:
            if not job:
                continue
            if job.count('市委书记') > 0:
                jobs = list(jieba.cut(job))
                print(jobs)
                job = jobs[-1]
            # addJob(
            #     {
            #         "job_name": job,
            #         "job_superior": 0,
            #         "job_history_create": '',
            #     }
            # )
            jobss.append(job)
        jobres = requests.post(
            'http://localhost:7001/web/query_job',
            json={
                'filter': {"job_name": jobss},
            },
        )
        data = jobres.json()
        if len(data['data']) > 0:

            addOfficer(
                {
                    "officer_name": user_name,
                    "officer_job": list(
                        map(lambda item: int(item['job_id']), data['data'])
                    ),
                    "officer_level": 0,
                    "officer_area": area_name,
                    'officer_superior': 0,
                    'officer_history_create': '',
                    "officer_avatar": '',
                }
            )


def get_buwei(url):
    res = requests.post(
        url,
        json={
            "appCode": "PC42ce3bfa4980a9",
            "token": "",
            "signature": "3be29e33cb708b79a3802f663cf8f16e",
            "param": "{}",
        },
        proxies={'http': {}, 'https': {}},
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        },
    )
    data = res.json()
    for item in data['resultData']['forums']:
        addDepartment(
            {
                "department_name": item['name'],
                "department_superior": 0,
                "department_website": '',
            }
        )


def addJob(params: dict):
    res = requests.post('http://localhost:7001/web/add_job', params)
    print(res.text)


def addOfficer(params: dict):
    res = requests.post('http://localhost:7001/web/add_officer', params)
    print(res.text)


def addDepartment(params: dict):
    res = requests.post('http://localhost:7001/web/add_department', params)
    print(res.text)


def main():
    get_main()
    # get_buwei('https://liuyan.people.com.cn/v1/forum/getTopBwForums')


if __name__ == "__main__":
    main()
