from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import os
import sys
import json
from user import User

def welcome() -> bool:
        """Print the welcome text to user"""
        # Print messages
        print("Welcome to Secure Exchange, where you can send files securely to other users! Please either login or register. You can type 'quit' to quit the program.\n")
        print("To login, use the following command: 'login <username> <password>' with no quotes and replacing <username> with your username and <password> with your password.\n")
        print("To register, use the following command: 'register <username> <password>' with no quotes and replacing <username> with your desired username and <password> with your desired password.\n")
        print("Type 'register help' to see specifc username and password requirements.\n")
        print("A note to anyone using this program: this is a practice encryption program by me, so I cannot guarantee actual security on anything you send/receive.\n")

        userAnswer = input("Please login, register, or quit to continue: ")
        return __parseWelcome(userAnswer)

def __parseWelcome(cmd) -> bool:
    # Parse user input
    parsedCmd = cmd.split(" ")

    # Check for keywords 'register' or 'login' and execute accordingly
    if len(parsedCmd) == 2 and parsedCmd[0] == "register" and parsedCmd[1] == "help":
        outcome = __registerHelp()
    elif parsedCmd[0] == "register" and len(parsedCmd) == 3:
        outcome = __register(parsedCmd[1], parsedCmd[2])
    elif parsedCmd[0] == "login" and len(parsedCmd) == 3:
        outcome = __login(parsedCmd[1], parsedCmd[2])
    elif parsedCmd[0] == "admin":
        outcome = __admin()
    elif parsedCmd[0] == "quit":
        print("Goodbye!")
        sys.exit()
    else:
        print("Invalid command, try again.")
        outcome = False
    
    return outcome

def __login(user, pwd) -> bool:
    """Allow users to login to the system"""
    ### TESTING ###
    infoDir = "%s/test_files/%s/userInfo.json" % (os.getcwd(), user)
    f = open(infoDir, "r")
    userInfo = json.load(f)
    f.close()

    if userInfo["password"] == pwd:
        print("Successful login!")
        return User(userInfo["username"])
    else:
        print("Bad password")
        return False

def __register(user, pwd) -> bool:
    """Allow users to register with the system"""
    ### FOR TESTING ###
    userInfo = {
        "username": user,
        "password": pwd,
        "files": []
    }
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
    print("Saving your keys...")

    # Create keys directory
    ### FOR TESTING ###
    test = input("Save profile? y/n: ")
    userDirectory = os.getcwd()
    if test == "y":
        userDirectory = "%s/test_files/%s" % (userDirectory, user)
        keysDir = "%s/keys" % userDirectory
        # Make user directory
        try:
            os.mkdir(userDirectory)
        except FileExistsError:
            print("Error making user directory")
            print(sys.exc_info[0])
    
        # Save user info
        infoDir = "%s/userInfo.json" % userDirectory
        f = open(infoDir, "w")
        json.dump(userInfo, f)
        f.close()
    else:
        keysDir = "%s/keys" % userDirectory
    
    try:
        os.mkdir(keysDir)
    except FileExistsError:
        # Don't make the directory
        pass

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

    ### FOR TESTING ONLY -- someday just send the public key to the database ###
    # Write public key
    pubPem = userPublicKey.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    publicDirectory = "%s/publicKey.pem" % keysDir
    f = open(publicDirectory, "wb")
    f.write(pubPem)
    f.close()

    print("Your private key has been saved. DO NOT LOSE THIS KEY. If you lose your private key you must re-register with the system and lose any messages or files that have been sent to you.")
    print("Your registration is successful! You may now login.")
    print("\n")

    return False

def __admin() -> bool:
    """This is only for testing, it MUST be deleted after deployment"""
    print("Success! Logged in as admin")
    return True

def __registerHelp() -> bool:
    print("Username requirements: 16 characters or less.")
    print("Password requirements: 32 characters or less.")
    return False