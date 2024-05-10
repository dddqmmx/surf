import { Injectable } from '@angular/core';
import forge from "node-forge";
@Injectable({
    providedIn: 'root'
})
export class CryptoService {
    session: string | undefined;
    serverPublicKey: string | undefined;
    clientPrivateKey: string | undefined;
    setServerPublicKey(publicKey:string): void {
        this.serverPublicKey = publicKey
    }
    setClientPrivateKey(publicKey:string): void {
        this.clientPrivateKey = publicKey
    }
    setSession(publicKey:string): void {
        this.session = publicKey
    }
    encryptData(data: string): string | false {
        const self = this;
        if (typeof self.serverPublicKey === 'string'){
            try {
                const publicKeyObj = forge.pki.publicKeyFromPem(self.serverPublicKey);
                const blockSize = 400; // 设置块大小
                const dataChunks = data.match(new RegExp(`.{1,${blockSize}}`, 'g')); // 将数据拆分为块
                let encryptedChunks: string[] = [];

                if (dataChunks) {
                    for (const chunk of dataChunks) {
                        const buffer = forge.util.encodeUtf8(chunk);
                        const encrypted = publicKeyObj.encrypt(buffer, 'RSA-OAEP', {
                            md: forge.md.sha256.create(),
                            mgf1: {
                                md: forge.md.sha256.create()
                            }
                        });
                        encryptedChunks.push(forge.util.encode64(encrypted));
                    }
                    return encryptedChunks.join(' '); // 将加密后的块连接成一个字符串
                } else {
                    throw new Error('Data splitting failed.');
                }
            } catch (err) {
                console.error('Encryption failed:', err);
            }
        }
        return false;
    }

    decryptData(encryptedData: string, privateKey: string): string | false {
        try {
            const privateKeyObj = forge.pki.privateKeyFromPem(privateKey);
            const encryptedChunks = encryptedData.split(' '); // Split encrypted data into chunks
            let decryptedChunks: string[] = [];

            for (const chunk of encryptedChunks) {
                const encryptedBytes = forge.util.decode64(chunk);
                const decrypted = privateKeyObj.decrypt(encryptedBytes, 'RSA-OAEP', {
                    md: forge.md.sha256.create(),
                    mgf1: {
                        md: forge.md.sha256.create()
                    }
                });
                decryptedChunks.push(forge.util.decodeUtf8(decrypted));
            }

            return decryptedChunks.join(''); // Join decrypted chunks into a single string
        } catch (err) {
            console.error('Decryption failed:', err);
            return false;
        }
    }

    async exportPublicKey(key: CryptoKey): Promise<string> {
        const exported = await window.crypto.subtle.exportKey("spki", key);
        let binary = '';
        const bytes = new Uint8Array(exported);
        const len = bytes.byteLength;
        for (let i = 0; i < len; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return window.btoa(binary);
    }

    generateKeyPair(): Promise<CryptoKeyPair> {
        return new Promise((resolve, reject) => {
            window.crypto.subtle.generateKey({
                name: "RSA-OAEP",
                modulusLength: 4096, // 密钥大小
                publicExponent: new Uint8Array([0x01, 0x00, 0x01]), // 公钥指数，等于65537
                hash: {name: "SHA-256"}, // 使用SHA-256哈希算法
            },
            true, // 是否提取密钥
            ["encrypt", "decrypt"] // 密钥用途
        ).then(function(cryptoKeyPair) {
            resolve(cryptoKeyPair);
        }).catch(function(err) {
            console.error(err);
            reject(err);
        });
    });
}


}
