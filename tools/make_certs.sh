#!/bin/sh

if [ -z "$1" ] || [ -z "$2" ] || [ -n "$3" ]
then
    echo "Usage: ./make_certs.sh <absolute-path-to-google-creds.json> <domain-name>"
    exit 1
fi

docker run -it --rm --name certbot -v "/etc/letsencrypt:/etc/letsencrypt" -v "/var/lib/letsencrypt:/var/lib/letsencrypt" -v "`pwd`:`pwd`" certbot/dns-google certonly --dns-google --dns-google-credentials $1 -d $2

