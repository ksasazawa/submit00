import os
import re
import platform
import time
import datetime

import requests
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# LOGファイルパス
LOG_FILE_PATH = "log/log_{datetime}.log"
log_file_path = LOG_FILE_PATH.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))


# ファイルの作成
def makedir_for_filepath(filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    
# ログとコンソールへの出力
def log(txt):
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logStr = '[%s: %s] %s' % ('log', now , txt)
    # ログ出力
    makedir_for_filepath(log_file_path)
    with open(log_file_path, 'a', encoding='utf-8_sig') as f:
        f.write(logStr + '\n')
    print(logStr)


def main(df, limit):
    
    # # ドライバの定義
    # def set_driver():
        
    #     #インストールされているChromeのヴァージョンを取得
    #     def get_chrome_version(cmd):
    #         pattern = r'\d+\.\d+\.\d+' # 正規表現
    #         stdout = os.popen(cmd).read() # cmdをターミナルで打った時に出てくる文字列「Chrome Version : 104.0.5112」を格納
    #         version = re.search(pattern, stdout) # 「Chrome Version : 104.0.5112」のうち、設定した正規表現に合う文字列を取得
    #         chrome_version = version.group(0) # 取得した文字列を格納
    #         print('Chrome Version : ' + chrome_version)
    #         return chrome_version
        
    #     #Chromeのヴァージョンから、適合する最新のChromeDriverのヴァージョンを取得
    #     def get_chrome_driver_version(chrome_version):
    #         url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_' + chrome_version
    #         response = requests.request('GET', url)
    #         print('ChromeDriver Version : ' + response.text)
    #         return response.text

    #     #OSを判別してヴァージョン確認のコマンドとChromeの格納先を取得
    #     pf = platform.system() # OSの表示
    #     if pf == 'Windows':
    #         print('OS : Windows')
    #         cmd = r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome Beta\BLBeacon" /v version' #cmd：それぞれのOSでChrome(Beta)のヴァージョンを確認するコマンド
    #         location = 'C:/Program Files/Google/Chrome Beta/Application/chrome.exe' #location：Chrome(Beta)の場所
    #     elif pf == 'Darwin':
    #         print('OS : Mac')
    #         cmd = r'/Applications/Google\ Chrome\ Beta.app/Contents/MacOS/Google\ Chrome\ Beta --version' #cmd：それぞれのOSでChrome(Beta)のヴァージョンを確認するコマンド
    #         location = '/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta' #location：Chrome(Beta)の場所

    #     #Chromeのヴァージョン取得
    #     chrome_version = get_chrome_version(cmd)

    #     #Chromeのヴァージョンから、適合する最新のChromeDriverのヴァージョンを取得
    #     driver_version = get_chrome_driver_version(chrome_version)

    #     #Chromeの場所を指定
    #     options = Options()
    #     options.binary_location = location

    #     #ChromeDriverのヴァージョンを指定
    #     chrome_service = Service(ChromeDriverManager(version=driver_version).install())

    #     return webdriver.Chrome(service=chrome_service,options=options)
    
    # ドライバの定義
    def set_driver():
        '''
        Chromeを自動操作するためのChromeDriverを起動してobjectを取得する
        '''
        USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
        options = ChromeOptions()

        # 起動オプションの設定
        options.add_argument(f'--user-agent={USER_AGENT}') # ブラウザの種類を特定するための文字列
        options.add_argument('log-level=3') # 不要なログを非表示にする
        options.add_argument('--ignore-certificate-errors') # 不要なログを非表示にする
        options.add_argument('--ignore-ssl-errors') # 不要なログを非表示にする
        # options.add_experimental_option('excludeSwitches', ['enable-logging']) # 不要なログを非表示にする
        options.add_argument('--incognito') # シークレットモードの設定を付与
        
        # ChromeのWebDriverオブジェクトを作成する。
        service=Service(ChromeDriverManager().install())
        return Chrome(service=service, options=options)


    driver = set_driver()
    
    def item_scraping(asin_list):
        
        item_info = []
        count = 0
        url = "https://www.amazon.co.jp/dp/{asin}"
        
        # １商品ごとにループ
        for asin in asin_list:
            driver.get(url.format(asin=asin["ASIN"]))
            count += 1
            time.sleep(3)
                
            # 検索画面上でprime判定ができなかった場合
            def listing(prime, price, d_charge, count, branch):
                time.sleep(2)
                # 新品アンド中古品リストがある場合
                try:
                    listing_box = driver.find_element(by=By.CSS_SELECTOR, value=".olp-touch-link")
                    listing_url = listing_box.get_attribute("href")
                    all_item_button = "item_list"
                # 新品アンド中古品リストがない場合
                except:
                    # 「全ての出品」がある場合
                    try:
                        listing_box = driver.find_element(by=By.CSS_SELECTOR, value="#buybox-see-all-buying-choices")
                        listing_url = listing_box.find_element(by=By.TAG_NAME, value="a").get_attribute("href")
                        all_item_button = "all_listing"
                    # 「在庫なし」などその他の場合
                    except:
                        log(f"{count}件目：fail(prime/price)>{branch}>all_item_button")
                        return prime, price, d_charge
                # リストを開いたページへ遷移
                idx = listing_url.find(asin["ASIN"])
                driver.get("https://www.amazon.co.jp/gp/offer-listing/"+asin["ASIN"]+"/"+listing_url[idx+1:])
                time.sleep(3)
                
                # 新品・primeに絞り込み
                try:
                    driver.find_element(by=By.ID, value="aod-filter-string").click()
                    time.sleep(2)
                    prime_check = driver.find_element(by=By.ID, value="primeEligible")
                    prime_check.find_element(by=By.TAG_NAME, value="i").click()
                    new_check = driver.find_element(by=By.ID, value="new")
                    new_check.find_element(by=By.TAG_NAME, value="i").click()
                    time.sleep(2)
                # 絞り込みができない場合（商品が一つしかない場合など）
                except:
                    try:
                        status = driver.find_elements(by=By.CSS_SELECTOR, value=".aod-information-block")[1].find_element(by=By.CSS_SELECTOR, value="#aod-offer-heading").text.strip()
                        shipper = driver.find_elements(by=By.CSS_SELECTOR, value=".aod-information-block")[1].find_element(by=By.CSS_SELECTOR, value="#aod-offer-shipsFrom").find_elements(by=By.CSS_SELECTOR, value="span")[1].text
                        if status=="新品" and (shipper=="Amazon" or shipper=="Amazon.co.jp"):
                            pass
                        else:
                            return prime, price, d_charge
                    except:
                        return prime, price, d_charge
                # prime、priceの取得
                try:
                    information_block = driver.find_elements(by=By.CSS_SELECTOR, value=".aod-information-block")
                    price = information_block[1].find_element(by=By.CSS_SELECTOR, value=".a-price-whole").text 
                    prime = "prime"
                    span_all = information_block[1].find_element(by=By.CSS_SELECTOR, value="#mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE").find_element(by=By.TAG_NAME, value="span")
                    span_remove = span_all.find_element(by=By.CSS_SELECTOR, value=".a-text-bold")
                    # spanタグの中から、子要素のspan（月日の情報）を除外
                    driver.execute_script('arguments[0].remove()', span_remove)
                    d_charge = span_all.text.lstrip("配送料 ¥")
                    log(f"{count}件目：success(prime/price)>{branch}>{all_item_button}")
                except:
                    log(f"{count}件目：fail(prime/price)>{branch}>{all_item_button}")
                    pass
                return prime, price, d_charge
            
            # 変数の初期化
            name = ""
            review_count = ""
            review = ""
            image_url = ""
            item_detail = ""
            d_charge = ""
            prime = ""
            price = ""
            
            # <<名前その他の情報の取得>>
            try:
                # 商品名
                name = driver.find_element(by=By.CSS_SELECTOR, value=".product-title-word-break").text
                # 画像URL
                try:
                    image_url = driver.find_element(by=By.CSS_SELECTOR, value=".itemNo0").find_element(by=By.TAG_NAME, value="img").get_attribute("src")
                except:
                    pass
                    # iamge_url_relay = driver.find_element(by=By.CSS_SELECTOR, value=".itemNo0")
                    # image_url = iamge_url_relay.find_element(by=By.CSS_SELECTOR, value=".a-dynamic-image").get_attribute("src")
                # レビュー数、レビュー
                try:
                    review_count = driver.find_element(by=By.CSS_SELECTOR, value="#reviewsMedley > div > div.a-fixed-left-grid-col.a-col-left > div.a-section.a-spacing-none.a-spacing-top-mini.cr-widget-ACR > div.a-row.a-spacing-medium.averageStarRatingNumerical > span").text.rstrip("件のグローバル評価")
                    review = driver.find_element(by=By.XPATH, value='//span[@data-hook="rating-out-of-text"]').text.replace("星5つ中の","")
                except:
                    review_count = 0
                    review = ""
                # 商品説明
                try:
                    item_detail_relay_1 = driver.find_element(by=By.ID, value="feature-bullets")
                    item_detail_relay_2s = item_detail_relay_1.find_elements(by=By.TAG_NAME, value="span")
                    for item_detail_relay_2 in item_detail_relay_2s:
                        item_detail += item_detail_relay_2.text+"\n"
                except:
                    pass
            except:
                # 商品ページがないか、エラーが起こった場合
                item_info.append({
                    "検索KW": asin["検索KW"],
                    "対象商品ページURL": asin["対象商品ページURL"],
                    "対象商品画像URL": asin["対象商品画像URL"],
                    "対象商品価格": asin["対象商品価格"],
                    "ASIN": asin["ASIN"],
                    "商品名": name,
                    "URL": url.format(asin=asin["ASIN"]),
                    "最低価格": price,
                    "prime": prime,
                    "評価件数": review_count,
                    "評価": review,
                    "画像URL": image_url,
                    "商品説明": item_detail,
                })
                log(f"{count}件目：error：商品ページがないか、エラーが起こっています。")
                continue
            
            
            # <<prime,値段の取得>>
            buy_box = driver.find_element(by=By.ID, value="buybox")
            # buy_boxで通常注文と定期注文が分かれている否かの判定
            try:
                normal_buy_box = driver.find_element(by=By.ID, value="newAccordionRow")
            except:
                normal_buy_box = "nothing"
            # buy_box内に該当情報があるか否かの判定
            try:
                buy_box_texts = driver.find_elements(by=By.CSS_SELECTOR, value=".tabular-buybox-text")
                if buy_box_texts==[]:
                    buy_box_texts = "nothing"
            except:
                buy_box_texts = "nothing"
            
            
            # buyboxに通常注文のみの場合   
            if normal_buy_box=="nothing" and buy_box_texts!="nothing":
                branch = "buy_box_no_separation"
                # 画面上で取得できる場合
                for buy_box_text in buy_box_texts:
                    # ボックス内でプライム対象商品があった場合
                    if buy_box_text.get_attribute("tabular-attribute-name") == "出荷元" and (buy_box_text.text == "Amazon" or buy_box_text.text == "Amazon.co.jp"):
                        prime = "prime"
                        # 黒字の値段
                        try:
                            price = buy_box.find_element(by=By.CSS_SELECTOR, value=".a-price-whole").text
                        # 赤字の値段
                        except:
                            price = driver.find_element(by=By.CSS_SELECTOR, value="#corePrice_feature_div > div > span.a-price.a-text-price.a-size-medium > span:nth-child(2)").text.lstrip("￥")
                        log(f"{count}件目：success(prime/price)>{branch}")
                    
                # 画面上では取得できなかった場合
                if prime == "":
                    result = listing(prime, price, d_charge, count, branch)
                    prime = result[0]
                    price = result[1]
                    d_charge = result[2]
            
            
            # buyboxに通常注文と定期注文が分かれている場合
            elif normal_buy_box!="nothing" and buy_box_texts!="nothin":
                branch = "buy_box_separation"
                spans = normal_buy_box.find_elements(by=By.TAG_NAME, value="span")
                for span in spans:
                    if span.text == "Amazon" or span.text == "Amazon.co.jp":
                        price = spans[1].text.lstrip("￥")
                        prime = "prime"
                        log(f"{count}件目：success(prime/price)>{branch}")
                if prime == "":
                    result = listing(prime, price, d_charge, count, branch)
                    prime = result[0]
                    price = result[1]
                    d_charge = result[2]
                
                
            # buyboxに何の情報もない場合
            elif normal_buy_box=="nothing" and buy_box_texts=="nothing":
                branch = "buy_box_no_informaition"
                result = listing(prime, price, d_charge, count, branch)
                prime = result[0]
                price = result[1]
                d_charge = result[2]   
            
            # その他
            else:
                pass            
            
            # リストへの格納
            item_info.append({
                "検索KW": asin["検索KW"],
                "対象商品ページURL": asin["対象商品ページURL"],
                "対象商品画像URL": asin["対象商品画像URL"],
                "対象商品価格": asin["対象商品価格"],
                "ASIN": asin["ASIN"],
                "商品名": name,
                "URL": url.format(asin=asin["ASIN"]),
                "最低価格": price,
                "prime": prime,
                "評価件数": review_count,
                "評価": review,
                "画像URL": image_url,
                "商品説明": item_detail,
            })
            
        return item_info
    
    driver.get("https://www.amazon.co.jp/")
    time.sleep(3)
    
    asin_list = []
    
    for search_name, mercari_url, mercari_image_url, mercari_price in zip(df["検索KW"], df["対象商品ページURL"], df["対象商品画像URL"], df["対象商品価格"]):
        log(f"KW:{search_name}")
        try:
            driver.find_element(by=By.ID ,value="twotabsearchtextbox").clear()
            driver.find_element(by=By.ID ,value="twotabsearchtextbox").send_keys(search_name)
            driver.find_element(by=By.ID, value="nav-search-submit-button").click()
        except:
            time.sleep(20)
            driver.find_element(by=By.ID ,value="nav-bb-search").clear()
            driver.find_element(by=By.ID ,value="nav-bb-search").send_keys(search_name)
            driver.find_element(by=By.ID, value="nav-bb-button").click()
        time.sleep(3)
        item_asin = []
        
        # 星４以上の商品に絞り込み
        try:
            driver.find_element(by=By.CSS_SELECTOR, value=".a-star-medium-4").click()
            time.sleep(2)
        except:
            try:
                driver.find_element(by=By.CSS_SELECTOR, value=".a-dropdown-container").click()
                lis = driver.find_element(by=By.CSS_SELECTOR, value=".a-popover-inner").find_elements(by=By.CSS_SELECTOR, value="li")
                for li in lis:
                    if li.text.strip() == "レビューの評価順":
                        li.click()
                        time.sleep(2)
                        break
            except:
                continue
        
        # ページごとにループ
        while True:
            # スポンサー商品を特定
            sponsors = driver.find_elements(by=By.CSS_SELECTOR, value="._bGlmZ_item_awNhH")
            sponsored_asin = []
            for sponsor in sponsors:
                sponsored_asin.append(sponsor.find_element(by=By.TAG_NAME, value="div").get_attribute("data-asin"))

            # log(f"スポンサーASIN:{len(sponsored_asin)}")

            # アイテムのASIN
            items = driver.find_elements(by=By.CSS_SELECTOR, value=".s-asin")
            for item in items:
                # プライム・指定価格以下の商品に絞り込み
                try:
                    item.find_element(by=By.CSS_SELECTOR, value=".a-icon-prime")
                    item_price = item.find_element(by=By.CSS_SELECTOR, value=".a-price-whole").text.lstrip('￥').replace(',', '')
                    if int(item_price) <= int(mercari_price) and item.get_attribute("data-asin") not in sponsored_asin:
                        item_asin.append({
                            "検索KW": search_name,
                            "対象商品ページURL": mercari_url,
                            "対象商品画像URL": mercari_image_url,
                            "対象商品価格": mercari_price,
                            "ASIN": item.get_attribute("data-asin"),
                    })
                except:
                    pass

            # log(f"アイテムASIN:{len(item_asin)}")

            # スポンサー商品を削除
            for sa in sponsored_asin:
                try:
                    while sa in item_asin:
                        item_asin.remove(sa)
                except:
                    pass
                
            # log(f"アイテムASINースポンサーASIN:{len(item_asin)}")
            
            # 商品数が足りない場合
            if len(item_asin) < int(limit):
                # 次ページを開く
                try:
                    driver.find_element(by=By.CSS_SELECTOR, value="a.s-pagination-next").click()
                    log("次ページ") # 削除
                    time.sleep(3)
                # 次ページがない場合
                except:
                    log("次ページなし") # 削除
                    log(f"検索ページ計＞＞＞＞＞{len(item_asin)}")
                    for ia in item_asin[:int(limit)]:
                        asin_list.append(ia)
                    break
            # 商品数が足りている場合
            else:
                log(f"検索ページ計＞＞＞＞＞{len(item_asin)}") # 削除
                for ia in item_asin[:int(limit)]:
                    asin_list.append(ia)
                break
    log(f"合計＞＞＞＞＞{len(asin_list)}")    
    return item_scraping(asin_list)

