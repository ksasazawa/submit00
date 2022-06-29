import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/estyle-086/Downloads/gcp-credentials.json', scope)
gc = gspread.authorize(credentials)
wks = gc.open('test_gspread').worksheet('シート2')
# wks = gc.open('test_gspread').sheet1

elements = ["たこ焼き","寿司","焼肉","おにぎり"]

for index, e in enumerate(elements, 1):
    wks.update_acell('A'+str(index) , e)