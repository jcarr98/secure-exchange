from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import os
import sys
import json
from user import User
import serverconnect

def print_welcome() -> None:
        """Print the welcome text to user"""
        # Print messages
        print("Welcome to Secure Exchange, where you can send files securely to other users! Please either login or register. You can type 'quit' to quit the program.\n")
        print("To login, use the following command: 'login <username> <password>' with no quotes and replacing <username> with your username and <password> with your password.\n")
        print("To register, use the following command: 'register <username> <password>' with no quotes and replacing <username> with your desired username and <password> with your desired password.\n")
        print("Type 'register help' to see specifc username and password requirements.\n")
        print("A note to anyone using this program: this is a practice encryption program by me, so I cannot guarantee actual security on anything you send/receive.\n")

def login(user, pwd) -> bool:
    """Allow users to login to the system"""
    ### TESTING ###
    infoDir = "%s/local_users/%s/userInfo.json" % (os.getcwd(), user)
    f = open(infoDir, "r")
    userInfo = json.load(f)
    f.close()

    if userInfo["password"] == pwd:
        return User(userInfo["username"]), "Successful login!"
    else:
        return None, "Bad username or password"

def register(user, pwd) -> bool:
    """Allow users to register with the system

            Parameters:
                user (str): username
                pwd (str): password

            Returns:
                True if registration is successful, False if not
    """

    print("Thank you for registering with the system! There are just a few more steps...")
    print("Generating private RSA key...")
    userPrivateKey = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    print("Success! Private key created.")
    print("Generating public RSA key...")
    userPublicKey = userPrivateKey.public_key()
    print("Success! Public key created.")

    # Attempt to register with system
    registered = serverconnect.register(user, pwd, userPublicKey)

    # If successful registration, save user information to local system
    if registered:
        # Create keys directory
        ### FOR TESTING ###
        userDirectory = "%s/local_users/%s" % (os.getcwd(), user)
        keysDir = "%s/keys" % userDirectory
        # Make user directory
        try:
            os.mkdir(userDirectory)
        except FileExistsError:
            return None, "Username in use"

        print("Saving your info...")
        # Create user info
        userInfo = {
            "username": user,
            "password": pwd
        }
        # Save user info
        infoDir = "%s/userInfo.json" % userDirectory
        f = open(infoDir, "w")
        json.dump(userInfo, f)
        f.close()
        
        try:
            os.mkdir(keysDir)
        except:
            # Don't make the directory
            return None, "Error creating keys directory."

        print("Saving your keys...")
        # Write private key
        prvPem = userPrivateKey.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        privateDirectory = "%s/privateKey.pem" % keysDir
        f = open(privateDirectory, "wb")
        f.write(prvPem)
        f.close()

        print("Your private key has been saved. DO NOT LOSE THIS KEY. If you lose your private key you must re-register with the system and lose any messages or files that have been sent to you.")
        print("Your registration is successful!")
        print("\n")
        return User(userInfo["username"]), "Successfully registered!"
    else:
        return None, "Failed to register with the system. Please try again."

def print_help() -> None:
    print("To register, types 'register <username> <password>', replacing <username> with your desired username and <password> with your desired password.")
    print("Username requirements: 16 characters or less.")
    print("Password requirements: 32 characters or less.")
    
    print("\n")
    
    print("To login, type 'login <username> <password>', replacing <username> with your username and <password> with your password.")