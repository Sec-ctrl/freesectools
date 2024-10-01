import whois
from datetime import datetime


class WhoisLookup:
    def __init__(self, domain):
        self.domain = domain
        self.data = None

    def perform_lookup(self):
        """
        Perform a WHOIS lookup on the provided domain.
        """
        try:
            self.data = whois.whois(self.domain)
            return self._format_data()
        except Exception as e:
            return f"Error: Unable to retrieve WHOIS data for {self.domain}. {str(e)}"

    def _format_data(self):
        """
        Format the WHOIS data into a user-friendly dictionary.
        """
        return {
            "Domain Name": self._format_single_value(self.data.domain_name),
            "Registrar": self.data.registrar,
            "Whois Server": self.data.whois_server,
            "Creation Date": self._format_date(self.data.creation_date),
            "Expiration Date": self._format_date(self.data.expiration_date),
            "Last Updated": self._format_date(self.data.updated_date),
            "Name Servers": self._format_list(self.data.name_servers),
            "Status": self._clean_status(self.data.status),
            "Emails": self._format_list(self.data.emails),
            "Registrant": self.data.registrant,
        }

    def _format_list(self, value_list):
        if isinstance(value_list, list):
            return ", ".join(value_list)
        return value_list

    def _format_single_value(self, value):
        if isinstance(value, list):
            return value[0]
        return value

    def _format_date(self, date):
        if isinstance(date, list):
            return ", ".join([self._format_single_date(d) for d in date])
        return self._format_single_date(date)

    def _format_single_date(self, date):
        if isinstance(date, datetime):
            return date.strftime("%Y-%m-%d %H:%M:%S")
        return date

    def _clean_status(self, status_list):
        if isinstance(status_list, list):
            cleaned_status = set()  # Use a set to avoid duplicates
            for status in status_list:
                cleaned_status.add(
                    status.split()[0]
                )  # Take only the first part (before the URL)
            return ", ".join(cleaned_status)
        return status_list
