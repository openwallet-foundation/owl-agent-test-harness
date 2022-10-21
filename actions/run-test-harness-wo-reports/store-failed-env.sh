#!/bin/bash
BOB="unknown"
DEFAULT="unknown"
while getopts ":b:d:" FLAG; do
    case $FLAG in
        b ) BOB=${OPTARG}
            ;;
        d )
            DEFAULT=${OPTARG}
            ;;
    esac
done

VERSION_FAILED="build-failed"

env_file="$(pwd)/test-harness/aries-test-harness/allure/allure-results/environment.properties"
declare -a env_array
env_array+=("role.acme=$DEFAULT")
env_array+=("acme.agent.version=$VERSION_FAILED")
env_array+=("role.bob=$BOB")
env_array+=("bob.agent.version=$VERSION_FAILED")
env_array+=("role.faber=$DEFAULT")
env_array+=("faber.agent.version=$VERSION_FAILED")
env_array+=("role.mallory=$DEFAULT")
env_array+=("mallory.agent.version=$VERSION_FAILED")
printf "%s\n" "${env_array[@]}" > $env_file
