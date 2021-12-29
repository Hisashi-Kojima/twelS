FROM nginx:1.21.3

# staticファイルはNginxのコンテナに置く必要がある．
RUN mkdir -p /twels/static/
COPY ./twels/static/ /twels/static
