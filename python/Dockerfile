ARG PYTHON_VERSION=3.11
ARG PYTHON_VERSION_FULL=${PYTHON_VERSION}.3

# build stage
FROM python:${PYTHON_VERSION_FULL} as build

RUN mkdir /site-packages/

# uWSGI needs a C compiler (gcc or clang).
# Python image having the C compiler installs uWSGI.
COPY ./python/requirements.txt .
RUN pip install --upgrade pip \
    && pip install -t /site-packages -r requirements.txt \
    && mv /site-packages/bin /dependencies


# product stage
FROM python:${PYTHON_VERSION_FULL}-slim

# call "ARG" so that
# ARGs defined before the first "FROM" can be used after "FROM".
ARG PYTHON_VERSION

ENV PYTHONUNBUFFERED 1

COPY --from=build /dependencies /usr/local/bin
COPY --from=build /site-packages /usr/local/lib/python${PYTHON_VERSION}/site-packages

# install libxml2 for uWSGI.
# make code directory for twelS code.
RUN apt update \
    && apt install -y curl libxml2 \
    && mkdir /code/
WORKDIR /code/

# DjangoProjectディレクトリを /code/front/ へコピーする．
COPY ./python/front/ /code/front/

# uWSGIの設定ファイルをコピー
COPY ./uwsgi/ /code/uwsgi/

# Nginxの設定ファイルをコピー
COPY ./webserver/conf.d /etc/nginx/conf.d

# entrypoint.shをコンテナにコピー
COPY ./entrypoint.sh /code/
