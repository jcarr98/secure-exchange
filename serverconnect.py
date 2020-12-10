import socket
import hashlib
import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# Methods for user to send information to server
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8009

def register(user, pwd, key):
    """Registers user with system

            Parameters:
                user (str): username
                pwd (str): password
                key (bytes): user's public RSA key

            Returns:
                True if successful, False if not
    """

    # Connect to server
    sock = __connect()
    serverKey = __handshake(sock)

    # Check successful key response
    if serverKey == False:
        return False

    # Convert user key to bytes
    key = key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Craft register message
    msg = ("REGISTER,%s,%s" % (user, pwd))

    # Encrypt with server's RSA key
    msgEnc = __encrypt(msg, serverKey)

    # Send REGISTER packet
    sock.sendall(msgEnc)

    # Receive confirmation, check for key request
    resp = sock.recv(1024).decode('utf-8')

    if resp == "REQ KEY":
        # Key requested
        msg = key

        # Send key to server
        print("Sending key")
        sock.sendall(msg)
    elif resp == "BAD USERNAME":
        # Username in use
        print("Username in use")
        sock.close()
        return False
    else:
        # Some other issue
        print("Unknown error")
        sock.close()
        return False
    
    # Wait for DONE
    try:
        print("waiting for DONE")
        resp = sock.recv(1024).decode('utf-8')
        sock.close()
    except ConnectionResetError:
        resp = "Connection closed"
        sock.close()
    
    parsedResp = resp.split(",")

    try:
        return parsedResp[1] == "OK"
    except IndexError:
        return False

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
    serverKey = __handshake(sock)

    if serverKey == False:
        return False

    # Craft AUTH packet
    msg = ("AUTH,%s,%s" % (user, pwd))
    print("Sending: %s" % msg)

    msgEnc = __encrypt(msg, serverKey)

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

def __handshake(sock):
    """Performs initial handshake with server and gets server's RSA
    
            Parameters:
                sock: socket connected to server

            Returns:
                Server's public RSA key
    """
    # Craft HELLO packet
    msg = "HELLO,SecureClient".encode('utf-8')
    
    # Send packet
    sock.sendall(msg)

    # Wait for server's key
    resp = sock.recv(1024).decode('utf-8')
    print(resp)
    
    # Parse response
    parsedResp = resp.split(",")

    # Check correcte response
    if parsedResp[0] != "HELLO" and parsedResp[1] != "SecureServer":
        print("Bad response")
        return False

    try:
        # Extract the key from server message
        dirtyKey = parsedResp[2]
    except IndexError:
        print("Bad key message")
        return False

    return __clean_key(dirtyKey)

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
        keyToReturn = serialization.load_pem_public_key(f.read(), backend=default_backend())
        f.close()

    return keyToReturn

def __encrypt(msg, key):
    """Encrypts message with RSA key

            Parameters:
                msg (str): message to be sent
                key (_RSAPublicKey): key to encrypt with
            
            Returns:
                Encrypted message
    """
    # Convert message to bytes
    msg = msg.encode('utf-8')
    print(msg.decode('utf-8'))
    return key.encrypt(
        msg,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )