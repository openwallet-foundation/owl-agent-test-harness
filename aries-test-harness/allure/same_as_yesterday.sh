#!/bin/bash

# This directory is where you have all your results locally, generally named as `allure-results`
ALLURE_RESULTS_DIRECTORY='./allure-results'
# Project ID according to existent projects in your Allure container - Check endpoint for project creation >> `[POST]/projects`
PROJECT_ID=${PROJECT_ID:-general}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "------------------COMPARE-RESULTS------------------"
cd $DIR
python ./same_as_yesterday.py
docker_result=$?

if [ ! "${docker_result}" == "0" ]; then
  echo "Exit with error code ${docker_result}"
  exit ${docker_result}
fi
