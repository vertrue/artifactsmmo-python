#!/bin/bash
sh stop.sh
git pull
sh run.sh
docker logs artifacts_container --follow