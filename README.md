# プログラムの実行手順

## 本番環境の起動

```sh
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 開発用サーバの起動

Djangoのsettings.pyのDebugをTrueにする。

```sh
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## crawl

```sh
docker compose -f docker-compose.yml -f docker-compose.scrape.yml up
```

他のターミナルでPythonコンテナに入り、crawlする。

```sh
docker exec -it python_container /bin/bash
cd web_crawler
scrapy crawl local
```

## test

テスト用データベースが用意されている開発用Docker-composeを実行（バックグラウンドで実行したい場合は-dオプションを付ける）

```sh
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

他のターミナルでPythonコンテナに入る。

```sh
docker exec -it python_container /bin/bash
cd tests
```

testsディレクトリにて  

```sh
pytest -n auto
```

pytest-xdistの'pytest -n NUMCPUS'の形で、'pytest -n auto'にするとCPUの最大数を使ってくれる。

```sh
pytest -s
```

print関数の出力が標準出力に書き出される。ただし、pytest-xdistとは共存しない。

```sh
pytest test_cursor.py
```

test_cursor.pyのみをテストする。

## note

### crawlにかかる時間

CPU: Intel Core(TM) i5-8500 @ 3.00GHz (6コア)、メモリ16GBのWindows PCで  
日本語のWikipediaの数学と物理学のページ合わせて8,147ページを  
シングルプロセスのスクレイピングをしたとき、  
19,852秒（5時間30分52秒）かかった。  
request_bytes: 2,571,985 (約2.5MB)  
response_bytes: 849,254,335 (約850MB)  

## mysqlのバックアップ

```sh
docker exec -it mysql_container /bin/bash
cd /var/lib/mysql
mysqldump --single-transaction -u root -p twels > mysql_backup.sql
```

mysqlのバックアップのファイル名には221007_mysql_backup.sql（2022年10月7日の場合）のように先頭に日付を入れること。

## ローカルブランチのアップデート

```sh
git pull origin REMOTE-BRANCH-NAME:LOCAL-BRANCH-NAME
```

ex.  

```sh
git pull origin develop:develop
```

## EC2内でのdocker daemonの再起動

```sh
sudo systemctl restart docker
```

## docker composeの設定の確認

```sh
docker compose config
```

または  

```sh
docker compose -f docker-compose.yml -f docker-compose.prod.yml config
```
