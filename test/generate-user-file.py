import json
import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def main():
    fileJson = {'server_address': input("输入你想要连接的服务器:"), 'server_passwords': input("输入服务器基本加密密码:")}
    private_key, public_key = generate_key_pair()

    public_key_str = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    private_key_str = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()  # No encryption
    ).decode('utf-8')

    # 进行第一次Base64编码
    public_key_b64 = base64.b64encode(public_key_str.encode('utf-8')).decode('utf-8')
    private_key_b64 = base64.b64encode(private_key_str.encode('utf-8')).decode('utf-8')

    fileJson['public_key'] = public_key_b64
    fileJson['private_key'] = private_key_b64

    with open('keys.json', 'w') as f:
        json.dump(fileJson, f, indent=4)
    print("生成成功")


if __name__ == "__main__":
    main()
