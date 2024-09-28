import dns.resolver
import dns.query
import dns.zone
import time
import socket
import ssl
import requests

class DNSLookup:
    def __init__(self, domain):
        self.domain = domain
        self.dns_servers = ['8.8.8.8', '1.1.1.1', '9.9.9.9', '208.67.222.222']  # Global DNS servers

    def perform_lookup(self):
        try:
            # Store results in a dictionary with more record types
            dns_data = {
                'A': [],
                'AAAA': [],
                'MX': [],
                'NS': [],
                'TXT': [],
                'CNAME': [],
                'SOA': [],
                'PTR': [],
                'SPF': [],
                'SRV': [],
                'DNSSEC': [],
                'Propagation': {},
                'Zone Transfer': [],
                'SSL Certificate': None,
                'TTL': {},
                'Timing': {},
            }

            # Record query start time
            start_time = time.time()

            # Perform DNS queries and gather TTL
            for record_type in dns_data.keys():
                if record_type in ['Propagation', 'SSL Certificate', 'Zone Transfer', 'Timing', 'DNSSEC']:
                    continue  # Skip custom fields here
                
                try:
                    answers = dns.resolver.resolve(self.domain, record_type)
                    dns_data['Timing'][record_type] = time.time() - start_time  # Timing for each query
                    
                    for answer in answers:
                        dns_data[record_type].append(str(answer))
                        if hasattr(answer, 'ttl'):
                            dns_data['TTL'][record_type] = answer.ttl

                    # DNSSEC Records
                    if record_type in ['RRSIG', 'DNSKEY']:
                        dns_data['DNSSEC'].append(f"{record_type}: {answer}")

                except dns.resolver.NoAnswer:
                    dns_data[record_type] = 'No record found'
                except dns.resolver.NXDOMAIN:
                    dns_data[record_type] = 'Domain does not exist'
                except dns.resolver.Timeout:
                    dns_data[record_type] = 'Query timed out'
                except dns.resolver.NoNameservers:
                    dns_data[record_type] = 'No nameservers available'
                except Exception as e:
                    dns_data[record_type] = f'Error: {e}'

            # Perform DNS Propagation Check
            for server in self.dns_servers:
                try:
                    resolver = dns.resolver.Resolver()
                    resolver.nameservers = [server]
                    answers = resolver.resolve(self.domain, 'A')
                    dns_data['Propagation'][server] = [str(answer) for answer in answers]
                except Exception as e:
                    dns_data['Propagation'][server] = f"Error: {e}"

            # Zone Transfer (AXFR) Test
            try:
                ns_answer = dns.resolver.resolve(self.domain, 'NS')
                primary_ns = str(ns_answer[0])
                zone = dns.zone.from_xfr(dns.query.xfr(primary_ns, self.domain))
                if zone:
                    dns_data['Zone Transfer'].append(f"Zone transfer succeeded: {primary_ns}")
                else:
                    dns_data['Zone Transfer'].append(f"Zone transfer failed: {primary_ns}")
            except Exception as e:
                dns_data['Zone Transfer'].append(f"Error during zone transfer: {e}")

            # SSL/TLS Certificate Info (for domains with HTTPS)
            try:
                cert_info = self.get_ssl_certificate(self.domain)
                dns_data['SSL Certificate'] = cert_info
            except Exception as e:
                dns_data['SSL Certificate'] = f"Error: {e}"

            return dns_data

        except Exception as e:
            return f'Error: {e}'

    def get_ssl_certificate(self, domain):
        """Fetch SSL/TLS certificate info for the domain."""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as sslsock:
                    cert = sslsock.getpeercert()
            return cert
        except Exception as e:
            return f"SSL Certificate error: {e}"

# Example usage
dns_lookup = DNSLookup('example.com')
dns_data = dns_lookup.perform_lookup()
print(dns_data)