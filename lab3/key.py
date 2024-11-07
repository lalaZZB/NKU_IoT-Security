from cryptography.fernet import Fernet

# 生成随机密钥
encryption_key = Fernet.generate_key()
print(encryption_key)
