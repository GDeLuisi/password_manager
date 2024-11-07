from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
from hashlib import sha512

def pad(string:str) -> str:
    if len(string)%32 == 0:
        return  string
    return str("".join(["0" for i in range(32-len(string))]))+string

def encrypt(key:str,string:str)-> str:
    fernet = Fernet(key=urlsafe_b64encode(pad(key).encode()))
    return fernet.encrypt(string.encode()).decode("utf-8")

def decrypt(key:str,string:str)->str:
    fernet = Fernet(key=urlsafe_b64encode(pad(key).encode()))
    return fernet.decrypt(string.encode()).decode("utf-8")

def generate_key()->str:
    return Fernet.generate_key().decode()

def generate_master_key(key:str,secret:str):
    mk=urlsafe_b64encode(f"{secret}:{key}".encode())
    return sha512(mk).hexdigest()