import os
import time
import datetime

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
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
        # options.add_experimental_option('excludeSwitches', ['enable-logging']) # 不要なログを非表示にする
        options.add_argument('--incognito') # シークレットモードの設定を付与
        
        # ChromeのWebDriverオブジェクトを作成する。
        service=Service(ChromeDriverManager().install())
        return Chrome(service=service, options=options)

    item_info = []
    count = 0
    
    driver = set_driver()
    url = "https://www.amazon.co.jp/dp/{asin}"
        
    # １商品ごとにループ
    for asin in df['ASIN']:
        driver.get(url.format(asin=asin))
        count += 1
        time.sleep(3)
            
        # 検索画面上でprime判定ができなかった場合
        def listing(prime, price, count, branch):
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
                    log(f"{count}件目：{asin}：fail(prime/price)>{branch}>all_item_button")
                    return prime, price
            # リストを開いたページへ遷移
            idx = listing_url.find(asin)
            driver.get("https://www.amazon.co.jp/gp/offer-listing/"+asin+"/"+listing_url[idx+1:])
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
                        return prime, price
                except:
                    return prime, price
            # prime、priceの取得
            try:
                information_block = driver.find_elements(by=By.CSS_SELECTOR, value=".aod-information-block")
                price = information_block[1].find_element(by=By.CSS_SELECTOR, value=".a-price-whole").text 
                prime = "prime"
                span_all = information_block[1].find_element(by=By.CSS_SELECTOR, value="#mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE").find_element(by=By.TAG_NAME, value="span")
                span_remove = span_all.find_element(by=By.CSS_SELECTOR, value=".a-text-bold")
                # spanタグの中から、子要素のspan（月日の情報）を除外
                driver.execute_script('arguments[0].remove()', span_remove)
                log(f"{count}件目：{asin}：success(prime/price)>{branch}>{all_item_button}")
            except:
                log(f"{count}件目：{asin}：fail(prime/price)>{branch}>{all_item_button}")
                pass
            return prime, price
        
        def get_size(size):
            try:
                regist_infos = driver.find_element(by=By.CSS_SELECTOR, value="#detailBullets_feature_div").find_elements(by=By.TAG_NAME, value="li")
                for regist_info in regist_infos:
                    if "梱包サイズ" in regist_info.find_elements(by=By.CSS_SELECTOR, value="span > span")[0].text:
                        size = regist_info.find_elements(by=By.CSS_SELECTOR, value="span > span")[1].text
            except:
                detail_infos = driver.find_element(by=By.CSS_SELECTOR, value="#productDetails_techSpec_section_1").find_elements(by=By.TAG_NAME, value="tr")
                for detail_info in detail_infos:
                    if "梱包サイズ" in detail_info.find_element(by=By.TAG_NAME, value="th").text:
                        size = detail_info.find_element(by=By.TAG_NAME, value="td").text
            return size
        
        # 変数の初期化
        name = ""
        review_count = ""
        review = ""
        image_url = ""
        item_detail = ""
        size = ""
        prime = ""
        price = ""
        
        # <<名前その他の情報の取得>>
        try:
            # 商品名
            name = driver.find_element(by=By.CSS_SELECTOR, value=".product-title-word-break").text
            # 画像URL
            try:
                image_url = driver.find_element(by=By.CSS_SELECTOR, value=".itemNo0").find_element(by=By.TAG_NAME, value="img").get_attribute("src")
                # image_url = driver.find_element(by=By.ID, value="landingImage").get_attribute("src")
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
            # 梱包サイズ
            try:
                size = get_size(size)
            except:
                pass
        except:
            # 商品ページがないか、エラーが起こった場合
            item_info.append({
                "ASIN": asin,
                "商品名": name,
                "URL": url.format(asin=asin),
                "最低価格": price,
                "prime": prime,
                "評価件数": review_count,
                "評価": review,
                "画像URL": image_url,
                "商品説明": item_detail,
                "梱包サイズ": size
            })
            log(f"{count}件目：{asin}：error：商品ページがないか、エラーが起こっています。")
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
                    log(f"{count}件目：{asin}：success(prime/price)>{branch}")
                
            # 画面上では取得できなかった場合
            if prime == "":
                result = listing(prime, price, count, branch)
                prime = result[0]
                price = result[1]
        
        
        # buyboxに通常注文と定期注文が分かれている場合
        elif normal_buy_box!="nothing" and buy_box_texts!="nothin":
            branch = "buy_box_separation"
            spans = normal_buy_box.find_elements(by=By.TAG_NAME, value="span")
            for span in spans:
                if span.text == "Amazon" or span.text == "Amazon.co.jp":
                    price = spans[1].text.lstrip("￥")
                    prime = "prime"
                    log(f"{count}件目：{asin}：success(prime/price)>{branch}")
            if prime == "":
                result = listing(prime, price, count, branch)
                prime = result[0]
                price = result[1]
            
            
        # buyboxに何の情報もない場合
        elif normal_buy_box=="nothing" and buy_box_texts=="nothing":
            branch = "buy_box_no_informaition"
            result = listing(prime, price, count, branch)
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
            "商品説明": item_detail,
            "梱包サイズ": size
        })
        
    return item_info