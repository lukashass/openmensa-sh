FROM python:3.10.6-alpine3.16

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY cron.txt /
RUN cat /cron.txt >> /var/spool/cron/crontabs/root
