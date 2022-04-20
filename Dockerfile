FROM python:3.6-slim

WORKDIR /exporter-app

RUN pip install prometheus-client

RUN apt update

RUN apt-get install -y sysstat

COPY metrics_exporter.py ./

CMD [ "python", "-u", "./metrics_exporter.py"]
