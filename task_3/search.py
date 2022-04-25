import os
import csv
import pandas as pd
import eel

### デスクトップアプリ作成課題

def kimetsu_search(word, file_name):
    # 検索対象取得
    # 既に該当ファイルがあった場合
    if os.path.exists(f"./{file_name}"):
        df=pd.read_csv(f"./{file_name}")
        source=list(df["name"])
    # 該当ファイルがなかった場合
    else:
        with open(f"./{file_name}", "w") as f:
            writer = csv.writer(f)
            writer.writerow(['no', 'name'])
        f.close()
        df=pd.read_csv(f"./{file_name}")
        source=list(df["name"])

    # 検索
    # CSVに該当ワードがあった場合
    if word in source:
        # CSV書き込み
        df=pd.DataFrame(source,columns=["name"])
        df.to_csv(f"./{file_name}",encoding="utf_8-sig")
        print("『{}』はあります".format(word)) 
        print(source)     
        return "『{}』はあります".format(word)
    # CSVに該当ワードがなかった場合
    else:
        source.append(word)
        # CSV書き込み
        df=pd.DataFrame(source,columns=["name"])
        df.to_csv(f"./{file_name}",encoding="utf_8-sig")
        print("『{}』はありません".format(word))
        print(source)
        return "『{}』はありません".format(word)
        # 追加
        #add_flg=input("追加登録しますか？(0:しない 1:する)　＞＞　")
        #if add_flg=="1":
    

