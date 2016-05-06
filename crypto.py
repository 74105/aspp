import sys
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto import Random

#AES key size
AES_KEY_SIZE = 32

# Uses null character as the padding character
PADDING_VALUE = '\0'


def padAES(message):
    lacking_char_num = 16 - (len(message) % 16)
    padded_message = message + lacking_char_num * PADDING_VALUE
    return padded_message


def encryptAES(message):
    # Get a random AES_BLOCK_SIZE byte key for AES
    aes_key = Random.new().read(AES_KEY_SIZE)

    # Initialization Vector
    iv = Random.new().read(AES.block_size)

    # Create a cipher using CFB mode
    cipher = AES.new(aes_key, AES.MODE_CFB, iv)

    # Encrypt the padded message
    encrypted_msg = cipher.encrypt(padAES(message))
    encrypted_msg = iv + aes_key + encrypted_msg
    return encrypted_msg


def decryptAES(ciphertext):
    #Extract IV and AES key from the given ciphertext
    iv = ciphertext[0 : AES.block_size]
    aes_key = ciphertext[AES.block_size : AES_KEY_SIZE + AES.block_size]
    message = ciphertext[AES_KEY_SIZE + AES.block_size:]

    #Create cipher
    cipher = AES.new(aes_key, AES.MODE_CFB, iv)

    # Strip padding chars
    message = message.rstrip(PADDING_VALUE)

    #Decipher the message
    decrypted_msg = cipher.decrypt(message)
    return decrypted_msg


def getRSAKey():
    random_generator = Random.new().read
    rsa_key = RSA.generate(1024, random_generator)
    return rsa_key


def encryptRSA(message, rsa_key):
    encrypted_msg = rsa_key.encrypt(message, 32)[0]
    return encrypted_msg


def decryptRSA(ciphertext, rsa_key):
    msg = rsa_key.decrypt(ciphertext)
    return msg
