FROM python:3.7-buster
COPY . /aries-test-harness
WORKDIR /aries-test-harness
RUN pip install -r requirements.txt

RUN \
    echo "==> Install stuff not in the requirements..."   && \
    pip install --no-cache-dir \
        aiohttp

ENTRYPOINT ["behave"]