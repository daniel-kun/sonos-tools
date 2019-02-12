FROM danielkun/sonos-tools_base-image:v1
WORKDIR /sonos-tools/frontend
COPY requirements.txt .
COPY static ./static/
COPY templates ./templates/
COPY js ./js/
WORKDIR /sonos-tools/frontend/js
RUN npm install && npm run build
WORKDIR /sonos-tools/frontend
RUN pip3 install -r requirements.txt
COPY *.py ./
ENTRYPOINT ["gunicorn", "--access-logfile", "-", "-b", "0.0.0.0:5001", "app:app"]

