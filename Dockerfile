FROM python:3.14.8-alpine3.24@sha256:f6a589d43c42b9e7f7dc67a12d37132491f362859a5d750607710cc56da3bc72

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY cron.txt /
RUN cat /cron.txt >> /var/spool/cron/crontabs/root
