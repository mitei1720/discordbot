import requests
import pandas as pd


TOKEN = "231bad688de8228bb3a63905d7c6964941aefe20dabe54fe1fac6f16c8acf292d417074029df57f7b39dca845f4ebe3de669254ea983ed4fa7b62cde711993fd"
url1 = "https://api.chunirec.net/2.0/music/showall.json"



params = {'token': TOKEN, 'region': 'jp2'}
response = requests.get(url1,params)

if response.status_code == 200:
    # データを加工するなどの処理を行う
    df = pd.read_json(response.text)
    df.to_csv('./jp2_songs.csv')
    
else:
    print("Error: ", response.status_code)

