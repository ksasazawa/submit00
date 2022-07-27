import os
import datetime
import pandas as pd
import scraping


# CSVファイルパス
EXP_CSV_PATH = "amazon_csv/exp_list_{kw}_{datetime}.csv"

# ファイルの作成
def makedir_for_filepath(filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

# メイン処理
def main():
    
    df = pd.read_csv(os.path.join(os.getcwd(), "kw_list.csv"))
    result = scraping.main(df=df)
        
    # CSVファイル保存処理
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    makedir_for_filepath(EXP_CSV_PATH)
    for kw, item_info in zip(result[0], result[1]):
        df = pd.DataFrame.from_dict(item_info, dtype=object)
        df.to_csv(EXP_CSV_PATH.format(kw=kw, datetime=now), encoding="utf-8-sig")
        
if __name__ == "__main__":      
    main()