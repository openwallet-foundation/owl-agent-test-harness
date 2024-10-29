#!/bin/bash
# set -x

echo Stopping remote agent:
docker stop fred_agent
echo Removing remote agent:
docker rm fred_agent
