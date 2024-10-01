import dns.resolver
import socket
import ssl


class DNSLookup:
    def __init__(self, domain):
        self.domain = domain

    def perform_lookup(self):
        try:
            # Store results in a dictionary with more record types
            dns_data = {
                "A": [],
                "AAAA": [],
                "MX": [],
                "NS": [],
                "TXT": [],
                "CNAME": [],
                "SOA": [],
                "PTR": [],
                "SPF": [],
                "SRV": [],
                "DNSSEC": [],
                "SSL Certificate": None,
                "TTL": {},
            }

            # Perform DNS queries and gather TTL
            for record_type in ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]:
                try:
                    answers = dns.resolver.resolve(self.domain, record_type)
                    dns_data[record_type] = [str(answer) for answer in answers]
                    dns_data["TTL"][record_type] = answers.rrset.ttl
                except Exception as e:
                    dns_data[record_type] = f"Error: {e}"

            # SSL certificate retrieval
            ssl_cert = self.get_ssl_certificate(self.domain)
            if not ssl_cert:
                # Try with www prefix
                ssl_cert = self.get_ssl_certificate(f"www.{self.domain}")
            dns_data["SSL Certificate"] = (
                ssl_cert if ssl_cert else "No SSL certificate detected."
            )

            return dns_data

        except Exception as e:
            return f"Error: {e}"

    def get_ssl_certificate(self, domain):
        """Fetch SSL/TLS certificate info for the domain."""
        context = ssl.create_default_context()
        try:
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as sslsock:
                    cert = sslsock.getpeercert()
                    return {
                        "subject": dict(x[0] for x in cert["subject"]),
                        "issuer": dict(x[0] for x in cert["issuer"]),
                        "valid_from": cert["notBefore"],
                        "valid_to": cert["notAfter"],
                        "serial_number": cert["serialNumber"],
                        "version": cert["version"],
                    }
        except Exception as e:
            return f"Error retrieving SSL certificate: {e}"
