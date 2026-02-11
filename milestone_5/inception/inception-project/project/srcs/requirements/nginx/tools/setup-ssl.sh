#!/bin/sh
# =============================================================================
# SSL Certificate Generation Script for NGINX
# =============================================================================

SSL_DIR="/etc/nginx/ssl"
CERT_FILE="${SSL_DIR}/nginx.crt"
KEY_FILE="${SSL_DIR}/nginx.key"

# Create SSL directory if it doesn't exist
mkdir -p ${SSL_DIR}

# Check if certificates already exist
if [ -f "${CERT_FILE}" ] && [ -f "${KEY_FILE}" ]; then
    echo "SSL certificates already exist. Skipping generation."
else
    echo "Generating self-signed SSL certificate..."
    
    # Generate self-signed certificate
    # -x509: Generate self-signed certificate
    # -nodes: No passphrase on private key
    # -days: Certificate validity (365 days)
    # -newkey rsa:2048: Generate new RSA 2048-bit key
    # -keyout: Output file for private key
    # -out: Output file for certificate
    # -subj: Certificate subject (adjust as needed)
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ${KEY_FILE} \
        -out ${CERT_FILE} \
        -subj "/C=FR/ST=IDF/L=Paris/O=42/OU=42/CN=${DOMAIN_NAME:-login.42.fr}"
    
    if [ $? -eq 0 ]; then
        echo "SSL certificate generated successfully!"
        echo "Certificate: ${CERT_FILE}"
        echo "Private Key: ${KEY_FILE}"
    else
        echo "ERROR: Failed to generate SSL certificate!"
        exit 1
    fi
fi

# Set proper permissions
chmod 600 ${KEY_FILE}
chmod 644 ${CERT_FILE}

echo "SSL setup complete!"
