import requests
import urllib
import pandas as pd


def get_api(url, params: dict):
    result = requests.get(url, params=params)
    return result.json()

# 課題３
def product_price_limit():
    url = "https://app.rakuten.co.jp/services/api/Product/Search/20170426"
    
    # パラメータを記述
    params = {
        "format": "json",
        "applicationId": "1019079537947262807",
        "productId": "3cae0110c1371d976812ac71abee8d4a"
    }
    
    res = get_api(url, params=params)
    
    print(f"商品名>>{res['Products'][0]['Product']['productName']}\n最高値>>{res['Products'][0]['Product']['maxPrice']}\n最安値>>{res['Products'][0]['Product']['minPrice']}")
    
    return res
    

product_price_limit()


