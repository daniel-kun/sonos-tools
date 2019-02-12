FROM python:3.7-slim
RUN apt-get update
RUN apt install -y curl gnupg
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt install -y nodejs
WORKDIR /sonos-tools/base_image
COPY requirements.txt .
RUN pip3 install -r requirements.txt

