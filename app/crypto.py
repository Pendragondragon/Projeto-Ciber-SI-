import hashlib
import os
from dotenv import load_dotenv

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

load_dotenv()

def HMAC_authentication(hmac_hash, cryptogram):
    #buscar a chave de integridade
    INTEGRITY_KEY = os.getenv("HMAC_INTEGRITY_KEY")
    #buscar o tamanho do bloco do algoritmo
    if hmac_hash == "hmac_sha256":
        block_size = 64
        hash_func = hashlib.sha256
    else:
        block_size = 128
        hash_func = hashlib.sha512

    #por para bytes
    key = INTEGRITY_KEY.encode()

    #verificar se a chave tem o tamanho necessario
    if len(INTEGRITY_KEY) > block_size:
        key = hash_func(INTEGRITY_KEY).digest()
    elif len(INTEGRITY_KEY) < block_size:
        #encher com zeros ate ao tamanho desejado
        key = key.ljust(block_size, b'\x00')

    #criar os pads
    ipad = bytes((x ^ 0x36) for x in key)
    opad = bytes((x ^ 0x5c) for x in key)

    #pad interior
    inner_pad = hash_func(ipad + cryptogram).digest()
    #resultado
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

    if sig_hash == "sig_sha256":
        hash_func = hashes.sha256()
    else:
        hash_func = hashes.sha512()

    signature = sk.sign(
        message,
        #pega na mensagem adiciona o salt(valor rand), e mistura tudo com uma funcao
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

    if sig_hash == "sig_sha256":
        hash_func = hashes.SHA256()
    else:
        hash_func = hashes.SHA512()

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
