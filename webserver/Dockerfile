FROM nginx:1.25.1

# staticファイルはNginxのコンテナに置く必要がある．
RUN mkdir -p /front/static/
COPY ./python/front/static/ /front/static
