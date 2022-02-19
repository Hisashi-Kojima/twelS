# 本番環境の起動
`docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`

# 開発用サーバの起動
`docker compose -f docker-compose.yml -f docker-compose.dev.yml up`  

# crawl
`docker compose -f docker-compose.yml -f docker-compose.scrape.yml up`  
他のターミナルで  
`docker exec -it python_container /bin/bash`  
`cd wiki_crawler`  
`scrapy crawl local_math`  

# test
環境の起動後，testsディレクトリにて  

`pytest -n auto`  
"""pytest-xdistの'pytest -n NUMCPUS'の形で，'pytest -n auto'にするとCPUの最大数を使ってくれる．"""  

`pytest -s`  
"""print関数の出力が標準出力に書き出される．ただし，pytest-xdistとは共存しない．"""

`pytest test_cursor.py`  
"""test_cursor.pyのみをテストする．"""

# make gitignore
.gitignoreを作成したいディレクトリにて  
`gibo dump Python macOS VisualStudioCode >> .gitignore`

# crawlにかかる時間
CPU: Intel Core(TM) i5-8500 @ 3.00GHz (6コア)，メモリ16GBのWindows PCで  
日本語のWikipediaの数学と物理学のページ合わせて7859ページを  
シングルプロセスのスクレイピングをしたとき，  
509097秒（5日21時間24分57秒）かかった．  
request_bytes: 2490609 (約2.4MB)  
response_bytes: 712761985 (約680MB)  

# mysqlのバックアップ  
`docker exec -it mysql_container /bin/bash`  
`cd /var/lib/mysql`  
`mysqldump --single-transaction -u root -p twels > mysql_backup.sql`  

# ローカルブランチのアップデート  
`git pull origin REMOTE-BRANCH-NAME:LOCAL-BRANCH-NAME`  
ex.  
`git pull origin develop:develop`  

# EC2内でのdocker daemonの再起動  
`sudo systemctl restart docker`  

# docker composeの設定の確認
`docker compose config`  
または  
`docker compose -f docker-compose.yml -f docker-compose.prod.yml config`
