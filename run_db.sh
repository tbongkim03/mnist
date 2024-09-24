#!/bin/bash

sudo docker run -d \
	--name mariadb \
	-e MARIADB_USER=mnist \
	--env MARIADB_PASSWORD=1234 \
	--env MARIADB_DATABASE=mnistdb \
	--env MARIADB_ROOT_PASSWORD=my-secret-pw \
	-p 53306:3306 \
	mariadb:latest
