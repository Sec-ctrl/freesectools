import hashlib
import requests

class EmailBreachChecker:
    def __init__(self):
        self.base_url = 'https://api.pwnedpasswords.com/range/'

    def _get_sha1_hash(self, email: str) -> str:
        """
        Hash the email using SHA-1.
        """
        sha1 = hashlib.sha1(email.encode('utf-8')).hexdigest().upper()
        return sha1

    def check_email_breach(self, email: str) -> bool:
        """
        Check if the given email has been part of any data breaches using hashed checks.
        Returns True if the email hash is found in breach data.
        """
        sha1_hash = self._get_sha1_hash(email)
        prefix, suffix = sha1_hash[:5], sha1_hash[5:]

        try:
            response = requests.get(f"{self.base_url}{prefix}")
            if response.status_code == 200:
                hashes = (line.split(':') for line in response.text.splitlines())
                for hash_suffix, count in hashes:
                    if hash_suffix == suffix:
                        return True  # Email found in breaches
                return False  # Email not found
            else:
                return False  # Unable to fetch or not found
        except requests.RequestException as e:
            print(f"Error: {e}")
            return False

# Usage example:
# Create an instance of the checker class
email_breach_checker = EmailBreachChecker()

# Perform an email breach check
email_to_check = 'christiannielsendk10@gmail.com'
breach_found = email_breach_checker.check_email_breach(email_to_check)

if breach_found:
    print("The email has been found in breaches.")
else:
    print("The email has not been found in any breaches.")
