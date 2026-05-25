# Docker image — mqtt-collector

Build context: **SensorDataCollector/** (this folder’s parent).

Image: **`becktkh/tempsensor-mqtt-collector`**

## Publish

```bash
cd SensorDataCollector
export DOCKERHUB_USER=becktkh
export DOCKER_TAG=tagname
make docker-publish-collector
```
