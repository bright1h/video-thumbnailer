# # Build upon this image "alpine" is a lightweight distro
# FROM python:3.6-alpine
# FROM acleancoder/imagemagick-full
# # Copy everthing from . to /app inside the 'box'
# COPY . /app
# WORKDIR /app

# # How to run it when we start up the box?
# ENTRYPOINT ["python3"]


FROM ubuntu:16.04
FROM jrottenberg/ffmpeg 
RUN apt-get update && apt-get install -y \
    imagemagick \
    python3-pip
    
RUN pip3 install --upgrade pip
WORKDIR /app
ADD requirements.txt .
RUN pip3 install -r requirements.txt
COPY . /app
COPY make_thumbnail.py /bin
#ENTRYPOINT [ "python3" ]
#CMD ["./make_thumbnail.py"]
