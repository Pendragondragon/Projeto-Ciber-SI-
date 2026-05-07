import hashlib
import os
from dotenv import load_dotenv

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

def assinar_digitalmente(sig_hash, message):
    print()