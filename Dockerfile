FROM python:3.15.2-alpine3.24@sha256:1656b7eaf309cadf99069ea9de335c7f67a8355789cfc6f1835a05818996f081

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY cron.txt /
RUN cat /cron.txt >> /var/spool/cron/crontabs/root
