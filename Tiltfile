k8s_yaml(local('./deploy_local.sh'))

docker_build(
	'danielkun/sonos-tools-local_frontend',
	'src/frontend',
	live_update=[
		fall_back_on(['src/frontend/js/package.json', 'src/frontend/js/package-lock.json']),
		sync('src/frontend/js', '/sonos-tools/frontend/js'),
		run('cd /sonos-tools/frontend/js && npm run build')
	]
)
docker_build('danielkun/sonos-tools-local_api.tts', 'src/api.tts')

k8s_resource('ingress', port_forwards='8443:443')


