Raiden Known Servers Metrics SD
-------------------------------

Generate Prometheus file-sd target files from the Raiden Service Bundle known servers file.
Used in our monitoring setup.


Dev Install
===========

- Have Poetry
- Run `make install`

Build Docker Image
==================

- Have Poetry
- Have Docker
- Run `make build`

Publish Docker Image
====================

Docker Hub is set up to automatically build latest `master`.

Build / publish manually:

- Have Docker
- Run `make publish`
