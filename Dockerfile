FROM python:3.14.7-alpine3.24@sha256:05b2b8b732ecd268fee8727a369f936f022d1321b59befd13c30ede22769dcdc

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY cron.txt /
RUN cat /cron.txt >> /var/spool/cron/crontabs/root
