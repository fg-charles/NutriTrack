FROM python:slim

RUN useradd nutritrack

WORKDIR /home/nutritrack

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn pymysql cryptography

COPY app app
COPY migrations migrations
COPY nutritrack.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP nutritrack.py

RUN chown -R nutritrack:nutritrack ./
USER nutritrack

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]