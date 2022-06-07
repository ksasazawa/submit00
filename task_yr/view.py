import eel
import desktop
import yahoo_ranking

app_name="html"
end_point="index.html"
size=(700,600)

# Javascript側から呼び出す関数
@ eel.expose
def scraping(rank_limit):
    yahoo_ranking.main(page_limit=rank_limit)
    
desktop.start(app_name,end_point,size)
#desktop.start(size=size,appName=app_name,endPoint=end_point)