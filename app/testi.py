from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

password = "user123"

print(password_hash.hash(password))