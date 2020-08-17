#!/bin/bash

echo 'Stopping and removing the previous instance' && \
  docker rm -f cb > /dev/null

echo 'Building and running' && \
  docker build -t oddlyshapeddog/collectionbot . && \
  docker run -dit --name cb \
    --mount type=bind,source="${PWD}/logs",target=/var/log \
    oddlyshapeddog/collectionbot && \
  docker ps -f name=cb

