# Python imports
import socket
import hashlib
import os
import sys

# Crypto imports
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# Methods for user to send information to server
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8008

USERS = "%s/local_users" % os.getcwd()

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

    # Handshake with server and get public key
    serverKey = __handshake(sock)

    # Error in packets
    if serverKey == False:
        return False, "Error communicating to server."

    # Craft AUTH packet
    msg = ("AUTH,%s,%s" % (user, pwd))

    # Encrypt packet with server's RSA key
    msgEnc = __encryptRSA(msg, serverKey)

    # Send AUTH packet
    sock.sendall(msgEnc)

    # Receive AUTH response
    resp = sock.recv(1024)

    # Decrypt AUTH response
    decResp = __decryptRSA(resp, user).decode('utf-8')

    # Parse response
    parsedResp = decResp.split(",")

    if parsedResp[0] == "OK":
        sessionKey = parsedResp[1].encode('utf-8')
    else:
        return False, "Bad username or password"

    # Save session key for user
    try:
        with open("%s/%s/keys/session_key.key" % (USERS, user), "wb") as f:
            f.write(sessionKey)
            f.close()
    except:
        return False, "Error saving session key."

    return True, "Successful login!"

def reg(user, pwd, key):
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
    msgEnc = __encryptRSA(msg, serverKey)

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

    # Check correct response
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

    # Convert key to bytes
    key = key.encode('utf-8')
    print(key)

    # Hash new key
    new = hashlib.sha256()
    new.update(key)

    # Hash old key
    existing = hashlib.sha256()
    
    try:
        with open("%s/serverKey.pem" % os.getcwd(), "rb") as f:
            existingBytes = f.read()
            f.close()
        
        existing.update(existingBytes)

        # Compare hash of new key and old key to see if key has been updated
        keyUpdated = new.digest() != existing.digest()
    except FileNotFoundError:
        # No key found
        keyUpdated = True

    if keyUpdated:
        print("Updated key")

        # Save new key
        with open("%s/serverKey.pem" % os.getcwd(), "wb") as f:
            f.write(key)
            f.close()
    else:
        print("Key not updated")

    # Load and return key
    with open("%s/serverKey.pem" % os.getcwd(), "rb") as f:
        keyToReturn = serialization.load_pem_public_key(f.read(), backend=default_backend())
        f.close()

    return keyToReturn

def __encryptRSA(msg, key):
    """Encrypts message with RSA key

            Parameters:
                msg (str): message to be sent
                key (_RSAPublicKey): key to encrypt with
            
            Returns:
                Encrypted message
    """
    # Convert message to bytes
    msg = msg.encode('utf-8')
    return key.encrypt(
        msg,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def __decryptRSA(msg, user):
    """Decrypts message with RSA key

            Parameters:
                msg (str): message to be sent
                user (str): user with key to use
            
            Returns:
                Decrypted message
    """
    # Load user's private key
    try:
        with open("%s/%s/keys/privateKey.pem" % (USERS, user), "rb") as f:
            privateKey = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
            f.close()
    except:
        print("Error opening user's private key")
        print(sys.exc_info())
        return None
    
    # Decrypt message
    return privateKey.decrypt(
        msg, 
        padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
    )