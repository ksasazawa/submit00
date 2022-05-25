import os
import time
import datetime
import pandas as pd

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


# LOGファイルパス
# LOG_FILE_PATH = "log/log_{datetime}.log"
# log_file_path = LOG_FILE_PATH.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
# CSVファイルパス
EXP_CSV_PATH = "amazon_csv/exp_list_{datetime}.csv"

# ファイルの作成
def makedir_for_filepath(filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

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
    
    item_info = []
    # selenium ver
    driver = set_driver()
    url = "https://www.amazon.co.jp/dp/{asin}"
    
    df = pd.read_csv("test.csv")
    for asin in df['ASIN']:
        driver.get(url.format(asin=asin))
        name = driver.find_element(by=By.CSS_SELECTOR, value=".product-title-word-break").text
        # price = driver.find_element(by=By.ID, value="snsDetailPagePrice")
        # price = driver.find_element(by=By.ID, value="sns-base-price").text
        # price = driver.find_element_by_id("sns-base-price")
        item_info.append({
            "ASIN": asin,
            "商品名": name,
            "URL": url.format(asin=asin),
            # "値段": price,         
        })

    # CSVファイル保存処理
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    makedir_for_filepath(EXP_CSV_PATH) 
    df = pd.DataFrame.from_dict(item_info, dtype=object)
    df.to_csv(EXP_CSV_PATH.format(datetime=now), encoding="utf-8-sig")
        
if __name__ == "__main__":        
    main()