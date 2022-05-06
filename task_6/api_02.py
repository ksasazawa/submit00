import requests
import urllib
import pandas as pd


def get_api(url, params: dict):
    result = requests.get(url, params=params)
    return result.json()

# 課題２
def item_search(keyword: str):
    keyword = keyword
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"
    
    # パラメータを記述
    params = {
        "format": "json",
        "keyword": keyword,
        "applicationId": "1019079537947262807",
        "minPrice": 111
    }
    
    res = get_api(url, params=params)
    
    for i in range(len(res['Items'])):
        print(f"商品名>>{res['Items'][i]['Item']['itemName']}\n価格>>{res['Items'][i]['Item']['itemPrice']}\n")

keyword = input("検索ワードを入力してください。：")
item_search(keyword)
    
    