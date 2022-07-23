import os
import datetime
import pandas as pd
import scraping02


# CSVファイルパス
EXP_CSV_PATH = "amazon_csv/exp_list_{datetime}.csv"

# ファイルの作成
def makedir_for_filepath(filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

# メイン処理
def main():
    
    limit = input("取得する商品数を入力してください。（半角数字）＞＞")
    df = pd.read_csv(os.path.join(os.getcwd(), "itemlist.csv"))
    scraping02.main(df=df, limit=limit)
        
if __name__ == "__main__":        
    main()