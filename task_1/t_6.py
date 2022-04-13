name=["たんじろう","ぎゆう","ねずこ","むざん"]
name.append("ぜんいつ")

def serach_char(char):
    if char in name:
        print(f"{char}は存在します。")
    else:
        print(f"{char}は存在しません。")
        
name1 = input("名前を入力してください：")

serach_char(name1)