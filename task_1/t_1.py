
# 検索ソース
source=["ねずこ","たんじろう","きょうじゅろう","ぎゆう","げんや","かなお","ぜんいつ"]

# 検索ツール
def search():
    word =input("鬼滅の登場人物の名前を入力してください >>> ")
    
    # 存在した場合
    if word in source:
        print(f"{word}が見つかりました")
    # 存在しなかった場合    
    else:
        print(f"{word}は見つかりませんでした。")

# 実行
if __name__ == "__main__":
    search()
    