FROM ubuntu:18.04
RUN apt-get update -y && apt-get install -y \
    imagemagick \
    python3-pip

#FROM python:3.7-alpine

# Copy requirements.txt
COPY ./requirements.txt /app/requirements.txt

# Install all the requirements
RUN pip3 install -r /app/requirements.txt

# Copy everthing from . to /app inside the 'box'
COPY . /app
WORKDIR /app


# How to run it when we start up the box?
ENTRYPOINT ["python3"]
CMD ["make_thumbnail"]

#FROM ubuntu:16.04
#FROM jrottenberg/ffmpeg
#RUN apt-get update && apt-get install -y \
#    imagemagick \
#    python-pip

#RUN pip3 install --upgrade pip
#WORKDIR /app
#ADD requirements.txt .
#RUN pip3 install -r requirements.txt
#COPY . /app
#COPY make_thumbnail /bin
#CMD ["./make_thumbnail"]


