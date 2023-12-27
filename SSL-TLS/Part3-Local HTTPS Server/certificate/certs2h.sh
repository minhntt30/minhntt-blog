#!/bin/bash

create_cert()
{
    # Create a root CA key
    openssl genrsa -aes256 -out root-ca-key.pem -passout pass:0123456789

    # Create a public CA Cert
    openssl req -new -x509 -sha256 -days 365 -key root-ca-key.pem -out root-ca.pem -subj "/CN=rootCA" -passin pass:0123456789

    # Create RSA key
    openssl genrsa -out cert-key.pem 2048

    # Create a Certificate Signing Request (CSR)
    openssl req -new -sha256 -subj "/CN=tls_server" -key cert-key.pem -out cert-key.csr

    # Create certificate
    openssl x509 -req -sha256 -days 365 -in cert-key.csr -CA root-ca.pem -CAkey root-ca-key.pem -out cert.pem -extfile extfile.cnf -CAcreateserial -passin pass:0123456789

    # Create full chain
    cat cert.pem > fullchain.pem
    cat root-ca.pem >> ./fullchain.pem 

    # export rootCA to import to Client
    openssl pkcs12 -inkey root-ca-key.pem -in root-ca.pem -export -out rootCA.pfx -passin pass:0123456789 -passout pass:0123456789
}

server_key_der_2048()
{
    # Write the header of the .h file
    echo "static const unsigned char server_key_der_2048[] = " > "$output_path"

    # Read the input file line by line and append \r\n and \" to each line
    while IFS= read -r line; do
        if [[ $line == *"-----BEGIN PRIVATE KEY-----"* ]]; then
            echo "\"$line\r\n\\" >> "$output_path"
        elif [[ $line == *"-----END PRIVATE KEY-----"* ]]; then
            echo "$line\r\n\";" >> "$output_path"
        else
            echo "$line\r\n\\" >> "$output_path"
        fi
    done < "$cert_key_part"

    echo "static const int sizeof_server_key_der_2048 = sizeof(server_key_der_2048);" >> "$output_path"
}

server_cert_der_2048()
{
    # Write the header of the .h file
    begin_cert=true
    end_cert=false
    echo "static const unsigned char server_cert_der_2048[] = " >> "$output_path"

    # Read the input file line by line and append \r\n and \" to each line
    while IFS= read -r line; do
        if [[ $line == *"-----BEGIN CERTIFICATE-----"* ]] && $begin_cert; then
            echo "\"$line\r\n\\" >> "$output_path"
            begin_cert=false
        elif [[ $line == *"-----END CERTIFICATE-----"* ]]; then
            if $end_cert; then
                echo "$line\r\n\";" >> "$output_path"
            else
                echo "$line\r\n\\" >> "$output_path"
                end_cert=true
            fi
        else
            echo "$line\r\n\\" >> "$output_path"
        fi
    done < "$fullchain_part"

    echo "static const int sizeof_server_cert_der_2048 = sizeof(server_cert_der_2048);" >> "$output_path"   
}

create_cert
cert_key_part="cert-key.pem"
fullchain_part="fullchain.pem"
output_path="certificate.h"
server_key_der_2048
server_cert_der_2048

