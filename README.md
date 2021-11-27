# nginxの起動
twelsディレクトリ(rootディレクトリにて)にて  
docker-compose up  
"""これでdockerが起動して，nginxも起動する．"""

# test
testsディレクトリにて  

pytest -n auto  
"""pytest-xdistの'pytest -n NUMCPUS'の形で，'pytest -n auto'にするとCPUの最大数を使ってくれる．"""  

pytest -s  
"""print関数の出力が標準出力に書き出される．ただし，pytest-xdistとは共存しない．"""

pytest test_cursor.py  
"""test_cursor.pyのみをテストする．"""

# make gitignore
.gitignoreを作成したいディレクトリにて
gibo dump Python macOS VisualStudioCode >> .gitignore

# crawl
CPU: Intel Core(TM) i5-8500 @ 3.00GHz (6コア)，メモリ16GBのWindows PCで  
日本語のWikipediaの数学と物理学のページ合わせて7859ページを  
シングルプロセスのスクレイピングをしたとき，  
488526秒（5日15時間42分6秒）かかった．  
request_bytes: 2505717 (約2.4MB)  
response_bytes: 712761985 (約680MB)  

# mysqlのバックアップ  
MySQLのコンテナ内で  
mysqldump --single-transaction -u root -p twels > mysql_backup.sql  

# ローカルブランチのアップデート  
git pull origin REMOTE-BRANCH-NAME:LOCAL-BRANCH-NAME  
ex.  
git pull origin develop:develop  

# EC2内でのdocker daemonの再起動  
sudo systemctl restart docker  

# 開発用サーバの起動
docker-compose -f docker-compose.dev.yml up  

# crawl
docker-compose -f docker-compose.scrape.yml up  
他のターミナルで  
docker exec -it twels-python-1 /bin/bash  
cd twelS/wiki_crawler  
scrapy crawl local_math  


mysqldump --single-transaction -u root -p twels > mysql_backup.sql  
