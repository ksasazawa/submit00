import os
import time
import datetime
import pandas as pd

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


# LOGファイルパスの雛形を作成
LOG_FILE_PATH = "log/log_{datetime}.log"
# 上記パスの変数datetimeに、現在の時刻を型指定して入れ込む
log_file_path = LOG_FILE_PATH.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
# CSVファイルパスの雛形を作成
EXP_CSV_PATH = "csv/exp_list_{datetime}.csv"


# ドライバの定義
def set_driver(hidden_chrome: bool = False):
        
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
    options = ChromeOptions()

    if hidden_chrome:
        options.add_argument('--headless')

    options.add_argument(f'--user-agent={USER_AGENT}') # ブラウザの種類を特定するための文字列
    options.add_argument('log-level=3') # 不要なログを非表示にする
    options.add_argument('--ignore-certificate-errors') # 不要なログを非表示にする
    options.add_argument('--ignore-ssl-errors') # 不要なログを非表示にする
    options.add_experimental_option('excludeSwitches', ['enable-logging']) # 不要なログを非表示にする
    options.add_argument('--incognito') # シークレットモードの設定を付与
    
    # ChromeのWebDriverオブジェクトを作成する。(Selenium version4からは以下のようにServiceを使用することが推奨される)
    service=Service(ChromeDriverManager().install())
    return Chrome(service=service, options=options)


# ファイルの作成
def makedir_for_filepath(filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)


# ログとコンソールへの出力
def log(txt):
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    # %sは文字列型を指定しており、右側のlog,now.txtを受けている。
    logStr = '[%s: %s] %s' % ('log',now , txt)
    # ログ出力
    makedir_for_filepath(log_file_path)
    with open(log_file_path, 'a', encoding='utf-8_sig') as f:
        f.write(logStr + '\n')
    print(logStr)


# メイン処理
def main(is_option: bool = False, page_limit: int=5, hidden_chrome: bool=False):
    # 処理開始のログ出力
    log(f"処理開始: is_option={is_option}, page_limit={page_limit}, hidden_chrome={hidden_chrome}")
    # driverを起動
    driver = set_driver(hidden_chrome)
    
    driver.get("https://shopping.yahoo.co.jp/category/2500/34747/45855/ranking/period_weekly/?sc_i=shp_pc_ranking-cate_mdRankListPager_1-20#list")
    time.sleep(3)

    # ページ終了まで繰り返し取得
    count = 0
    success = 0
    fail = 0
    page = 1
    item_info = []
    while page <= int(page_limit):
        # 求人の要素を丸ごと取得
        item_boxes = driver.find_elements(by=By.CSS_SELECTOR, value=".isReflect")
        
        # 1ページ分繰り返し
        for item_box in item_boxes:
            # try~exceptはエラーの可能性が高い箇所に配置
            try:
                # 順位を取得
                rank = item_box.find_element(by=By.CSS_SELECTOR, value=".num").text
                # 商品タイトルを取得
                item_title = item_box.find_element(by=By.CSS_SELECTOR, value=".elTitle")
                # 商品名を取得
                name = item_title.find_element(by=By.TAG_NAME, value="a").text
                # 商品URLを取得
                item_url = item_title.find_element(by=By.TAG_NAME, value="a").get_attribute("href")
                # DataFrameにレコードを追加(辞書形式でセット)
                item_info.append(
                    {
                        "順位": rank,
                        "商品名": name,
                        "商品URL": item_url,
                    }
                )
                # 成功パターン
                success+=1
                count+=1
                log(f"[成功]{success} 件目 (page: {page}) : \n{name}\n")
            except Exception as e:
                # 失敗パターン
                fail+=1
                log(f"[失敗]{fail} 件目 (page: {page})")
                log(e)
            finally:
                # ページ最下部まで進んだらfor文が終了し、次のページへ。
                count+=1

        # 次のページボタンがあればリンクを取得して画面遷移、なければ終了
        next_pages = driver.find_element(by=By.CSS_SELECTOR, value=".elPager")
        next_page = next_pages.find_elements(by=By.TAG_NAME, value="a")
        
        if page==5:
            print("最終ページです。終了します。")
            break
        else:
            driver.get(next_page[page-1].get_attribute("href"))
            
        page += 1

    # 現在時刻を指定した文字列フォーマットとして取得（非常によく使う）
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    # csv出力（encodingはWindowsのExcelの文字化け防止のためにutf-8-sig(BOM付きUTF8)とする
    makedir_for_filepath(EXP_CSV_PATH)
    # df.appendは非推奨になったため、from_dictを使用する
    df = pd.DataFrame.from_dict(item_info, dtype=object)
    df.to_csv(EXP_CSV_PATH.format(datetime=now), encoding="utf-8-sig")
    log(f"処理完了 成功件数: {success} 件 / 失敗件数: {fail} 件")

    
# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()


              
    