FROM python:3.9 as BUILDER

RUN pip install -U poetry && mkdir -p /src/raiden-known-servers-metrics-sd

COPY poetry.lock /src/raiden-known-servers-metrics-sd
COPY pyproject.toml /src/raiden-known-servers-metrics-sd

WORKDIR /src/raiden-known-servers-metrics-sd

RUN poetry install

ADD . /src/raiden-known-servers-metrics-sd/

RUN ls -la && poetry build

FROM python:3.9-slim

COPY --from=BUILDER /src/raiden-known-servers-metrics-sd/dist/*.whl /

RUN pip install /*.whl

ENTRYPOINT ["/usr/local/bin/raiden-known-servers-metrics-sd"]
