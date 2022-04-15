import csv
import itertools

# 検索ツール
def search():
    word =input("鬼滅の登場人物の名前を入力してください >>> ")
    
    # CSVを読み込み、sourceリストに格納
    with open('submit00/task_1/kimetsu02 - シート1.csv') as f:
        reader = csv.reader(f)
        source = [row for row in reader]
        source = list(itertools.chain.from_iterable(source))
    
    # 見つかった場合    
    if word in source:
        print(f"{word}が見つかりました")
    
    # 見つからなかった場合    
    else:
        # 追記
        with open('submit00/task_1/kimetsu02 - シート1.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([word])
        
        # 再読み込み    
        with open('submit00/task_1/kimetsu02 - シート1.csv') as f:
            reader = csv.reader(f)
            source = [row for row in reader]
            source = list(itertools.chain.from_iterable(source))  
            
        print("見つからなかったため、追加しました。")
        print(source)

# 実行
if __name__ == "__main__":
    search()
    

