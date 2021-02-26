install:
	poetry install

build:
	docker build -t raidennetwork/raiden-known-servers-metrics-sd .

publish: build
	docker push -a raidennetwork/raiden-known-servers-metrics-sd
