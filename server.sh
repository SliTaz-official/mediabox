#!/bin/sh
#
# server.sh - Serve MediBox via Busybox HTTPd for development
#
. /lib/libtaz.sh

if [ -d "cache" ]; then
	port=8090
	echo "Starting server on port: $port"
	echo "URL: $(boldify http://localhost:$port/)"
	echo "Press CTRL+C to stop the server"
	httpd -f -u www:www -p ${port} -c data/httpd.conf
else
	echo "Missing cache dir: cache/"
	echo "install -d -m 0777 cache"
fi && exit 0
