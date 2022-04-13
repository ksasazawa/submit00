name1="ねずこ"

while True:
    name2=input("名前を入力してください")
    
    if name2=="ぜんいつ":
        print(f"「{name1}」と「{name2}」は仲間です。")
        break
        
    elif name2=="むざん":
        print(f"「{name1}」と「{name2}」は仲間ではありません。")
        break
    
    else:
        print("入力し直してください。")