import os
import time
import datetime
import pandas as pd

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


# LOGファイルパス
LOG_FILE_PATH = "log/log_{datetime}.log"
log_file_path = LOG_FILE_PATH.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
# CSVファイルパス
EXP_CSV_PATH = "amazon_csv/exp_list_{datetime}.csv"

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

# メイン処理
def main():
    
    search_csv = input("ASINを取得するCSV名を指定してください。>>")
    df = pd.read_csv(os.path.join(os.getcwd(), search_csv))
    
    driver = set_driver()
    url = "https://www.amazon.co.jp/dp/{asin}"
    
    item_info = []
    count = 1
    
    for asin in df['ASIN']:
        try:     
            driver.get(url.format(asin=asin))
            name = driver.find_element(by=By.CSS_SELECTOR, value=".product-title-word-break").text
            image_url = driver.find_element(by=By.ID, value="landingImage").get_attribute("src")
            price = ""
            prime = ""
            try:
                review_count = driver.find_element(by=By.CSS_SELECTOR, value="#reviewsMedley > div > div.a-fixed-left-grid-col.a-col-left > div.a-section.a-spacing-none.a-spacing-top-mini.cr-widget-ACR > div.a-row.a-spacing-medium.averageStarRatingNumerical > span").text.rstrip("件のグローバル評価")
                review = driver.find_element(by=By.XPATH, value='//span[@data-hook="rating-out-of-text"]').text.replace("星5つ中の","")   
            except:
                review_count = 0
                review = ""
            try:
                new_item_box = driver.find_element(by=By.ID, value="newAccordionRow")
            except:
                new_item_box = ""
            
            # 公式でない場合    
            if new_item_box == "":
                a_box = driver.find_element(by=By.ID, value="addToCart")
                rows = a_box.find_elements(by=By.CSS_SELECTOR, value=".tabular-buybox-text")
                for row in rows:
                    # ボックス内でプライム対象商品があった場合
                    if row.get_attribute("tabular-attribute-name") == "出荷元" and (row.text == "Amazon" or row.text == "Amazon.co.jp"):
                        prime = "prime"
                        # 黒字の値段
                        try:
                            price = a_box.find_element(by=By.CSS_SELECTOR, value=".a-price-whole").text
                        # 赤字の値段
                        except:
                            price = driver.find_element(by=By.CSS_SELECTOR, value="#corePrice_feature_div > div > span.a-price.a-text-price.a-size-medium > span:nth-child(2)").text.lstrip("￥")
                # なかった場合は、新品＆中古品のリストまで見る。
                if prime == "":
                    try:
                        driver.find_element(by=By.CSS_SELECTOR, value="#olpLinkWidget_feature_div > div.a-section.olp-link-widget > span > a > div > div").click()
                        time.sleep(2)
                        information_block = driver.find_elements(by=By.CSS_SELECTOR, value=".aod-information-block")
                        # アイテムのリストから一つずつ情報を取得
                        for information in information_block:
                            status = information.find_element(by=By.TAG_NAME, value="h5").text
                            flg = False
                            rows = information.find_elements(by=By.CSS_SELECTOR, value=".a-fixed-left-grid-inner")
                            # アイテムの情報から１行ずつ値を取得し、出荷元の情報なら変数に格納
                            for row in rows:
                                head = row.find_elements(by=By.TAG_NAME, value="span")
                                if head[0].text=="出荷元" and (head[1].text=="Amazon" or head[1].text=="Amazon.co.jp") and status=="新品":
                                    # 最低価格
                                    price = information.find_element(by=By.CSS_SELECTOR, value=".a-price-whole").text
                                    # prime
                                    prime = "prime"
                                    flg = True
                                    break                        
                                else:
                                    continue
                            # 対象データが取得できたらアイテムリストのループから抜ける
                            if flg==True:
                                break
                    except:
                        pass                   
            # 公式販売ページの場合
            else:
                rows = new_item_box.find_elements(by=By.TAG_NAME, value="span")
                for row in rows:
                    if row.text == "Amazon" or row.text == "Amazon.co.jp":
                        price = new_item_box.find_elements(by=By.TAG_NAME, value="span")[1].text.lstrip("￥")
                        prime = "prime"
            log(f"{count}件目【成功！】：{name}")
        
        except:
            name = ""
            price = ""
            prime = ""
            review_count = ""
            review = ""
            image_url = ""
            log(f"{count}件目【失敗、、、】：{name}")
                            
        item_info.append({
            "ASIN": asin,
            "商品名": name,
            "URL": url.format(asin=asin),
            "最低価格": price,
            "prime": prime,
            "評価件数": review_count,
            "評価": review,
            "画像URL": image_url
        })
        count+=1

    # CSVファイル保存処理
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    makedir_for_filepath(EXP_CSV_PATH) 
    df = pd.DataFrame.from_dict(item_info, dtype=object)
    df.to_csv(EXP_CSV_PATH.format(datetime=now), encoding="utf-8-sig")
        
if __name__ == "__main__":        
    main()
