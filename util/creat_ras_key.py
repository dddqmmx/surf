from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding


def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def main():
    # Generate key pair
    private_key, public_key = generate_key_pair()

    # Write public key to file
    with open("public_key.pem", "wb") as public_key_file:
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        public_key_file.write(public_key_bytes)

    # Write private key to file
    with open("private_key.pem", "wb") as private_key_file:
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()  # No encryption
        )
        private_key_file.write(private_key_bytes)

    print("Public and private keys are written to public_key.pem and private_key.pem respectively.")


if __name__ == "__main__":
    main()
