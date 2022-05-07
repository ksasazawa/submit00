import requests
import urllib
import pandas as pd


def get_api(url, params: dict):
    result = requests.get(url, params=params)
    return result.json()

# 課題4
def product_ranking():
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Ranking/20170628"
    rk = pd.DataFrame(columns=['ランク','商品名','価格','URL'])
    
    # パラメータを記述
    params = {
        "format": "json",
        "applicationId": "1019079537947262807",
        "genreId": "101941"
    }
    
    res = get_api(url, params=params)
    
    for i in range(len(res['Items'])):
        addRow = [res['Items'][i]['Item']['rank'],res['Items'][i]['Item']['itemName'],res['Items'][i]['Item']['itemPrice'],res['Items'][i]['Item']['itemUrl']]
        rk.loc[i] = addRow
    
    rk.to_csv('./rank.csv', encoding="utf-8")
    
    return res
    

product_ranking()