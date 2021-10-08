FROM python:3.9.6

ENV PYTHONUNBUFFERED 1

# /code/ フォルダを作成して移動
RUN mkdir /code/
WORKDIR /code/

# DjangoProjectディレクトリを /code/twelS/ へコピーする．
COPY ./twelS/ /code/twelS/

# uWSGIの設定ファイルをコピー
COPY ./uwsgi/ /code/uwsgi/

# Nginxの設定ファイルをコピー
COPY ./webserver/conf.d /etc/nginx/conf.d

# パッケージのインストール
COPY ./python/requirements.txt .
RUN pip install -r requirements.txt

# entrypoint.shをコンテナにコピー
COPY ./entrypoint.sh /code/
