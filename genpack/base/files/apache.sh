#!/bin/sh
set -e

sed -i 's/^\(APACHE2_OPTS=.*\)\"$/\1 -D PROXY -D DAV"/' /etc/conf.d/apache2

# binary cacheからインストールした場合 pkg_postinst がスキップされ
# /etc/ssl/apache2/server.{crt,key,pem} が生成されない。
# 既に存在する場合は recursive-touch でイメージに取り込み、
# 存在しない場合は openssl で自己署名証明書を生成する。
if [ -e /etc/ssl/apache2/server.pem ]; then
    recursive-touch /etc/ssl/apache2/server.crt /etc/ssl/apache2/server.key /etc/ssl/apache2/server.pem
else
    mkdir -p /etc/ssl/apache2
    openssl req -x509 -newkey rsa:2048 -nodes -days 3650 \
        -keyout /etc/ssl/apache2/server.key \
        -out /etc/ssl/apache2/server.crt \
        -subj "/CN=localhost"
fi
