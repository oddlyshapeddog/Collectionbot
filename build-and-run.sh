#!/bin/bash

echo 'Stopping and removing the previous instance' && \
  docker rm -f cb > /dev/null

echo 'Building and running' && \
  docker build -t oddlyshapeddog/collectionbot . && \
  docker run -d --name cb oddlyshapeddog/collectionbot && \
  docker ps -f name=cb

