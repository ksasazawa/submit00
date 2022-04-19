import os
import datetime

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd


# LOGファイルパスの雛形を作成
LOG_FILE_PATH = "/Users/estyle-086/Desktop/Project-01/submit00/task_2/log_{datetime}.log"
# 上記パスの変数datetimeに、現在の時刻を型指定して入れ込む
log_file_path = LOG_FILE_PATH.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))



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

def makedir_for_filepath(filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
def log(txt):
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    # %sは文字列型を指定しており、右側のlog,now.txtを受けている。
    logStr = '[%s: %s] %s' % ('log',now , txt)
    # ログ出力
    makedir_for_filepath(log_file_path)
    with open(log_file_path, 'a', encoding='utf-8_sig') as f:
        f.write(logStr + '\n')
    print(logStr)


def main():
    '''
    main処理
    '''
    ### 課題４：検索キーワードの入力を受け付ける。
    search_keyword = input("検索したいキーワードを入力してください。：")
    
    driver = set_driver()
    
    
    driver.get("https://tenshoku.mynavi.jp/")
    time.sleep(5)
    
    '''
    ポップアップを閉じる
    ※余計なポップアップが操作の邪魔になる場合がある
      モーダルのようなポップアップ画面は、通常のclick操作では処理できない場合があるため
      excute_scriptで直接Javascriptを実行することで対処する
    '''
    driver.execute_script('document.querySelector(".karte-close").click()')
    time.sleep(5)
    
    driver.execute_script('document.querySelector(".karte-close").click()')


    '''
    find_elementでHTML要素(WebElement)を取得する
    byで、要素を特定する属性を指定するBy.CLASS_NAMEの他、By.NAME、By.ID、By.CSS_SELECTORなどがある
    特定した要素に対して、send_keysで入力、clickでクリック、textでデータ取得が可能
    '''
    
    driver.find_element(by=By.CLASS_NAME, value="topSearch__text").send_keys(search_keyword)
    
    driver.find_element(by=By.CLASS_NAME, value="topSearch__button").click()


    '''
    find_elements(※複数形)を使用すると複数のデータがListで取得できる
    一覧から同一条件で複数のデータを取得する場合は、こちらを使用する
    '''
    
    while True:
        
        name_elms = driver.find_elements(by=By.CLASS_NAME, value="cassetteRecruit__name")
        ### 課題２：求人名のクラスを取得
        job_elms = driver.find_elements(by=By.CLASS_NAME, value="cassetteRecruit__copy")




        
        df = pd.DataFrame()

        
        print(len(name_elms))
        '''
        name_elmsには１ページ分の情報が格納されているのでforでループさせて１つづつ取り出して、Dataframeに格納する
        '''
        for name_elm, job_elm in zip(name_elms, job_elms):
            ### 課題６：エラーが起きてもスキップする。
            try:
                log(name_elm.text)
                ### 課題２：求人名クラスからaタグのテキストを取得。
                job_elm = job_elm.find_element(by=By.TAG_NAME, value="a").get_attribute("textContent")
                log(job_elm)
                
                df = df.append(
                    {"会社名": name_elm.text, 
                        "求人名": job_elm}, 
                    ignore_index=True)
            except:
                continue
        ### 課題３：2ページ目以降の情報も取得
        try:    
            driver.get(driver.find_element(by=By.CLASS_NAME, value="iconFont--arrowLeft").get_attribute("href"))
        except:
            log("最後のページです。")
            break
    ### 課題５：csvファイルへの出力    
    df.to_csv("/Users/estyle-086/Desktop/Project-01/submit00/task_2/求人一覧.csv", encoding="utf-8_sig")    
        



if __name__ == "__main__":
    main()

    
    