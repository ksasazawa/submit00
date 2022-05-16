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
EXP_CSV_PATH = "csv/exp_list_{search_keyword}_{datetime}.csv"


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


# テーブルから初年度年収を探して返す
def find_table_col_by_header_name(th_elms, td_elms, target:str):
    # 各求人のテーブルからthとtdを取得してforで回す
    for th_elm,td_elm in zip(th_elms,td_elms):
        # テーブルのthが初年度年収ならtdを返す
        if th_elm.text == target:
            return td_elm.text


# メイン処理
def main(is_option: bool = False, page_limit: int=5, hidden_chrome: bool=False):
    # 処理開始のログ出力
    log(f"処理開始: is_option={is_option}, page_limit={page_limit}, hidden_chrome={hidden_chrome}")
    # 検索キーワードの受付
    search_keyword=input("検索キーワードを入力してください：")
    #検索キーワードのログ出力
    log("検索キーワード:{}".format(search_keyword))
    # driverを起動
    driver = set_driver(hidden_chrome)
    
    # Webサイトを開く
    if is_option:
        # URLで直接遷移するパターン
        driver.get(f"https://tenshoku.mynavi.jp/list/kw{search_keyword}/?jobsearchType=14&searchType=18")
        time.sleep(1)
    else:
        driver.get("https://tenshoku.mynavi.jp/")
        time.sleep(1)
        try:
            # ポップアップを閉じる（seleniumだけではクローズできない）
            driver.execute_script('document.querySelector(".karte-close").click()')
            time.sleep(5)
            # ポップアップを閉じる
            driver.execute_script('document.querySelector(".karte-close").click()')
        except:
            print("エラー")
            pass

        # 検索窓に入力
        # Selenium version4からfind_element_by_*のメソッドは非推奨となったため、以下の通りfind_elementを使用
        driver.find_element(by=By.CLASS_NAME, value="topSearch__text").send_keys(search_keyword)
        # 検索ボタンクリック
        driver.find_element(by=By.CLASS_NAME, value="topSearch__button").click()

    # ページ終了まで繰り返し取得
    count = 0
    success = 0
    fail = 0
    page = 1
    recruits = []
    while page <= page_limit:
        # 求人の要素を丸ごと取得
        recruit_elms = driver.find_elements(by=By.CSS_SELECTOR, value=".cassetteRecruit")
        
        # 1ページ分繰り返し
        for recruit_elm in recruit_elms:
            # try~exceptはエラーの可能性が高い箇所に配置
            try:
                # 会社名
                name = recruit_elm.find_element(by=By.CSS_SELECTOR, value=".cassetteRecruit__name").text
                # 求人名
                copy = recruit_elm.find_element(by=By.CSS_SELECTOR, value=".cassetteRecruit__copy").text
                # 雇用形態
                employment_status = recruit_elm.find_element(by=By.CSS_SELECTOR, value=".labelEmploymentStatus").text
                # テーブルを取得。
                # table_elm = recruit_elm.find_element(by=By.CSS_SELECTOR, value=".tableCondition")でもOK
                table_elm = recruit_elm.find_element(by=By.CSS_SELECTOR, value="table")
                # 上記で取得したテーブルのthとtd、"初年度年収"を関数に組み込み、thが初年度年収ならそのtdを変数に格納する。
                first_year_fee = find_table_col_by_header_name(table_elm.find_elements(by=By.TAG_NAME, value="th"), table_elm.find_elements(by=By.TAG_NAME, value="td"), "初年度年収")
                # DataFrameにレコードを追加(辞書形式でセット)
                recruits.append(
                    {
                        "企業名": name,
                        "キャッチコピー": copy,
                        "ステータス": employment_status,
                        "初年度年収": first_year_fee
                    }
                )
                # 成功パターン
                success+=1
                log(f"[成功]{count} 件目 (page: {page}) : {name}")
            except Exception as e:
                # 失敗パターン
                fail+=1
                log(f"[失敗]{count} 件目 (page: {page})")
                log(e)
            finally:
                # ページ最下部まで進んだらfor文が終了し、次のページへ。
                count+=1

        # 次のページボタンがあればリンクを取得して画面遷移、なければ終了
        next_page = driver.find_elements(by=By.CLASS_NAME, value="iconFont--arrowLeft")
        # next_pageにdriverで取得した要素が入っていれば（次ページがあれば）実行する。
        if next_page:
            next_page_link = next_page[0].get_attribute("href")
            driver.get(next_page_link)
        else:
            log("最終ページです。終了します。")
            break
        
        page += 1

    # 現在時刻を指定した文字列フォーマットとして取得（非常によく使う）
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    # csv出力（encodingはWindowsのExcelの文字化け防止のためにutf-8-sig(BOM付きUTF8)とする
    makedir_for_filepath(EXP_CSV_PATH)
    # df.appendは非推奨になったため、from_dictを使用する
    df = pd.DataFrame.from_dict(recruits, dtype=object)
    df.to_csv(EXP_CSV_PATH.format(search_keyword=search_keyword, datetime=now), encoding="utf-8-sig")
    log(f"処理完了 成功件数: {success} 件 / 失敗件数: {fail} 件")

    
# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()


              
    