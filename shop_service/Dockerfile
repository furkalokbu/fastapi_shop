FROM python:3.9
 
WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN apt-get update \
    && apt-get install gcc -y \
    && apt-get clean

RUN apt-get update
RUN apt-get install -y gdal-bin libgdal-dev

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal


RUN pip install -r /app/requirements.txt \
    && rm -rf /root/.cache/pip

RUN pip install numpy
RUN pip install gdal==$(gdal-config --version) 

ADD . /app/
