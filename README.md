# SAFE-DEPOSIT-BOX
This project provides a web application where users can securely store messages in an encrypted state, being able to choose between several cypher modes. The system ensures confidentially, integrity, and authenticity by utilizing multiple cryptographic standards. Users can retrieve their messages later by providing cryptographic codes they generated earlier.

### Core Features

This application has some core features that are important to mention since they share strong concepts of user's messages and data security. 

####  Encrypthion Methods
 * Symmetric Encryption ([AES-256-CBC](https://en.wikipedia.org/wiki/AES_implementations))
 * Password-based Derivation ([Secure KDF](https://en.wikipedia.org/wiki/Key_derivation_function))
 * Asymmetric Encryption ([RSA](https://en.wikipedia.org/wiki/RSA_cryptosystem))
---

##  Technologies and Prerequisites
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


To create an environment in [Visual Studio Code](https://code.visualstudio.com/) follow the following steps:
```bash
$ python -m venv .venv
$ source "PATH/.venv/bin/activate"
```
Then press ctrl + shift + P,<br>
Later, select the option Python: Select Interpreter<br>
Later, choose Python (.venv)
Once those steps are finished, you have an environment created to suport this project.

There were also used the following tools and frameworks:
 * [tailwind](https://tailwindcss.com/plus/ui-blocks/application-ui/forms/form-layouts)

---
## Test Credentials Already Created

There were created some credential when testing the developed web application

---
## Iniciating the Application
