FROM python:3.9-slim

COPY dist/*.whl /

RUN pip install /*.whl

ENTRYPOINT ["/usr/local/bin/raiden-known-servers-metrics-sd"]
