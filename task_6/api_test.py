# from api_02 import get_api
import requests
from api_02 import item_search
from api_03 import product_price_limit
from api_04 import product_ranking
import pprint 

def get_api(url):
    result = requests.get(url)
    return result.json()
    

def test_get_api():
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706?format=json&keyword={PS5}&applicationId=1019079537947262807"
    res = get_api(url=url)
    
    # チェック
    # 正常系　→　うまくいった時の処理
    assert len(res["Items"]) >= 1
    assert res["Items"][0]["Item"]["itemCode"]
    
    # 異常系　→　失敗時の処理
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706?format=json&keyword={PS5ああああああああああ}&applicationId=1019079537947262807"
    res = get_api(url=url)
    
    assert len(res["Items"]) == 0
    
def test_item_search():
    keyword = "鬼滅"
    res = item_search(keyword)
    
    assert res["Items"]
    assert res["Items"][0]["Item"]["itemName"]
    assert res["Items"][0]["Item"]["itemPrice"]
    
def test_product_price_limit():
    res = product_price_limit()
    
    assert res["Products"]
    assert res["Products"][0]["Product"]["minPrice"]
    assert res["Products"][0]["Product"]["maxPrice"]
    
def test_product_ranking():
    res = product_ranking()
    
    assert res["Items"]
    assert res["Items"][0]["Item"]["itemName"]
    assert res["Items"][0]["Item"]["itemPrice"]



