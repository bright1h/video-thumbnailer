# Build upon this image "alpine" is a lightweight distro
FROM python:3.6-alpine
FROM acleancoder/imagemagick-full
# Copy everthing from . to /app inside the 'box'
COPY . /app
WORKDIR /app

# How to run it when we start up the box?
ENTRYPOINT ["python3"]
