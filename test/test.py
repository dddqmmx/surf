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

def encrypt_message(message, public_key):
    ciphertext = public_key.encrypt(
        message.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

def decrypt_message(ciphertext, private_key):
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext.decode('utf-8')

# 示例用法
private_key, public_key = generate_key_pair()

# 假设 Bob 拿到了 Alice 的公钥，然后 Bob 加密消息给 Alice
message_to_alice = "Hello, Alice! This is a secure message from Bob."
encrypted_message = encrypt_message(message_to_alice, public_key)

# Alice 收到加密消息后用自己的私钥解密
decrypted_message = decrypt_message(encrypted_message, private_key)

print("Original Message:", message_to_alice)
print("Encrypted Message:", encrypted_message)
print("Decrypted Message:", decrypted_message)
