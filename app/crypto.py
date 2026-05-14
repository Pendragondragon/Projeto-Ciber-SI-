import hashlib
import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidKey

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding

import rsa
import sqlite3

load_dotenv()

def HMAC_authentication(hmac_hash, cryptogram):
    INTEGRITY_KEY = os.getenv("HMAC_INTEGRITY_KEY")

    if hmac_hash == "sha256":  
        block_size = 64
        hash_func = hashlib.sha256
    else:
        block_size = 128
        hash_func = hashlib.sha512

    key = INTEGRITY_KEY.encode()

    if len(key) > block_size:
        key = hash_func(key).digest()
    elif len(key) < block_size:
        key = key.ljust(block_size, b'\x00')

    ipad = bytes((x ^ 0x36) for x in key)
    opad = bytes((x ^ 0x5c) for x in key)

    inner_pad = hash_func(ipad + cryptogram).digest()
    result = hash_func(opad + inner_pad).hexdigest()
    return result

def sign_digitally(sig_hash, message):
    keyfile = "pk_and_sk.pem"
    key_password = os.getenv("PRIVATE_KEY_PASSWORD")
    if key_password:
        key_password = key_password.encode()

    with open(keyfile, "rb") as key_file:
        sk = serialization.load_pem_private_key(
            key_file.read(),
            password=key_password
        )

    if sig_hash == "sha256":  
        hash_func = hashes.SHA256()  
    else:
        hash_func = hashes.SHA512()  

    if isinstance(message, str):
        message = message.encode()  

    signature = sk.sign(
        message,
        asym_padding.PSS(
            mgf=asym_padding.MGF1(hash_func),
            salt_length=asym_padding.PSS.MAX_LENGTH
        ),
        hash_func
    )
    return signature

def verify_signature(signature, message, sig_hash):
    keyfile = "pk.pem"
    with open(keyfile, "rb") as key_file:
        pk = serialization.load_pem_public_key(key_file.read())

    if sig_hash == "sha256":  
        hash_func = hashes.SHA256()
    else:
        hash_func = hashes.SHA512()

    if isinstance(message, str):
        message = message.encode()  

    try:
        pk.verify(
            signature,
            message,
            sym_padding.PSS(
                mgf=sym_padding.MGF1(hash_func),
                salt_length=sym_padding.PSS.MAX_LENGTH
            ),
            hash_func
        )
        return True
    except Exception:
        return False
    
#pega na password e deriva de forma a ficar aleatorio e com tamanho maior
#devolve a chave no formato certo e o salt usado no processo
def deriveKey(key):
    salt = os.urandom(16)
    keyBytes = key.encode()
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1_200_000,
    )

    key = kdf.derive(keyBytes)
    return salt, key

def verifyDerivedKey(salt, storedKey, insertedKey):
    password = insertedKey.encode()

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1_200_000,
    )

    try:
        kdf.verify(password, storedKey)        
        return True
    except InvalidKey:
        return False
    


# Chave Simétrica (POR TESTETAR - NÃO USAR AINDA)

## AES256_CBC

def random_bytes(n: int) -> bytes:
    return os.urandom(n)
    
def aes256_cbc_encrypt(message, key, iv):
    if key == None:
        key = random_bytes(32)
    else:
        if len(key) != 32:
            key = hashlib.sha256(key.encode()).digest()
    if iv is None:
        iv = os.urandom(16)
    if len(iv) != 16:
        raise ValueError("CBC IV must be 16 bytes")

    padder = sym_padding.PKCS7(128).padder()
    padded_message = padder.update(message.encode('utf-8'))
    padded_message += padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_message) + encryptor.finalize()
    
    return ciphertext, iv, key

def decrypt_AES_CBC(ciphertext, key, iv):
    decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = sym_padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data)
    unpadded_data += unpadder.finalize()
    return unpadded_data.decode('utf-8')


## AES256_CTR
def aes256_ctr_encrypt(message, key, iv):
    if key == None:
        key = random_bytes(32)
    else:
        if len(key) != 32:
            key = hashlib.sha256(key.encode()).digest()
    if iv is None:
        iv = os.urandom(16)
    if len(iv) != 16:
        raise ValueError("CTR IV must be 16 bytes")

    padder = sym_padding.PKCS7(128).padder()
    padded_message = padder.update(message.encode('utf-8'))
    padded_message += padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_message) + encryptor.finalize()
    
    return ciphertext, iv, key

def decrypt_AES_CTR(ciphertext, key, iv):
    decryptor = Cipher(algorithms.AES(key), modes.CTR(iv)).decryptor()
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = sym_padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data)
    unpadded_data += unpadder.finalize()
    return unpadded_data.decode('utf-8')


# ChaCha20

def encrypt_chacha20(message, key, iv):
    if iv is None:
        iv = os.urandom(16)
    if len(iv) != 16:
        raise ValueError("CBC IV must be 16 bytes")
    algorithm = algorithms.ChaCha20(key, iv)
    cipher = Cipher(algorithm, mode=None) # Stream ciphers não precisam de 'mode' externo
    encryptor = cipher.encryptor()
    
    ciphertext = encryptor.update(message.encode('utf-8'))
    return ciphertext, iv

def decrypt_chacha20(ciphertext, key, iv):
    algorithm = algorithms.ChaCha20(key, iv)
    cipher = Cipher(algorithm, mode=None)
    decryptor = cipher.decryptor()
    
    plaintext = decryptor.update(ciphertext)
    return plaintext.decode('utf-8')

#RSA

def generate_keys(bits: int) -> tuple[bytes, bytes]:

    public_key, private_key = rsa.newkeys(bits)

    return public_key.save_pkcs1("PEM"), private_key.save_pkcs1("PEM")


def encrypt_message(message, public_key: bytes) -> bytes:
    
    pk = rsa.PublicKey.load_pkcs1(public_key)
    encrypted_message = rsa.encrypt(message.encode(), pk)

    return encrypted_message


def decrypt_message(encrypted_message: bytes, private_key: bytes) -> str:

    sk = rsa.PrivateKey.load_pkcs1(private_key)
    decrypted_message = rsa.decrypt(encrypted_message, sk).decode()

    return decrypted_message

def pk_user(user_id: int, bits, db=None) -> tuple[bytes, bytes]:
    # Use provided db connection or create a new one for thread safety
    if db is None:
        db = sqlite3.connect("database.db")
        local_cursor = db.cursor()
        should_close = True
    else:
        local_cursor = db.cursor()
        should_close = False

    try:
        local_cursor.execute(
            """
            SELECT 1
            FROM rsaKey
            WHERE utilizador_id = ?
            LIMIT 1
            """,
            (user_id,),
        )

        if local_cursor.fetchone() is not None:
            public_key = local_cursor.execute(
                """
                SELECT pkRsa
                FROM rsaKey
                WHERE utilizador_id = ?
                """,
                (user_id,),
            ).fetchone()[0]
            return public_key, None

        public_key, private_key = generate_keys(bits)
        local_cursor.execute(
            """
            INSERT INTO rsaKey (utilizador_id, pkRsa)
            VALUES (?, ?)
            """,
            (user_id, public_key),
        )
        db.commit()

        return public_key, private_key
    finally:
        if should_close:
            db.close()
