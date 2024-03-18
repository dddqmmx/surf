from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

def encrypt_with_serialized_public_key(message, serialized_public_key):
    public_key = serialization.load_pem_public_key(
        serialized_public_key.encode(),
        backend=default_backend()
    )

    ciphertext = public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return ciphertext

def decrypt_with_private_key(ciphertext, private_key):
    try:
        decrypted_message = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_message.decode()
    except ValueError as ve:
        print(f"Decryption failed: ValueError - {ve}")
    except Exception as e:
        print(f"Decryption failed: {type(e).__name__} - {e}")
    return None


def main():
    # 生成密钥对
    private_key, public_key = generate_key_pair()

    public_key_str = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    print(f"Public Key:\n{public_key_str}")

    message = "Hello, cryptography!"
    ciphertext = encrypt_with_serialized_public_key(message, public_key_str)

    print(f"Original Message: {message}")
    print(f"Encrypted Message: {ciphertext.hex()}")

    decrypted_message = decrypt_with_private_key(ciphertext, private_key)

    if decrypted_message is not None:
        print(f"Decrypted Message: {decrypted_message}")
    else:
        print("Decryption failed.")

if __name__ == "__main__":
    main()
