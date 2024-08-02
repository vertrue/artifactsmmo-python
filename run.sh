#!/bin/bash
docker stop artifacts_container 2>/dev/null || true
docker rm artifacts_container 2>/dev/null || true

docker build -t artifacts .  
docker run -d --name artifacts_container artifacts