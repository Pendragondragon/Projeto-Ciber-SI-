import rsa
import sqlite3

# public_key, private_key = rsa.newkeys(1024)

# with open("pkteste.pem", "wb") as f:
#     f.write(public_key.save_pkcs1("PEM"))

# with open("skteste.pem", "wb") as f:
#     f.write(private_key.save_pkcs1("PEM"))


# with open("pkteste.pem", "rb") as f:
#     public_key = rsa.PublicKey.load_pkcs1(f.read())

# with open("skteste.pem", "rb") as f:
#     private_key = rsa.PrivateKey.load_pkcs1(f.read())

# message = "Olá, esta é uma mensagem secreta!"

# encrypted_message = rsa.encrypt(message.encode(), public_key)
# print("Mensagem cifrada:", encrypted_message)


# with open("encrypted_message.bin", "wb") as f:
#     f.write(encrypted_message)

# encrypted_message = open("encrypted_message.bin", "rb").read()

# clear_mensagem = rsa.decrypt(encrypted_message, private_key).decode()
# print("Mensagem decifrada:", clear_mensagem)


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


public_key, private_key = generate_keys(1024)

# print(public_key)

# message = "Olá, esta é uma mensagem secreta!"

# encrypted_message = encrypt_message(message, public_key)

# print("Mensagem cifrada:", encrypted_message)

# decrypted_message = decrypt_message(encrypted_message, private_key)

# print("\nMensagem decifrada:", decrypted_message)
    

connection = sqlite3.connect("database.db")
cursor = connection.cursor()


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



# public_key, private_key = generate_keys(1024)
# print("Private Key:\n", private_key)
# private_key_encoded = private_key.decode("utf-8")
# print("\n\nPrivate Key decode:\n", private_key_encoded)

# e = encrypt_message("Olá, esta é uma mensagem secreta!", public_key)

# d = decrypt_message(e, private_key_encoded.encode("utf-8"))


# print("\n\nDecrypted message:\n", d)

