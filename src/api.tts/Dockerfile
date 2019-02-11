FROM python:3.7-slim
WORKDIR /sonos-tools/api.tts/
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY *.py ./
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

