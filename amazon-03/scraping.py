import os
import time
import datetime
import math
from concurrent.futures import ThreadPoolExecutor
import re
import platform

import requests
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
        
    driver = set_driver()   
    driver.get("https://www.amazon.co.jp/")
    time.sleep(3)
    
    item_info = []
        
    for search_name in df["検索KW"]:
        log(f"KW:{search_name}")
        page_cnt = 0
        item_cnt = 0
        
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
    
        # ページごと
        while True:
            page_cnt += 1
            items = driver.find_elements(by=By.CSS_SELECTOR, value=".s-asin")
            
            for item in items:
                item_cnt += 1
                try:
                    asin = item.get_attribute("data-asin")
                    url = f"https://www.amazon.co.jp/dp/{asin}"
                except:
                    asin = ""
                    url = ""
                    log(f"【failure】ASIN:{page_cnt}ページ目：{item_cnt}商品目")
                try:
                    price = item.find_element(by=By.CSS_SELECTOR, value=".a-price-whole").text
                except:
                    price = ""
                    log(f"【failure】PRICE:{page_cnt}ページ目：{item_cnt}商品目")
                try:
                    name = item.find_element(by=By.CSS_SELECTOR, value="h2").find_element(by=By.CSS_SELECTOR, value="a").find_element(by=By.CSS_SELECTOR, value="span").text
                except:
                    name = ""
                    log(f"【failure】NAME:{page_cnt}ページ目：{item_cnt}商品目")
                if asin != "" and price != "":
                    log(f"【success】:{page_cnt}ページ目：{item_cnt}商品目")
                # リストへの格納
                item_info.append({
                    "page_No.": page_cnt,
                    "item_No.": item_cnt,
                    "ASIN": asin,
                    "商品名": name,
                    "値段": price,
                    "URL": url
                })
            try:
                driver.find_element(by=By.CSS_SELECTOR, value="a.s-pagination-next").click()
                time.sleep(3)
            except:
                break
            
    return item_info

