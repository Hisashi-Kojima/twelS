FROM nginx:1.21.5

# staticファイルはNginxのコンテナに置く必要がある．
RUN mkdir -p /front/static/
COPY ./front/static/ /front/static
