FROM python:3.4
ENV PYTHONUNBUFFERED 1
# http://login:password@ip_address:port/db/data/
ENV NEO4J_REST_URL=http://neo4j:neo4j@0.0.0.0:7474/db/data/
RUN mkdir /django
WORKDIR /django
ADD requirements.txt /django/
RUN pip install -r requirements.txt
ADD . /django/
