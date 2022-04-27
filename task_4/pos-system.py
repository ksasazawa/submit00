import pandas as pd
import datetime
import os

# LOGファイルパスの雛形を作成
LOG_FILE_PATH = "./receipt_{datetime}.log"
# 上記パスの変数datetimeに、現在の時刻を型指定して入れ込む
log_file_path = LOG_FILE_PATH.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))

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
        self.item_order_list={}
        self.item_master=item_master
    
    # オーダーリスト（辞書）に商品コード、個数を格納
    def add_item_order(self,item_code,order_cnt):
        # すでに登録されている商品コードなら個数を追加する
        if item_code in self.item_order_list:
            self.item_order_list[item_code] += order_cnt
        # なければ個数を入れる
        else:
            self.item_order_list[item_code] = order_cnt
    
    # 商品コード、商品名、値段、小計、合計個数、合計金額をターミナルおよびログファイルへ出力    
    def view_item_list(self):
        item_cnt = 0
        price_sum = 0
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        for item, item_order_cnt in zip(self.item_order_list.keys(), self.item_order_list.values()):
            for i_m in self.item_master:
                if item == i_m.item_code:
                    with open(log_file_path, 'a', encoding='utf-8_sig') as f:
                        f.write(f"商品コード：{item}"+'\n')
                        f.write(f"商品名：{i_m.item_name}"+'\n')
                        f.write(f"値段{i_m.price}"+'\n')
                        f.write(f"小計：{i_m.price * item_order_cnt}"+'\n')
                    print("商品コード:{}".format(item))
                    print("商品名：{}".format(i_m.item_name))
                    print("値段：{}".format(i_m.price))
                    print("小計：{}".format(i_m.price * item_order_cnt))
                    item_cnt += item_order_cnt
                    price_sum += i_m.price * item_order_cnt
        
        with open(log_file_path, 'a', encoding='utf-8_sig') as f:
            f.write(f"オーダー個数合計：{item_cnt}"+'\n')
            f.write(f"オーダー金額合計：{price_sum}"+'\n')
        print("オーダー個数合計：{}".format(item_cnt))
        print("オーダー金額合計：{}".format(price_sum))
        
        # お預かりとお釣りのお渡し
        while True:  
            shiharai = int(input("お預かり金額："))
            if shiharai < price_sum:
                print("金額が足りません")
            else:
                with open(log_file_path, 'a', encoding='utf-8_sig') as f:
                    f.write(f"お預かり金額：{shiharai}"+'\n')
                    f.write(f"お釣り：{shiharai-price_sum}"+'\n')
                break
                    
        print("お釣りは{}円です。".format(shiharai-price_sum))
        
    
    
### メイン処理
def main():
    # マスタ登録（リストにクラスを格納）
    df = pd.read_csv("./product_master.csv", dtype={'商品コード': object})
    item_master=[]
    for num in range(len(df)):
        item_master.append(Item(df.iloc[num,0],df.iloc[num,1],df.iloc[num,2]))
    
    # オーダー登録（オーダークラスにアイテムマスタを読み込ませ、オーダーされたもののコードのみオーダーリストに追加する。
    order=Order(item_master)
    while True:
        order_no = input("商品コードを入力してください。完了の場合は0を入力してください。：")
        if order_no == "0":
            break
        order_cnt = int(input("個数を入力してください。："))
        order.add_item_order(order_no,order_cnt)

    
    # # オーダー表示
    order.view_item_list()
    
    
    
    
if __name__ == "__main__":
    main()