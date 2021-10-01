#!/bin/sh
set -eu

# init canteen templates with HOST env variable
mkdir -p /app/http-root/canteens
cp -r /app/canteen-templates/. /app/http-root/canteens
find /app/http-root/canteens -type f -exec sed -i -e "s/\[HOST_PLACEHOLDER\]/${HOST}/g" {} \;

mkdir -p /app/http-root/feeds

exec busybox crond -f -l 7 -L /dev/stdout
