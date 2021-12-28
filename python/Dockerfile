FROM python:3.10.0

ENV PYTHONUNBUFFERED 1

# /code/ フォルダを作成して移動
RUN mkdir /code/
WORKDIR /code/

# DjangoProjectディレクトリを /code/twels/ へコピーする．
COPY ./twels/ /code/twels/

# uWSGIの設定ファイルをコピー
COPY ./uwsgi/ /code/uwsgi/

# Nginxの設定ファイルをコピー
COPY ./webserver/conf.d /etc/nginx/conf.d

# パッケージのインストール
COPY ./python/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# entrypoint.shをコンテナにコピー
COPY ./entrypoint.sh /code/
