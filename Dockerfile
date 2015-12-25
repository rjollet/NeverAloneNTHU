FROM python:3.4
ENV PYTHONUNBUFFERED 1
RUN mkdir /django
WORKDIR /django
ADD requirements.txt /django/
RUN pip install -r requirements.txt
ADD . /django/
