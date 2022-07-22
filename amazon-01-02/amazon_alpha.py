import os
import datetime
import pandas as pd
import scraping


# CSVファイルパス
EXP_CSV_PATH = "amazon_csv/exp_list_{datetime}.csv"

# ファイルの作成
def makedir_for_filepath(filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

# メイン処理
def main():
    
    limit = input("取得する商品数を入力してください。（半角数字）＞＞")
    address = input("メールアドレス＞＞")
    password = input("パスワード＞＞")
    df = pd.read_csv(os.path.join(os.getcwd(), "itemlist.csv"))
    item_info = scraping.main(df=df, limit=limit, address=address, password=password)
        
    # CSVファイル保存処理
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    makedir_for_filepath(EXP_CSV_PATH) 
    df = pd.DataFrame.from_dict(item_info, dtype=object)
    df.to_csv(EXP_CSV_PATH.format(datetime=now), encoding="utf-8-sig")
        
if __name__ == "__main__":        
    main()