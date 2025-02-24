import base64
import hashlib
import hmac
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def decrypt_token(encrypted_token, iv, WEBHOOK_SECRET):
    """Decrypt API token using WEBHOOK_SECRET as the key."""
    # Generate the key from WEBHOOK_SECRET in the same way as the GitHub Action
    key = hashlib.sha256(WEBHOOK_SECRET.encode()).hexdigest()
    key_bytes = bytes.fromhex(key)
    iv_bytes = bytes.fromhex(iv)
    
    # Base64 decode the encrypted token
    encrypted_data = base64.b64decode(encrypted_token)
    
    # Create cipher and decrypt
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
    decrypted_bytes = cipher.decrypt(encrypted_data)
    
    # Handle padding properly
    try:
        unpadded = unpad(decrypted_bytes, AES.block_size)
    except ValueError:
        # If unpadding fails, try to find the null termination
        if b'\x00' in decrypted_bytes:
            unpadded = decrypted_bytes[:decrypted_bytes.index(b'\x00')]
        else:
            unpadded = decrypted_bytes
            
    return unpadded.decode('utf-8')


def verify_signature(secret, body, signature):
    """Verify GitHub webhook signature using HMAC-SHA256."""
    mac = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    expected_signature = f"sha256={mac}"
    return hmac.compare_digest(expected_signature, signature)