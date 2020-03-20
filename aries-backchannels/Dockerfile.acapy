FROM python:3.7-buster
COPY . /aries-backchannels
WORKDIR /aries-backchannels
RUN pip install -r requirements.txt

# install libraries used for remote debugging into container from Visual Studio Code
RUN pip install ptvsd

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88 \
   && apt-get update \
   && apt-get install -y software-properties-common \
   && apt-get update \
   && add-apt-repository 'deb https://repo.sovrin.org/sdk/deb bionic stable' \
   && apt-get update \
   && apt-get install -y libindy \
   && apt-get install -y libnullpay

ENV RUNMODE=docker

#aca-py is in /usr/local/bin. The Backchannel is looking for it in ./bin, create a link to it in ./bin
RUN mkdir -p ./bin
RUN ln -s /usr/local/bin/aca-py ./bin/aca-py

ENTRYPOINT ["python", "-m", "ptvsd", "--host", "0.0.0.0", "--port", "5678", "--wait", "acapy_backchannel.py"]