import socket
import hashlib
import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# Methods for user to send information to server
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8008

def auth(user, pwd):
    """Authenticate user to server
    
        Parameters:
            user (str): username
            pwd (str): password

        Returns:
            True if authenticated, False if bad auth
    """
    # Connect to server
    sock = __connect()

    # Craft HELLO packet
    msg = "0,0,HELLO,SecureClient,<checksum>".encode('utf-8')
    
    # Send packet
    sock.sendall(msg)

    # Wait for server's key
    resp = sock.recv(1024).decode('utf-8')

    try:
        # Extract the key from server message
        dirtyKey = resp[4]
    except IndexError:
        print("Bad key message")
        return False

    key = __clean_key(dirtyKey)

    # Craft AUTH packet
    msg = ("1,1,AUTH,%s,%s,<checksum>" % (user, pwd)).encode('utf-8')

    # Encrypt packet
    msgEnc = key.encrypt(
        msg,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Send AUTH packet
    sock.sendall(msgEnc)

    # Receive AUTH confirmation
    resp = sock.recv(1024)
    
def send():
    pass

def receive():
    pass

def __connect():
    """Connects user to server

        Returns:
            connected socket
    """
    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect socket to server
    sock.connect((SERVER_IP, SERVER_PORT))

    # Return connected socket
    return sock

def __checksum():
    pass

def __clean_key(key):
    keyUpdated = False

    key = key.encode('utf-8')

    # Hash new key
    new = hashlib.sha256()
    new.update(key)

    # Hash old key
    existing = hashlib.sha256()
    
    try:
        with open("%s/serverInfo.pem" % os.getcwd(), "rb") as f:
            existingBytes = f.read()
            f.close()
        
        existing.update(existingBytes)

        keyUpdated = new.digest() != existing.digest()
    except FileNotFoundError:
        # No key found
        keyUpdated = True

    if keyUpdated:
        print("Updated key")
        # Save new key
        with open("%s/serverInfo.pem" % os.getcwd(), "wb") as f:
            f.write(key)
            f.close()
    else:
        print("Key not updated")

    # Load and return key
    with open("%s/serverInfo.pem" % os.getcwd(), "rb") as f:
        keyToReturn = serialization.load_pem_public_key(f.read())
        f.close()

    return keyToReturn