
# 検索ソース
source=["ねずこ","たんじろう","きょうじゅろう","ぎゆう","げんや","かなお","ぜんいつ"]


# 検索ツール
def search():
    word =input("鬼滅の登場人物の名前を入力してください >>> ")
    
    # 見つかった場合
    if word in source:
        print(f"{word}が見つかりました")
    
    # 見つからなかった場合    
    else:
        # このファイルを読み込み
        with open('submit00/task_1/t_2.py') as f:
            l = f.readlines()
        
        # 上記で読み込んだ配列lの四行目で、sourceリストにwordを追加    
        l.insert(3, f'source.append("{word}")\n')
        
        # 上記の配列lの内容でこのファイルを上書き
        with open('submit00/task_1/t_2.py', mode='w') as f:
            f.writelines(l)             
        
        print(f"現在のキャラクターリストは{source}です。")  
        print("存在しなかったため、追加しました。")

# 実行
if __name__ == "__main__":
    search()
    