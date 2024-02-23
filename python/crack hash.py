import hashlib
import base64
import os
class texttohash:
    def __init__(self, hash_type="SHA", pbkdf2_iterations=10000):
        self.hash_type=hash_type
        self.pbkdf2_iteration=pbkdf2_iterations
    def crypt_bytes(self, salt, value):
        if not salt:
            salt=base64.urlsafe_b64encode(os.urandom(16)).decode('utf-8')
        hash_obj=hashlib.new(self.hash_type)
        hash_obj.update(salt.encode('utf-8'))
        hash_obj.update(value)
        hashed_bytes=hash_obj.digest()
        result=f"${self.hash_type}${salt}${base64.urlsafe_b64encode(hashed_bytes).decode('utf-8').replace('+', '.')}"
        return result
    def get_crypted_bytes(self, salt, value):
        try:
            hash_obj=hashlib.new(self.hash_type)
            hash_obj.update(salt.encode('utf-8'))
            hash_obj.update(value)
            hashed_bytes=hash_obj.digest()
            return base64.urlsafe_b64decode(hashed_bytes).decode('utf-8').replace('+', '.')
        except hashlib.NoSuchAlgorithmException as e:
            raise Exception(f"there is error happended : ( {self.hash_type}: {e})")

hash_t="SHA1"
salt="d"
target_hash="$SHA1$d$uP0_QaVBpDWFeo8-dRzDqRwXQ2I="
wordlist='/usr/share/wordlist/rockyou.txt'
encryptor=texttohash(hash_t)
total_lines=sum(1 for _ in open(wordlist, 'r', encoding='latin-1'))
with open(wordlist, 'r', encoding='latin-1') as password_list:
    for password in password_list:
        value=password.strip()
        hashed_password = encryptor.crypt_bytes(salt, value.encode('utf-8'))
        if hashed_password == target_hash:
            print(f'found the pw: {value}, hash:{hashed_password}')
            break