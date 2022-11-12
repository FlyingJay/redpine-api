 FROM python:3.6.1
 ENV PYTHONUNBUFFERED 1
 RUN mkdir /code
 WORKDIR /code
 RUN apt-get update -qy
 RUN apt-get install -y libgdal-dev libzbar-dev libzbar0
 ADD requirements.txt /code/
 RUN pip install -r requirements.txt
 ADD . /code/
