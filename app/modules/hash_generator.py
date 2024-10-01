# app/modules/hash_generator.py
import hashlib
import base64
import hmac


class AdvancedHashGenerator:
    def __init__(
        self, algorithm="sha256", use_hmac=False, secret_key=None, output_format="hex"
    ):
        """
        Initializes the AdvancedHashGenerator with:
        - algorithm: Hashing algorithm to use (e.g., 'md5', 'sha256', 'blake2b').
        - use_hmac: Whether to use HMAC for hashing.
        - secret_key: The secret key for HMAC (if used).
        - output_format: 'hex' or 'base64' for hash output format.
        """
        self.algorithm = algorithm.lower()
        self.use_hmac = use_hmac
        self.secret_key = secret_key.encode("utf-8") if secret_key else None
        self.output_format = output_format

        if self.algorithm not in hashlib.algorithms_available:
            raise ValueError(f"Algorithm {self.algorithm} is not supported.")

    def generate_hash(self, input_data, salt=""):
        """
        Generates a hash for the given input data (text, URL, etc.) with optional salt.
        """
        input_data = salt + input_data
        if self.use_hmac and self.secret_key:
            hash_function = hmac.new(
                self.secret_key, input_data.encode("utf-8"), self.algorithm
            )
        else:
            hash_function = hashlib.new(self.algorithm)
            hash_function.update(input_data.encode("utf-8"))

        return self._format_output(hash_function)

    def generate_file_hash(self, file_path, salt=""):
        """
        Generates a hash for a given file with optional salt.
        Reads the file in chunks to handle large files.
        """
        hash_function = (
            hmac.new(self.secret_key, salt.encode("utf-8"), self.algorithm)
            if self.use_hmac and self.secret_key
            else hashlib.new(self.algorithm)
        )

        with open(file_path, "rb") as file:
            while chunk := file.read(8192):
                hash_function.update(chunk)

        return self._format_output(hash_function)

    def generate_batch_hashes(self, inputs, salt=""):
        """
        Batch processing of multiple inputs. Supports both text and file paths.
        """
        results = {}
        for item in inputs:
            if isinstance(item, str):
                if item.startswith("http") or item.startswith("/"):  # URL or File
                    try:
                        results[item] = self.generate_file_hash(item, salt=salt)
                    except Exception:
                        results[item] = self.generate_hash(item, salt=salt)
                else:  # Plain text input
                    results[item] = self.generate_hash(item, salt=salt)
        return results

    def _format_output(self, hash_function):
        """
        Formats the hash output based on user preferences (hex or base64).
        """
        if self.output_format == "base64":
            return base64.b64encode(hash_function.digest()).decode("utf-8")
        return hash_function.hexdigest()
