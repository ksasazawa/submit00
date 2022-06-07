from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

# ログイン情報
address = "k.sasazawa@estyle-inc.jp"
password = "kennta776"

# ドライバの定義
def set_driver(hidden_chrome: bool=False):
    '''
    Chromeを自動操作するためのChromeDriverを起動してobjectを取得する
    '''
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    options = ChromeOptions()


    if hidden_chrome:
        options.add_argument('--headless')

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
def main(hidden_chrome: bool=False, option: bool=True):
    
    # selenium ver
    if option:
        driver = set_driver(hidden_chrome)
        
        # ログインページ
        driver.get("https://id.jobcan.jp/account/profile")
        driver.find_elements(by=By.CSS_SELECTOR, value=".form__input")[0].send_keys(address)
        driver.find_elements(by=By.CSS_SELECTOR, value=".form__input")[2].send_keys(password)
        driver.find_element(by=By.ID, value="login_button").click()
        
        # 勤怠ページ
        kintai_page = driver.find_element(by=By.CSS_SELECTOR, value=".jbc-app-link").get_attribute("href")
        
        # 打刻ページ
        driver.get(kintai_page)
        time.sleep(3)
        driver.find_element(by=By.CSS_SELECTOR, value=".jbc-btn-secondary").click()
        time.sleep(3)

    # beautifulsoup ver
    else:
        session = requests.session()
        
        info = {
            "authenticity_token": "A9Ov/Jy4IQ+DTqvJ110xgKVmrmTpLYR+jhJlqwxWg0vfesPWhPYant+OAcS3FuCVN8SGKHPO8W2UWc+CiSxmtg==",
            "user[email]": address,
            "user[password]": password,
        }
        
        url_login = "https://id.jobcan.jp/users/sign_in"
        try:
            response = session.post(url_login, data=info)
            soup = BeautifulSoup(response.text, 'html.parser')
            print(soup.title.string)
        except:
            print("ログインエラー")
        
        
main(option=False)