FROM danielkun/sonos-tools_base-image:v1
WORKDIR /sonos-tools/frontend/js
COPY js/package.json .
RUN npm install
WORKDIR /sonos-tools/frontend
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY static ./static/
COPY templates ./templates/
COPY js ./js/
COPY *.py ./
WORKDIR /sonos-tools/frontend/js
RUN npm run build
WORKDIR /sonos-tools/frontend/
ENTRYPOINT ["gunicorn", "--access-logfile", "-", "-b", "0.0.0.0:5001", "app:app"]

