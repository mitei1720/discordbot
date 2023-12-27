import requests
import pandas as pd
import os 
import settings



url1 = "https://api.chunirec.net/2.0/music/showall.json"



params = {'token': settings.UNI_TOKEN, 'region': 'jp2'}
response = requests.get(url1,params)

if response.status_code == 200:
    # データを加工するなどの処理を行う
    df = pd.read_json(response.text)
    df.to_csv('./jp2_songs.csv')
    
else:
    print("Error: ", response.status_code)

