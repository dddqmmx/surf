import os
import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    return private_key, public_key


def decrypt_data(ciphertext, private_key):
    try:
        decrypted_message = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_message
    except ValueError as ve:
        print(f"Decryption failed: ValueError - {ve}")
    except Exception as e:
        print(f"Decryption failed: {type(e).__name__} - {e}")
    return None


def encrypt_data(input_file, output_file, public_key):
    block_size = 446  # 调整块大小以符合你的加密算法的要求
    with open(input_file, 'rb') as f_in:
        with open(output_file, 'wb') as f_out:
            while True:
                chunk = f_in.read(block_size)
                if not chunk:
                    break
                encrypted_chunk = encrypt_with_serialized_public_key(chunk, public_key)  # 你需要实现这个函数
                f_out.write(encrypted_chunk)


def encrypt_with_serialized_public_key(data, serialized_public_key):
    public_key = serialization.load_pem_public_key(
        serialized_public_key.encode(),
        backend=default_backend()
    )

    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return ciphertext


if __name__ == '__main__':
    data_file = "kanan.mp4"
    encrypted_file = "encrypted_kanan.mp4"
    public_key = """
        -----BEGIN PUBLIC KEY-----
    MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAuasaDw1Vzfy2JSpgU3+D
    Dy0tC5ZuqMJ8NjzgBO9PKAqU8AwbzmVtF93KbyO1wLRLbrIy1GKIVPdwFp9Un6Vv
    RMxr1CHfDv6XQiaJfn2KgQZCYCrj8DJ+po87agyQwGk6dJCsfM8z1zsjgwPBLrLs
    pz8ifFpcIRI/X1uktTKRshxVVHt8kXb5kD9zIC5zDQqPLyW5NqhPVDmMTvqotm9K
    brYjJymn/qi2nTjep3Z+1qlzy6gOEqxKzkjVpwYr2SlmaDANbOdJjrnAWl4qU5sw
    z+34VNIdhrSJxWF0QGc3iO6PCYKofaelQbXf27Q1yRMSu61/HjvhVQcoNv1y1POg
    JYdolbDL0aoiXSW9fN+hGwtff73v20zeu7tFYj0m5bs1Ewro+dcR6lBaTPpQfvC/
    rueJhzMg0/gxoLQAjB7y9MVuPa3DPUiIQivKGxkT7vJvSyXgBooJ8vb4MztIHoPF
    x1otfCNOj8Utiptn+8QSQvtQrEvIYuZZ8DgIGu6kQW1D36aDmbTWkkM/ML7RdF7m
    1ZNorA31gOrPZprNTPS9qEkSclxulhguGwfXPG0NY45Vq6XhQmLGCF0UZXxkEyej
    Wu+JV14e2Q5IsM7mhZNBZyJ4qJ6u0T1gDT2vVX3ukZ6vkg6VkX7qLQMD95gG0f7i
    pJ1tPY5s0mhNdTIJo80sNNsCAwEAAQ==
    -----END PUBLIC KEY-----

        """
    # Encrypt the data
    encrypt_data(data_file, encrypted_file, public_key)

    # Get file sizes
    original_size = os.path.getsize(data_file)
    encrypted_size = os.path.getsize(encrypted_file)

    print("Original File Size:", original_size, "bytes")
    print("Encrypted File Size:", encrypted_size, "bytes")
