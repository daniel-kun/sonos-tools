FROM danielkun/sonos-tools_base-image:v1
WORKDIR /sonos-tools/api.tts/
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY *.py ./
ENTRYPOINT ["gunicorn", "--access-logfile", "-", "-b", "0.0.0.0:5000", "app:app"]

