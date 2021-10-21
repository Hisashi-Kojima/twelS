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
51236秒（約14時間10分）かかった
追加の物理学は7883秒（約2時間11分）かかった

# mysqlのバックアップ  
mysqldump --single-transaction -u hisashi -p twels > mysql_backup.sql  

# ローカルブランチのアップデート  
git pull origin REMOTE-BRANCH-NAME:LOCAL-BRANCH-NAME  
ex.  
git pull origin develop:develop  

# EC2内でのdocker daemonの再起動  
sudo systemctl restart docker  
