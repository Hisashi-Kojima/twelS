ARG PYTHON_VERSION=3.11
ARG PYTHON_VERSION_FULL=${PYTHON_VERSION}.3
ARG UWSGI_VERSION_FULL=2.0.21

# build stage
FROM python:${PYTHON_VERSION_FULL} as build

# call "ARG" so that
# ARGs defined before the first "FROM" can be used after "FROM".
ARG UWSGI_VERSION_FULL

RUN mkdir /code/
WORKDIR /code/

# uWSGI needs a C compiler (gcc or clang).
# Python image having the C compiler installs uWSGI.
RUN pip install --upgrade pip \
    && pip install uWSGI==${UWSGI_VERSION_FULL}


# product stage
FROM python:${PYTHON_VERSION_FULL}-slim

# call "ARG" so that
# ARGs defined before the first "FROM" can be used after "FROM".
ARG PYTHON_VERSION
ARG UWSGI_VERSION_FULL

ARG PATH1=/usr/local/bin/uwsgi
ARG PATH2=/usr/local/lib/python${PYTHON_VERSION}/site-packages/uWSGI-${UWSGI_VERSION_FULL}.dist-info
ARG PATH3=/usr/local/lib/python${PYTHON_VERSION}/site-packages/uwsgidecorators.py

ENV PYTHONUNBUFFERED 1

# copy the compiled uWSGI.
COPY --from=build ${PATH1} ${PATH1}
COPY --from=build ${PATH2} ${PATH2}
COPY --from=build ${PATH3} ${PATH3}

# make code directory for twelS code.
RUN mkdir /code/
WORKDIR /code/

# frontのコピーよりも先にpip installをすることで、
# frontのコードに修正があってもpip installまではキャッシュを活用できる。
COPY ./python/requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# DjangoProjectディレクトリを /code/front/ へコピーする．
COPY ./front/ /code/front/

# uWSGIの設定ファイルをコピー
COPY ./uwsgi/ /code/uwsgi/

# Nginxの設定ファイルをコピー
COPY ./webserver/conf.d /etc/nginx/conf.d

# entrypoint.shをコンテナにコピー
COPY ./entrypoint.sh /code/
