#!/bin/bash

VERSION='latest'

if [ $1 ]; then
    VERSION=$1
fi

echo 'Stop and Remove Container'
docker stop tracker && docker rm tracker

echo 'Build Image'
docker build -t postmon:$VERSION .

echo 'Run Container'
docker run -d --name=tracker -p 80:9876 postmon:$VERSION

echo 'Access Bash Container'
docker exec -it tracker bash
