#!/bin/bash
# set -x

echo Stoping remote agent:
docker stop fred_agent
echo Removing remote agent:
docker rm fred_agent
