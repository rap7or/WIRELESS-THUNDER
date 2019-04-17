FROM python:3.6-stretch

RUN mkdir -p /opt/src/
COPY ./requirements.txt /opt/src/requirements.txt
RUN pip3 install -r /opt/src/requirements.txt

WORKDIR /opt/src

CMD python3 -m flask run

