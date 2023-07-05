from requests import Session, request
from requests.adapters import HTTPAdapter
from typing import TypedDict, List, Tuple, Dict

class RequestParams(TypedDict):
    start_url: str
    custom_header: dict
    coding: str
    method: str

def netRequest(params: RequestParams):
    method = params.get('method')
    headers = params.get('custom_header')
    start_url = params.get('start_url')
    coding = params.get('coding')
    file_type = params.get('file_type','')


    res = request(method=method, headers=headers, url=start_url)
    resj = res.text
    if file_type.upper() == 'JSON':
        resj = res.json()
    return resj