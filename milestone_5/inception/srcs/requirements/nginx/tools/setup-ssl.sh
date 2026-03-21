#!/bin/sh

SSL_DIR="/etc/nginx/ssl"
CERT_FILE="${SSL_DIR}/nginx.crt"
KEY_FILE="${SSL_DIR}/nginx.key"

mkdir -p ${SSL_DIR}

if [ -f "${CERT_FILE}" ] && [ -f "${KEY_FILE}" ]; then
    echo "SSL certificates already exist."
else
    echo "Generating self-signed SSL certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ${KEY_FILE} \
        -out ${CERT_FILE} \
        -subj "/C=FR/ST=IDF/L=Paris/O=42/OU=42/CN=${DOMAIN_NAME:-localhost}"
    echo "SSL certificate generated!"
fi

chmod 600 ${KEY_FILE}
chmod 644 ${CERT_FILE}
