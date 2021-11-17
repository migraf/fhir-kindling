FROM python:3.9

RUN apt-get update && apt-get install -y && pip install pipenv
COPY . /opt
WORKDIR /opt
RUN pipenv install
