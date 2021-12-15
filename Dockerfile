FROM python:3-slim-bullseye

RUN apt-get update
RUN apt-get install -y git

ADD requirements.txt .

RUN pip3 install -r requirements.txt

WORKDIR /talus

ADD addtorepo.sh .
ADD talus.py .
ADD wsgi.py .

RUN git clone https://github.com/PrebuiltMPR/builder.git

EXPOSE 8080

CMD uvicorn talus:app --reload --host 0.0.0.0 --port 8080
