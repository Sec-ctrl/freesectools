import random
import string


class PasswordGenerator:
    def __init__(
        self,
        length=12,
        include_uppercase=True,
        include_lowercase=True,
        include_digits=True,
        include_symbols=True,
        exclude_similar=False,
        exclude_ambiguous=False,
        exclude_quotes=False,
        exclude_custom=False,
        custom_chars="",
    ):
        self.length = length
        self.include_uppercase = include_uppercase
        self.include_lowercase = include_lowercase
        self.include_digits = include_digits
        self.include_symbols = include_symbols
        self.exclude_similar = exclude_similar
        self.exclude_ambiguous = exclude_ambiguous
        self.exclude_quotes = exclude_quotes
        self.exclude_custom = exclude_custom
        self.similar_chars = "il1Lo0O"  # Characters that look alike
        self.ambiguous_chars = "{}[]()/'\"`~,;:.<>\\|"
        self.quotes = "\"'"
        self.custom_chars = custom_chars

    def generate(self):
        characters = ""
        if self.include_uppercase:
            characters += string.ascii_uppercase
        if self.include_lowercase:
            characters += string.ascii_lowercase
        if self.include_digits:
            characters += string.digits
        if self.include_symbols:
            characters += string.punctuation

        # Remove similar chars if needed
        if self.exclude_similar:
            characters = "".join(
                [char for char in characters if char not in self.similar_chars]
            )

        # Remove ambiguous chars if needed
        if self.exclude_ambiguous:
            characters = "".join(
                [char for char in characters if char not in self.ambiguous_chars]
            )

        # Remove quotes if needed
        if self.exclude_quotes:
            characters = "".join(
                [char for char in characters if char not in self.quotes]
            )

        # Remove custom chars if needed
        if self.exclude_custom and self.custom_chars:
            characters = "".join(
                [char for char in characters if char not in self.custom_chars]
            )

        if not characters:
            raise ValueError("No character set selected for password generation.")

        password = "".join(random.choice(characters) for _ in range(self.length))
        return password
