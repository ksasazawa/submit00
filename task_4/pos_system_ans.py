import pandas as pd
import sys
import datetime
import os

# アイテムマスタのパス
ITEM_MASTER_CSV_PATH="./item_master.csv"
# レシートフォルダの作成
RECEIPT_FOLDER="./receipt"
os.makedirs(RECEIPT_FOLDER, exist_ok=True)

### 商品クラス
class Item:
    def __init__(self,item_code,item_name,price):
        self.item_code=item_code
        self.item_name=item_name
        self.price=price
    
    def get_price(self):
        return self.price
    
### オーダークラス
class Order:
    def __init__(self,item_master):
        self.item_order_list=[]
        self.item_count_list=[]
        self.item_master=item_master
        self.set_datetime()
    
    # 現在の日時を取得（直接self.datetime=で指定してはいけないのか？）  
    def set_datetime(self):
        self.datetime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    
    # 商品コードと個数をオーダーリストに格納    
    def add_item_order(self,item_code,item_count):
        self.item_order_list.append(item_code)
        self.item_count_list.append(item_count)
    
    # オーダーリストにある商品コードを表示    
    def view_item_list(self):
        for item in self.item_order_list:
            print("商品コード:{}".format(item))
            
    # オーダー番号から商品名、値段を取得する（課題１）
    def get_item_data(self,item_code):
        for m in self.item_master:
            if item_code==m.item_code:
                return m.item_name,m.price
    
    # オーダー入力　課題２，４
    def input_order(self):
        print("いらっしゃいませ！")
        while True:
            buy_item_code=input("購入したい商品を入力してください。登録を完了する場合は、0を入力してください >>> ")
            # 登録完了でない場合の処理
            if int(buy_item_code)!=0:
                # checkにタプル型として戻り値である商品名、値段を格納
                # https://note.nkmk.me/python-function-return-multiple-values/
                check=self.get_item_data(buy_item_code)
                # 商品マスタに登録がある商品だった場合
                if check!=None:
                    print("{} が登録されました".format(check[0]))
                    buy_item_count=input("個数を入力してください　>>> ")
                    self.add_item_order(buy_item_code,buy_item_count)
                # 商品マスタに登録がない商品だった場合
                else:
                    print("「{}」は商品マスタに存在しません".format(buy_item_code))
            # 登録完了の場合の処理
            else:
                print("商品登録を終了します。")
                break    
    
    def view_order(self):
        number=1
        self.sum_price=0
        self.sum_count=0
        self.receipt_name="receipt_{}.log".format(self.datetime)
        self.write_receipt("-----------------------------------------------")
        self.write_receipt("オーダー登録された商品一覧\n")
        for item_order,item_count in zip(self.item_order_list,self.item_count_list):
            # resultにタプル型で商品名と値段を格納
            result=self.get_item_data(item_order)
            # 商品ごとに値段と個数を掛け算してsum_priceに格納
            self.sum_price+=result[1]*int(item_count)
            # 個数をカウントアップ
            self.sum_count+=int(item_count)
            # レシート番号.商品名(商品コード)：¥値段　個数　＝　小計
            receipt_data="{0}.{2}({1}) : ￥{3:,}　{4}個 = ￥{5:,}".format(number,item_order,result[0],result[1],item_count,int(result[1])*int(item_count))
            self.write_receipt(receipt_data)
            number+=1
            
        # 合計金額、個数の表示
        self.write_receipt("-----------------------------------------------")
        self.write_receipt("合計金額:￥{:,} {}個".format(self.sum_price,self.sum_count))
    
    def input_and_change_money(self):
        if len(self.item_order_list)>=1:
            while True:
                self.money=int(input("お預かり金を入力してください >>> "))
                self.change_money = self.money - self.sum_price #おつり
                if self.change_money>=0:
                    self.write_receipt("お預り金:￥{:,}".format(self.money))
                    self.write_receipt("お釣り：￥{:,}".format(self.change_money))
                    break
                else:
                    print("￥{:,}　不足しています。再度入力してください".format(self.change_money))
            
            print("お買い上げありがとうございました！")
            
    def write_receipt(self,text):
        print(text)
        with open(RECEIPT_FOLDER + "\\" + self.receipt_name,mode="a",encoding="utf-8_sig") as f:
            f.write(text+"\n") 
        
# マスタ登録(課題３)
def add_item_master_by_csv(csv_path):
    print("------- マスタ登録開始 ---------")
    item_master=[]
    count=0
    try:
        item_master_df=pd.read_csv(csv_path,dtype={"item_code":object}) # CSVでは先頭の0が削除されるためこれを保持するための設定
        for item_code,item_name,price in zip(list(item_master_df["item_code"]),list(item_master_df["item_name"]),list(item_master_df["price"])):
            item_master.append(Item(item_code,item_name,price))
            print("{}({})".format(item_name,item_code))
            count+=1
        print("{}品の登録を完了しました。".format(count))
        print("------- マスタ登録完了 ---------")
        return item_master
    except:
        print("マスタ登録が失敗しました")
        print("------- マスタ登録完了 ---------")
        sys.exit()
        

### メイン処理
def main():
    # マスタ登録(課題３)
    item_master=add_item_master_by_csv(ITEM_MASTER_CSV_PATH) # CSVからマスタへ登録
    order=Order(item_master) #マスタをオーダーに登録
    
    # オーダー入力(課題２)
    order.input_order()
    
    # オーダー番号から商品情報を取得する（課題１、６）
    order.view_order()
    order.input_and_change_money()
        
if __name__ == "__main__":
    main()        # 合計金額、個数の表示
 