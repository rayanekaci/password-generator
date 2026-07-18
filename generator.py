import secrets
import string
import sys


def generate_password(length: int) -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        has_upper = any(c in string.ascii_uppercase for c in password)
        has_lower = any(c in string.ascii_lowercase for c in password)
        has_digit = any(c in string.digits for c in password)
        has_symbol = any(c in string.punctuation for c in password)
        if has_upper and has_lower and has_digit and has_symbol:
            return password


def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit() or int(sys.argv[1]) < 4:
        print("Usage: python generator.py <length>")
        print("Password length must be a number >= 4.")
        sys.exit(1)

    length = int(sys.argv[1])
    print(f"Generated password: {generate_password(length)}")


if __name__ == "__main__":
    main()
