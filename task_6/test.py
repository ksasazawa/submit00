# APIリクエストに必要なライブラリ
import requests
# URL＋クエリパラメータ
url = 'https://zipcloud.ibsnet.co.jp/api/search?zipcode=2220036'
# APIリクエストを送信
res = requests.get(url)
res_json = res.json()
results = res_json['results'][0]
address = results['address1'] + results['address2'] + results['address3']
print(address)


