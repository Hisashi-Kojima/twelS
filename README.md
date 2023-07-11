# プログラムの実行手順

## Solrの初期化

```sh
docker compose -f docker-compose.yml -f docker-compose.solr.yml up
```

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
cd web_crawler/web_crawler/spiders
python local_spider.py
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

CPU: 12th Gen Intel Core(TM) i3-12100 @ 3.30GHz (4コア)、メモリ16GB（8GB割り当て）のWindows PCで  
日本語のWikipedia  

* 数学 (7,021 pages)
* 物理学 (1,127 pages)
* 経済学 (9,378 pages、数式を含むページは200くらい)

manabitimes.jp (1,270 pages)  

* 数学
* 物理学

英語のWikipedia
* 数学 (18,310 pages)


これらのページ合わせて37,106ページ（一部無関係のファイルを含む）を  
スクレイピングをしたとき、数式を含むページ6,826ページが登録され、  
15,679秒（4時間21分19秒）かかった。  

## mysqlのバックアップ

```sh
docker exec -it mysql_container /bin/bash
cd /var/lib/mysql
mysqldump --single-transaction -u root -p twels > mysql_backup.sql
```

mysqlのバックアップのファイル名には221007_mysql_backup.sql（2022年10月7日の場合）のように先頭に日付を入れること。

## Solrのバックアップ

pythonコンテナで以下のコマンドを実行。  

```sh
curl --user Hisashi:Kojima "http://solr1:8983/solr/admin/collections?action=BACKUP&name=solrBackup&collection=twels_collection&location=backup"
```

## Solrのリストア

```sh
curl --user Hisashi:Kojima "http://solr1:8983/solr/admin/collections?action=RESTORE&name=solrBackup&collection=twels_collection&location=backup"
```

## ローカルブランチのアップデート

```sh
git pull origin REMOTE-BRANCH-NAME:LOCAL-BRANCH-NAME
```

e.g.  

```sh
git pull origin develop:develop
```

## docker composeの設定の確認

```sh
docker compose config
```

または  

```sh
docker compose -f docker-compose.yml -f docker-compose.prod.yml config
```
