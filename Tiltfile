k8s_yaml(local('./deploy_local.sh'))

docker_build('danielkun/sonos-tools-local_frontend', 'src/frontend')
docker_build('danielkun/sonos-tools-local_api.tts', 'src/api.tts')

k8s_resource('ingress', port_forwards='8443:443')


