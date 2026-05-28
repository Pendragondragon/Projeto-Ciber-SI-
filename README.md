# SAFE-DEPOSIT-BOX
SAFE-DEPOSIT-BOX was developed as the pratical project for the Cybersecurity subject at Universidade da Beira Interior (UBI).<br>
This project provides a web application where users can securely store messages in an encrypted state, being able to choose between several cypher modes. The system ensures confidentially, integrity, and authenticity by utilizing multiple cryptographic standards. Users can retrieve their messages later by providing cryptographic codes they generated earlier.

### Core Features

This application has some core features that are important to mention since they share strong concepts of user's messages and data security. 

####  Encrypthion Methods
 * Symmetric Encryption ([AES-256-CBC](https://en.wikipedia.org/wiki/AES_implementations))
 * Password-based Derivation ([Secure KDF](https://en.wikipedia.org/wiki/Key_derivation_function))
 * Asymmetric Encryption ([RSA](https://en.wikipedia.org/wiki/RSA_cryptosystem))

####  Security and Integrity
 * [HMAC-SHA256](https://en.wikipedia.org/wiki/HMAC): Ensures message integrity for all stored cryptograms.
 *  Digital Signatures: All plaintext messages are signed before encryption to ensure authenticity.

####  Verification
 * Integrity and authenticity are checked automatically, whenever a vault is opened.

### Advanced Features
 * Algorithm Flexibility: Support for [AES-256-CBC](https://en.wikipedia.org/wiki/AES_implementations), [ChaCha20](https://wiki.tcl-lang.org/page/ChaCha20) and selectable hash functions such as [SHA256/SHA512](https://en.wikipedia.org/wiki/Secure_Hash_Algorithms)
 * Customizable Parameters: Options to configurate [RSA](https://en.wikipedia.org/wiki/RSA_cryptosystem) key sizes and hash functions.

### Technical Stack
 * Encryption: [AES-256-CBC](https://en.wikipedia.org/wiki/AES_implementations), [RSA](https://en.wikipedia.org/wiki/RSA_cryptosystem)
 * Integrity/Signing: [HMAC-SHA256](https://en.wikipedia.org/wiki/HMAC), Digital Signatures.  
 * Environment: Designed for local deployment and prototyping.

### How It Works?
 * Deposit: User inputs a message → System encrypts and signs → Keys/Credentials are provided to the user.
 * Verify: The system stores an [HMAC-SHA256](https://en.wikipedia.org/wiki/HMAC) for every vault to detect tampering.
 * Retrieve: User provides the key/password → System verifies integrity → Message is decrypted and displayed.
---

##  Technologies and Prerequisites

####  Instalations
Before starting this application, make sure of having the following tools installed:
  * cryptography
  * flask
  * flask-bcrypt
  * flask-mail
  * jupyter
  * matplotlib
  * notebook
  * numpy
  * pandas
  * pyjwt
  * python 3.13.12
  * python-dotenv
  * rsa
  * sqlalchemy
  * sqlite
  * sqlite-utils


####  Environment Creation
To create an environment in [Visual Studio Code](https://code.visualstudio.com/) follow the following steps:
```bash
$ python -m venv .venv
$ source "PATH/.venv/bin/activate"
```
Then press ctrl + shift + P,<br>
Later, select the option Python: Select Interpreter<br>
Later, choose Python (.venv)<br>
Once those steps are finished, you have an environment created to suport this project.


####  Tools and Frameworks
There were also used the following tools and frameworks:
 * [tailwind](https://tailwindcss.com/plus/ui-blocks/application-ui/forms/form-layouts)

---
## Test Credentials Already Created

There were created some credential when testing the developed web application

---
## Iniciating the Application
