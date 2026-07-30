#!/usr/bin/env python3
"""
GitHub Secrets 加密工具
使用 PyNaCl 加密 secret 并上传到 GitHub
"""
import json
import base64
import sys
import urllib.request
import urllib.error
from nacl import encoding, public

GITHUB_TOKEN = "REMOVED_GITHUB_PAT"
REPO_OWNER = "yijiuzero"
REPO_NAME = "chat-hanbao"

def get_public_key():
    """获取 GitHub Actions 公钥"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/public-key"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return data["key"], data["key_id"]
    except urllib.error.HTTPError as e:
        print(f"Error getting public key: {e}")
        return None, None

def encrypt_secret(plaintext, public_key):
    """使用 GitHub 公钥加密 secret"""
    key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(key)
    encrypted = sealed_box.encrypt(plaintext.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def create_secret(secret_name, encrypted_value, key_id):
    """创建或更新 GitHub Secret"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/{secret_name}"
    data = json.dumps({
        "encrypted_value": encrypted_value,
        "key_id": key_id
    }).encode()
    req = urllib.request.Request(url, data=data, method="PUT", headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"✅ Secret '{secret_name}' created/updated successfully")
            return True
    except urllib.error.HTTPError as e:
        print(f"Error creating secret: {e}")
        return False

def main():
    # Step 1: Get public key
    print("[1/3] Getting GitHub Actions public key...")
    public_key, key_id = get_public_key()
    if not public_key:
        print("Failed to get public key")
        return
    
    # Step 2: Encrypt secrets
    print("[2/3] Encrypting secrets...")
    
    dockerhub_token = input("Enter your Docker Hub Access Token (or press Enter to skip): ").strip()
    
    # Step 3: Create secrets
    print("[3/3] Creating secrets...")
    
    # DOCKERHUB_USERNAME
    encrypted = encrypt_secret("yijiuzero", public_key)
    create_secret("DOCKERHUB_USERNAME", encrypted, key_id)
    
    # DOCKERHUB_TOKEN (if provided)
    if dockerhub_token:
        encrypted = encrypt_secret(dockerhub_token, public_key)
        create_secret("DOCKERHUB_TOKEN", encrypted, key_id)
    
    print("\n✅ All secrets configured!")

if __name__ == "__main__":
    main()
