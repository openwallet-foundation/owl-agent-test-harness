FROM ubuntu:18.04 as base

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -y && apt-get install -y \
    software-properties-common \
    apt-transport-https \
    curl \
    # Only needed to build indy-sdk
    build-essential 

# libindy
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88
RUN add-apt-repository "deb https://repo.sovrin.org/sdk/deb bionic stable"

# nodejs
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash

# yarn
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list

# install depdencies
RUN apt-get update -y && apt-get install -y --allow-unauthenticated \
    libindy \
    nodejs

# Install yarn seperately due to `no-install-recommends` to skip nodejs install 
RUN apt-get install -y --no-install-recommends yarn

FROM base as final

WORKDIR /src
ENV RUN_MODE="docker"

# Prints logs to CLI, nog log file.
# Let's wait with this until we have properly implemented logging in AFJ
# ENV DEBUG="aries-framework-javascript"

COPY javascript/server/package.json package.json
COPY javascript/server/yarn.lock yarn.lock
COPY javascript/aries-framework-javascript-v1.0.0.tgz ../aries-framework-javascript-v1.0.0.tgz

# Run install after copying only depdendency file
# to make use of docker layer caching
RUN yarn install

# Copy other depedencies
COPY javascript/server .

# For now we use ts-node. Compiling with typescript
# doesn't work because indy-sdk types are not exported
ENTRYPOINT [ "yarn", "ts-node", "src/index.ts" ]