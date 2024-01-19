-1,必要な環境変数

BOT_TOKEN         discord developper portalから持ってきてください
UNIREC_TOKEN      chunirecのトークンをはっつけてください
GUILD_ID          動かしたいdiscordのサーバのIDを突っ込んでください
MOGI_ROLE         discord鯖のロールを適当に作ってIDを突っ込んでください


+で
/cogs/mogi.py内グローバル変数に各チャンネルIDをはっつける場所があります。



0,randombot.py
bot本体
起動はpython randombot.py


1,libmemo.yaml 
conda環境一覧

2,requirements.txt
pip環境一覧

3,Dockerfile
デプロイ用(railwayにデプロイしてる)


4,DB
botのユーザデータ管理
-mogi情報管理
-楽曲情報管理
大体libs/db_util.pyがDBを弄ってる

5,cogs/
BOTコマンド群
-random.py  曲のランダムピックや楽曲のデータ管理など
-mogi.py    2v2mogiに関するコマンド、Player_役職付与,プレイヤーDB管理
-o_side.py  ゲームに関係ないコマンド
-score_attack.py  スコアタ関連

6,libs/
ユーティリティ
大体データベースを弄る関数が入ってる

