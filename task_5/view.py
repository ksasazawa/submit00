import eel
import desktop
import pos_system

app_name="html"
end_point="index.html"
size=(700,600)

order = pos_system.main_0()

# CSVファイルの情報を読み込み、入力コードが登録されているものであればコードと個数をリストに格納する。
@ eel.expose
def main_1(buy_item_code, buy_item_count):
    return pos_system.main_1(order, buy_item_code, buy_item_count)

# 合計金額と合計個数を算出し、レシートとテキストエリアに表示する。
@eel.expose
def main_2():
    return pos_system.main_2(order)

# お支払いを受け付け、レシートとテキストエリアにお釣りを表示する。
@eel.expose
def main_3(payment):
    return pos_system.main_3(order, payment)
    
desktop.start(app_name,end_point,size)
#desktop.start(size=size,appName=app_name,endPoint=end_point)