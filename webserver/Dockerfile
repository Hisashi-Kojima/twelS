FROM nginx:1.23.3

# staticファイルはNginxのコンテナに置く必要がある．
RUN mkdir -p /front/static/
COPY ./front/static/ /front/static
