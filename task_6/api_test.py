# from api_02 import get_api
import requests
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

def test_2():
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706?format=json&keyword=PS5&applicationId=1019079537947262807"
    res = get_api(url=url)
    
    assert res.get("Items") == None