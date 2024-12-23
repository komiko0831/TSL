import re
from Crypto.Util.number import getPrime
from Crypto.Cipher import AES
from random import randint
from math import gcd,sqrt
from hashlib import sha256

# 工具函数
def get_key():
    p = getPrime(1024)
    q = getPrime(1024)
    n = p * q
    e = 65537
    phi  = (p-1)*(q-1)
    d = pow(e,-1,phi)
    return d,e

def pad_message(msg):
    """
    补齐消息以适应 AES 加密
    """
    while len(msg) % 16 != 0:
        msg += " "
    return msg.encode()

def get_hash(message_string):
    """
    计算哈希函数
    """
    return sha256(message_string.encode('utf-8')).hexdigest()


# AES
def aes_encrypt(key, msg):
    """
    AES加密
    """
    aes = AES.new(key.to_bytes(16, 'big'), AES.MODE_ECB)
    return aes.encrypt(pad_message(msg))


def aes_decrypt(key, en_msg):
    """
    AES解密
    """
    aes = AES.new(key.to_bytes(16, 'big'), AES.MODE_ECB)
    return aes.decrypt(en_msg).decode().strip()


# GM
def is_quad_residue(a, p):
    """
    欧拉准则判定是否为二次剩余
    """
    if a % p == 0:
        return False
    return pow(a, (p - 1) // 2, p) == 1


def generate_key():
    """
    生成GM算法密钥对
    """
    p = getPrime(666)
    q = getPrime(666)
    n = p * q
    x = 2
    while is_quad_residue(x, p) or is_quad_residue(x, q):
        x += 1
    return (n, x), (p, q)


def m_to_binary(s):
    """
    将字符串转换为连续的二进制字符串
    """
    binary_m = ''.join([bin(ord(c))[2:].zfill(8) for c in s])
    return binary_m


def GM_encrypt(message, public_key):
    """
    GM概率加密
    """
    n, x = public_key
    encrypt = []
    for bit in message:
        r = randint(1, n - 1)
        while gcd(r, n) != 1:
            r = randint(1, n - 1)

        if bit == '1':
            c = (r ** 2 * x) % n
        else:
            c = (r ** 2) % n
        encrypt.append(c)

    return encrypt


def GM_decrypt(c, private_key):
    """
    GM解密:将密文解密为二进制字符串
    """
    p, q = private_key
    decrypt = ""
    for i in c:
        if is_quad_residue(i, p) and is_quad_residue(i, q):
            decrypt += "0"
        else:
            decrypt += "1"
    return decrypt


def binary_to_m(binary_str):
    """
    将连续的二进制字符串转换为原始字符串
    """
    grouped_bits = [binary_str[i:i + 8] for i in range(0, len(binary_str), 8)]
    msg = ''.join([chr(int(bits, 2)) for bits in grouped_bits])
    return msg


# Diffie-Hellman 密钥交换
def generate_prime():
    """
    生成一个大素数p
    """
    prime = 0
    while not is_prime(prime):
        prime = randint(2 ** 20, 2 ** 21)
    return prime


def is_prime(n):
    """
    判断一个数是否为素数
    """
    if n <= 1:
        return False
    for i in range(2, int(sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def generate_primitive_root(p):
    """
    判断一个数是否为素数
    """
    for g in range(2, p):
        if is_primitive_root(g, p):
            return g
    return None


def is_primitive_root(g, p):
    """
    判断一个数是否为原根
    """
    if not is_prime(p):
        return False
    phi = p - 1
    factors = prime_factors(phi)
    for factor in factors:
        if pow(g, phi // factor, p) == 1:
            return False
    return True


def prime_factors(n):
    """
    计算一个数的素因子
    """
    factors = []
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    i = 3
    while i <= sqrt(n):
        if n % i == 0:
            factors.append(i)
            n //= i
        else:
            i += 2
    if n > 1:
        factors.append(n)
    return factors

#生成DH参数
p = generate_prime()
g = generate_primitive_root(p)


def generate_private_key():
    return randint(1000000, 10000000000)

def exchange_key(private_key):
    y = pow(g,private_key,p)
    return y

def shared_key(private_key, public_key):
    return pow(public_key, private_key, p)


# 综合加解密流程
def process_message(key,message):
    # 提取字母和数字部分及其原始顺序
    tokens = re.findall(r'[a-zA-Z]+|\d+', message)
    token_types = ["letter" if token.isalpha() else "number" for token in tokens]
    """
    # DH 协商 AES 密钥
    private_key_a = generate_private_key()
    private_key_b = generate_private_key()

    public_key_a = pow(g, private_key_a, p)
    public_key_b = pow(g, private_key_b, p)

    shared_key_a = shared_key(private_key_a, public_key_b)
    shared_key_b = shared_key(private_key_b, public_key_a)

    assert shared_key_a == shared_key_b, "密钥协商失败"
    aes_key = shared_key_a
    """

    # GM 密钥对
    public_key, private_key = generate_key()

    # 加密
    encrypted_tokens = []
    for token, token_type in zip(tokens, token_types):
        if token_type == "letter":
            encrypted_tokens.append(aes_encrypt(key, token))
        else:
            encrypted_tokens.append(GM_encrypt(m_to_binary(token), public_key))

    # 解密
    decrypted_tokens = []
    for token, token_type in zip(encrypted_tokens, token_types):
        if token_type == "letter":
            decrypted_tokens.append(aes_decrypt(key, token))
        else:
            decrypted_binary = GM_decrypt(token, private_key)
            decrypted_tokens.append(binary_to_m(decrypted_binary))

    # 还原消息
    encrypted_message = encrypted_tokens  # 加密后的消息
    decrypted_message = " ".join(decrypted_tokens)  # 解密后的消息

    return encrypted_message, decrypted_message


# 测试消息
"""
message = "Dday landing month 6 month 6 year 1944"
encrypted, decrypted = process_message(message)

print("原始消息:", message)
print("加密后的消息: [略]")
print("解密后的消息:", decrypted)
"""

# 参数
N = 7  # 多项式大小
P = 2  # 私钥模数
Q = 29  # 消息模数

poly_h = [23, 23, 23, 24, 23, 24, 23]  # 公钥 h
poly_f = [1, 1, 1, 0, 1, 1, 0]         # 私钥 f
poly_m = [1, 3, 2, 0, 1, 3, 0]         # 明文消息 m
poly_r = [1, 1, 0, 1, 0, 0, 1]         # 随机多项式 r

# 加密函数
def encrypt():
    # r * P 后，使用公钥 h 加密消息
    temp_r = [(P * r) % Q for r in poly_r]
    poly_cipher = [(temp_r[i] * poly_h[i] + poly_m[i]) % Q for i in range(N)]
    return poly_cipher

# 解密函数
def decrypt(poly_cipher):
    # 使用私钥 f 解密
    decrypt_m = [(poly_f[i] * poly_cipher[i]) % Q for i in range(N)]
    # 调整范围到 -Q/2 到 Q/2
    half_Q = Q // 2
    for i in range(N):
        if decrypt_m[i] > half_Q:
            decrypt_m[i] -= Q
        elif decrypt_m[i] < -half_Q:
            decrypt_m[i] += Q
    return decrypt_m

# 签名生成函数
def sign(message):
    # 加密消息
    poly_cipher = encrypt()
    # 使用私钥计算签名
    signature = [(poly_f[i] * poly_cipher[i]) % P for i in range(N)]
    return signature

# 签名验证函数
def verify(signature):
    # 解密加密后的多项式
    poly_cipher = encrypt()
    decrypt_m = decrypt(poly_cipher)
    # 检查解密消息是否与签名一致
    expected_signature = [(poly_f[i] * poly_cipher[i]) % P for i in range(N)]
    return signature == expected_signature

# 测试
if __name__ == "__main__":
    # 加密
    cipher = encrypt()
    print("Cipher:", cipher)

    # 解密
    decrypted_message = decrypt(cipher)
    print("Decrypted message:", decrypted_message)

    # 签名
    signature = sign(poly_m)
    print("Signature:", signature)

    # 验证签名
    is_valid = verify(signature)
    print("Signature valid:", is_valid)
