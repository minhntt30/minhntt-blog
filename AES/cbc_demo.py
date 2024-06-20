from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def aes_cbc_encrypt(plaintext, key):
    print("-"*20, "ECRYPTION", "-"*20)
    # 1. Initialization
    iv = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    print(f"iv: {iv.hex()}")

    # 2. Padding
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_plaintext = padder.update(plaintext) + padder.finalize()
    print(f"Padded plaintext: {padded_plaintext}")

    # 3. Encryption
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()

    # 3.1 Divide padded plaintext into blocks
    block_size = 16
    blocks = [padded_plaintext[i:i+block_size] for i in range(0, len(padded_plaintext), block_size)]
    print([block for block in blocks])

    # 3.2 XOR first block with IV
    xored_block = bytes([a ^ b for a, b in zip(blocks[0], iv)])
    print(f"XOR result: {xored_block.hex()}")

    # 3.3 Encrypt blocks
    encrypted_blocks = []
    encrypted_blocks.append(encryptor.update(xored_block))
    for block in blocks[1:]:
        encrypted_blocks.append(encryptor.update(block))
    encrypted_blocks.append(encryptor.finalize())
    for idx, block in enumerate(encrypted_blocks):
        print(f"Block {idx}: {block.hex()}" )

    # Ciphertext
    ciphertext = b"".join(encrypted_blocks)
    # print(f"Ciphertext (including IV): {iv + ciphertext}")
    return ciphertext

def aes_cbc_decrypt(ciphertext, key):
    print("-"*20, "DECRYPTION", "-"*20)
    
    # 1. Initialization
    iv = ciphertext[:16]  # Extract the IV from the ciphertext
    print(f"iv: {iv.hex()}")

    # 2. Decryption
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()

    # 2.1 Divide ciphertext into blocks
    block_size = 16
    blocks = [ciphertext[i:i+block_size] for i in range(0, len(ciphertext), block_size)]
    for idx, block in enumerate(blocks):
        print(f"Block {idx}: {block.hex()}")

    # 2.2 Decrypt first block then xor with IV
    decrypted_blocks = []
    first_block = decryptor.update(blocks[0])
    xored_block = bytes([a ^ b for a, b in zip(first_block, iv)])
    print(f"XOR result: {xored_block.hex()}")
    decrypted_blocks.append(xored_block)

    # 2.3 Decrypt rest blocks
    for block in blocks[1:]:
        decrypted_blocks.append(decryptor.update(block))
    decrypted_blocks.append(decryptor.finalize())  # Include the final block
    for idx, decrypted_block in enumerate(decrypted_blocks):
        print(f"Block {idx}: {decrypted_block}")

    # 3. Plaintext
    decrypted_data = b"".join(decrypted_blocks)

    # 4. Remove padding
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(decrypted_data) + unpadder.finalize()

    return plaintext

if __name__ == "__main__":
    input = b"This is a longer message that exceeds 16 bytes."
    key = b"this is my srkey"
    ciphertext = aes_cbc_encrypt(input, key)
    print(f"ciphertext: {ciphertext.hex()}")
    plaintext = aes_cbc_decrypt(ciphertext, key)
    print(f"plaintext: {plaintext}")

