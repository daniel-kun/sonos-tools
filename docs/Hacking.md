# Hacking sonos-tools

To run your own (either production or development) instance of sonos-tools, you need the following prerequisites:

- A Kubernetes cluster and kubectl pointing to it (I can recommend https://www.hetzner.com/cloud, it's pretty convenient and very cheap)
- A Google Cloud account with the following activated APIs and corresponding credentials:
-- OAuth
-- Cloud Text-to-Speech API
- A Sonos developer account (see https://developer.sonos.com)
- A mongodb instance (I use https://cloud.mongodb.com)

For production use, you will also need:
- A domain pointing to an ingress of your Kubernetes cluster
- TLS certificates for HTTPS for that domain

# Helm variables

Set these variables when doing `helm install` using `--set`.

- Env (DEVELOPMENT, anything else)
- ClusterPublicIP
- ClusterPublicRoot
- DockerRepo
- DockerImagePrefix
- TlsCert
- TlsKey
- FlaskSecret
- GcpApiKey
- GoogleAuthClientId
- MongoDBConnectUri
- RedirectRoot
- SonosApiEndpoint
- SonosApiEndpointWS
- SonosApiAppKey
- SonosApiAppSecret

