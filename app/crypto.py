import hashlib
import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidKey

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
        padding.PSS(
            mgf=padding.MGF1(hash_func),
            salt_length=padding.PSS.MAX_LENGTH
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
            padding.PSS(
                mgf=padding.MGF1(hash_func),
                salt_length=padding.PSS.MAX_LENGTH
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