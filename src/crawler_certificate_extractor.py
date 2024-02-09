from datetime import datetime
import json
import os

from cryptography import x509
from cryptography.hazmat.backends import default_backend
import ssl
import socket

import util
import util_def


def parse_date(date):
    # Convert the original date string to a datetime object
    dt = datetime.strptime(date, "%b %d %H:%M:%S %Y %Z")

    # Format the datetime object to the desired format
    formatted_date = dt.strftime("%b %d %Y")

    return formatted_date



def calc_duration(start, end):
    start = parse_date(start)
    end = parse_date(end)

    # Convert the date string to a datetime object
    start = datetime.strptime(start, "%b %d %Y").date()
    end = datetime.strptime(end, "%b %d %Y").date()

    num_days = (end - start).days
    return num_days



def get_certificate_signature_algorithm(cert):
    cert_object = x509.load_der_x509_certificate(cert, default_backend())
    signature_algorithm = cert_object.signature_algorithm_oid._name
    return signature_algorithm


def determine_port_from_website_protocol(url):
    if url.startswith("http://"):
        return 80
    
    if url.startswith("https://"):
        return 443


# Extracts and saves the TLS/SSL certificate info of the url if available
def extract_certificate_info(website_url, folder_path):
    error_tag = "Connection Error"
    port = determine_port_from_website_protocol(website_url)

    # Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get the hostname from the url
    hostname = util.extract_hostname(website_url)
    if hostname is None:
        status = "Failed"
        print("Error extracting certificate info...")
        return status
    

    # Wrap the socket with SSL/TLS
    context = ssl.create_default_context()
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        try:
            # Establish a connection to the website
            ssock.connect((hostname, port))

            # Get the TLS certificate information
            cert = ssock.getpeercert()
            cert_binary = ssock.getpeercert(binary_form=True)

            # Extract certificate details
            subject = dict(x[0] for x in cert["subject"])
            alt_subject= cert["subjectAltName"]
            issuer = dict(x[0] for x in cert["issuer"])
            version = cert["version"]
            not_before = cert["notBefore"]
            not_after = cert["notAfter"]
            valid_period = calc_duration(not_before, not_after)
            serial_number = cert["serialNumber"]
            signature_algorithm = get_certificate_signature_algorithm(cert_binary)
            protocol_version = ssock.version()

        except Exception as e:
            print("Cert Extraction Error: ", e)
            subject = {
                "commonName": error_tag,
                "organizationName": error_tag,
                "localityName": error_tag,
                "stateOrProvinceName": error_tag,
                "countryName": error_tag,
                "businessCategory": error_tag,
                "serialNumber": error_tag,
                "jurisdictionState": error_tag,
                "jurisdictionLocality": error_tag,
            }

            issuer = {
                "countryName": error_tag,
                "organizationName": error_tag,
                "organizationalUnitName": error_tag,
                "commonName": error_tag,
            }
            version = error_tag 
            not_before = error_tag 
            not_after = error_tag 
            valid_period = error_tag 
            serial_number = error_tag 
            signature_algorithm = error_tag
            protocol_version = error_tag
            alt_subject = [error_tag]
            
        finally:
            ssock.close()
    
            data = {
                "website url": website_url,
                "hostname": hostname,
                "subject": subject,
                "issuer": issuer,
                "version": version,
                "not_before": not_before,
                "not_after": not_after,
                "valid_period": valid_period,
                "serial_number": serial_number,
                "signature_algo": signature_algorithm,
                "protocol_version": protocol_version,
                "alternate subject name": alt_subject
            }

            json_file_output_path = os.path.join(folder_path, util_def.FILE_CERT)
            util.save_data_to_json_format(json_file_output_path, data)
            
            print("Certificate info saved.")
            status = "Success"
            
            return status
