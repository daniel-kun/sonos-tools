FROM python:3.7-slim
WORKDIR /sonos-tools/frontend
COPY requirements.txt .
COPY static ./static/
COPY templates ./templates/
COPY js ./js/
RUN apt-get update
RUN apt install -y curl gnupg
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt install -y nodejs
WORKDIR /sonos-tools/frontend/js
RUN npm install && npm run build
WORKDIR /sonos-tools/frontend
RUN pip3 install -r requirements.txt
COPY *.py ./
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5001", "app:app"]

