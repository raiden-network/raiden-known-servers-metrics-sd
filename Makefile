install:
	poetry install

build:
	poetry build
	docker build -t raidennetwork/raiden-known-servers-metrics-sd .
