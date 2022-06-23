import os
import pandas as pd
import time

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# メイン処理
def main(df):
    
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
        options.add_experimental_option('excludeSwitches', ['enable-logging']) # 不要なログを非表示にする
        options.add_argument('--incognito') # シークレットモードの設定を付与
        
        # ChromeのWebDriverオブジェクトを作成する。
        service=Service(ChromeDriverManager().install())
        return Chrome(service=service, options=options)

    item_info = []
    
    driver = set_driver()
    url = "https://www.amazon.co.jp/dp/{asin}"

    
    # １商品ごとにループ
    for asin in df['ASIN']:
        driver.get(url.format(asin=asin))
        time.sleep(3)
        
        # 検索画面上でprime判定ができなかった場合
        def listing(prime, price):
            time.sleep(2)
            # 新品アンド中古品リストがある場合
            try:
                listing_box = driver.find_element(by=By.CSS_SELECTOR, value=".olp-link-widget")
            # 新品アンド中古品リストがない場合（「全ての出品」の場合）
            except:
                # 「全ての出品」がある場合
                try:
                    listing_box = driver.find_element(by=By.CSS_SELECTOR, value="#buybox-see-all-buying-choices")
                # 「在庫なし」などその他の場合
                except:
                    return prime, price
            listing_url = listing_box.find_element(by=By.TAG_NAME, value="a").get_attribute("href")
            idx = listing_url.find(asin)
            driver.get("https://www.amazon.co.jp/gp/offer-listing/"+asin+"/"+listing_url[idx+1:])
            time.sleep(3)
            try:
                driver.find_element(by=By.ID, value="aod-filter-string").click()
                time.sleep(2)
                prime_check = driver.find_element(by=By.ID, value="primeEligible")
                prime_check.find_element(by=By.TAG_NAME, value="i").click()
                new_check = driver.find_element(by=By.ID, value="new")
                new_check.find_element(by=By.TAG_NAME, value="i").click()
                time.sleep(2)
            except:
                pass
            try:
                information_block = driver.find_elements(by=By.CSS_SELECTOR, value=".aod-information-block")
                price = information_block[1].find_element(by=By.CSS_SELECTOR, value=".a-price-whole").text 
                prime = "prime"
            except:
                pass
            return prime, price
        
        
        # <<名前その他の情報を取得>>
        # 商品名
        name = driver.find_element(by=By.CSS_SELECTOR, value=".product-title-word-break").text
        # 画像URL
        try:
            image_url = driver.find_element(by=By.ID, value="landingImage").get_attribute("src")
        except:
            iamge_url_relay = driver.find_element(by=By.CSS_SELECTOR, value=".itemNo0")
            image_url = iamge_url_relay.find_element(by=By.CSS_SELECTOR, value=".a-dynamic-image").get_attribute("src")
        # レビュー数、レビュー
        try:
            review_count = driver.find_element(by=By.CSS_SELECTOR, value="#reviewsMedley > div > div.a-fixed-left-grid-col.a-col-left > div.a-section.a-spacing-none.a-spacing-top-mini.cr-widget-ACR > div.a-row.a-spacing-medium.averageStarRatingNumerical > span").text.rstrip("件のグローバル評価")
            review = driver.find_element(by=By.XPATH, value='//span[@data-hook="rating-out-of-text"]').text.replace("星5つ中の","")   
        except:
            review_count = 0
            review = ""
        # 商品説明
        item_detail = ""
        item_detail_relay_1 = driver.find_element(by=By.ID, value="feature-bullets")
        item_detail_relay_2s = item_detail_relay_1.find_elements(by=By.TAG_NAME, value="span")
        for item_detail_relay_2 in item_detail_relay_2s:
            item_detail += item_detail_relay_2.text+"\n"
        # プライムと値段（初期化）
        prime = ""
        price = ""
        
        
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
                
            # 画面上では取得できなかった場合
            if prime == "":
                result = listing(prime, price)
                prime = result[0]
                price = result[1]
        
        
        # buyboxに通常注文と定期注文が分かれている場合
        elif normal_buy_box!="nothing" and buy_box_texts!="nothin":
            spans = normal_buy_box.find_elements(by=By.TAG_NAME, value="span")
            for span in spans:
                if span.text == "Amazon" or span.text == "Amazon.co.jp":
                    price = spans[1].text.lstrip("￥")
                    prime = "prime"
            if prime == "":
                result = listing(prime, price)
                prime = result[0]
                price = result[1]
            
            
        # buyboxに何の情報もない場合
        elif normal_buy_box=="nothing" and buy_box_texts=="nothing":
            result = listing(prime, price)
            prime = result[0]
            price = result[1]
       
        
        # その他
        else:
            pass
        
        
        # リストへの格納
        item_info.append({
            "ASIN": asin,
            "商品名": name,
            "URL": url.format(asin=asin),
            "最低価格": price,
            "prime": prime,
            "評価件数": review_count,
            "評価": review,
            "画像URL": image_url,
            "商品説明": item_detail
        })
        
    return item_info