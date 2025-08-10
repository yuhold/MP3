import os
import binascii # 用于将字节串转换为十六进制字符串

# 生成24个字节的随机数据，对于Flask的SECRET_KEY来说是一个推荐的长度
random_bytes = os.urandom(24)

# 将字节数据转换为十六进制字符串，方便在INI文件中存储和复制
secret_key = binascii.hexlify(random_bytes).decode('utf-8')

print(f"为您生成的 SECRET_KEY: {secret_key}")
print("\n请将此字符串复制到 server_config.ini 文件中的 [FLASK_APP] -> SECRET_KEY 配置项。")
print("例如：SECRET_KEY = " + secret_key)
