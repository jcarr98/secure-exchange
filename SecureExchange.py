# Python imports
import sys
import os
import json
import time

# Crypto imports
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Custom imports
from secex import Exchange
from src.ext.serverconnect import ServerConnect as Server
import src.welcome as welcome

def clear():
    """Clears terminal window"""
    # Windows
    if os.name == 'nt':
        _ = os.system('cls')

    # Mac/linux
    else:
        _ = os.system('clear')


def user_exists(directory):
    # Get username
    with open("{dir}/user_info.json".format(dir=directory), "r") as f:
        info = json.loads(f.read())
        f.close()

    username = info["username"]

    print("Hello {user}! Please login to continue. Type 'quit' to quit.".format(user=username))
    # Login stuff
    pwd = input("Password: ")

    if pwd.lower() == "quit":
        print("Goodbye!")
        sys.exit()

    return None


def new_user():
    print("Hello! Please register a new account to continue.")
    print("You can type 'cancel' at any time to cancel registration, or 'quit' to quit the program\n")

    # Get username
    badUsername = True
    username = ""
    while badUsername:
        badUsername = False
        print("To start, please create a username.")
        print("Usernames can include A-Z, a-z, 0-9, or symbols. Please do not include commas.")
        print("Usernames can be between 1 and 20 characters.")
        username = input("Please enter your username: ")
        
        # Check validity of username
        if username.lower() == "quit":
            print("Goodbye!")
            sys.exit()
        if username.lower() == "cancel":
            clear()
            return False
        if len(username) > 20 or len(username) < 1:
            badUsername = True
        if "," in username:
            badUsername = True

        if badUsername:
            clear()
            print("Bad username input. Please try again.\n")
            continue

        # Check username is available
        serv = Server()
        taken = serv.check_username(username)
        if taken:
            badUsername = True
            clear()
            print("Sorry, username is taken, please try another.")

    # Get password
    clear()
    badPassword = True
    pwd = ""
    while badPassword:
        badPassword = False
        print("Great, welcome {user}! Now we need to create a password.".format(user=username))
        print("Passwords can include A-Z, a-z, 0-9, or symbols. Please do not include commas.")
        print("Passwords must be at least 10 characters and cannot be longer than 1024 characters.")
        pwd = input("Please enter a password: ")

        # Check validity of password
        if pwd.lower() == "quit":
            print("Goodbye!")
            sys.exit()
        if pwd.lower() == "cancel":
            clear()
            return False
        if len(pwd) > 1024 or len(pwd) < 10:
            badPassword = True
        if "," in pwd:
            badPassword = True

        if badPassword:
            clear()
            print("Bad password input. Please try again.\n")

    return register(username, pwd)


def register(user, pwd):
    print("Thank you for registering {user}! There are just a few more steps...".format(user=user))
    print("Generating your private RSA key...")
    try:
        userPrivateKey = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
    except:
        print("Error generating private key. Please try registering again.")
        return False

    print("Success! Private key created.")
    print("Generating your public RSA key...")
    try:
        userPublicKey = userPrivateKey.public_key()
    except:
        print("Error creating private key. Please try registering again.")
        return False
    print("Success! Public key created.")

    # Create connection with server
    serv = Server()

    # Attempt to register user with server
    registered = serv.register(user, pwd, userPublicKey)

    # If successful registration, save user information to local system
    if registered:
        print("Saving your info...")
        # Define user directory
        userDirectory = "{dir}/existing_user/{user}".format(dir=os.getcwd(), user=user)

        # Make user directory
        try:
            os.mkdir(userDirectory)
        except:
            print("Error creating user directory.")
            return False

        # Make keys directory
        try:
            os.mkdir("{udir}/keys".format(udir=userDirectory))
        except:
            print("Error creating keys directory.")
            return False

        # Create user info - find more info to store here
        userInfo = {
            "username": user,
            "creation": time.asctime()
        }

        # Save user info
        try:
            with open("{cwd}/existing_user/user_info.json".format(cwd=os.getcwd()), "w") as f:
                json.dump(userInfo, f)
                f.close()
        except:
            print(sys.exc_info())
            print("Error saving user info")
            return False

        print("Saving your keys...")
        # Write private key
        prvPem = userPrivateKey.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        try:
            with open("{uDir}/keys/privatekey.pem".format(uDir=userDirectory), "wb") as f:
                f.write(prvPem)
                f.close()
        except:
            print("Error saving private key.")
            return False

        print("\n\nYour private key has been saved. !!!!! DO NOT LOSE THIS KEY !!!!! If you lose your private key you must DELETE YOUR ACCOUNT and re-register with the system, which will cause you to lose all your files.")
        print("Your registration was successful!")
        print("\n")
        return True
    else:
        print("Error registering with server.")
        return False


def greeting():
    user = None
    directory = "{cwd}/existing_user".format(cwd=os.getcwd())

    while user is None:
        # Greeting message
        print("Hello! Welcome to Secure Exchange where you can securely send files to other users.\n")
        print("A note to anyone using this program: this is a program for me to gain a better understanding of encryption techniques, so I cannot guarantee actual security of anything you send/receive.\n")

        # Direct user to correct portal
        while True:
            # Check user directory exists. If not, make it
            try:
                userList = os.listdir(directory)
                break
            except FileNotFoundError:
                os.mkdir(directory)
                continue

        if len(userList) > 0:
            print("User detected...")
            user = user_exists(directory)
        else:
            print("User not detected!")
            reg = new_user()

            if not reg:
                print("There was an error registering you with the system. Please check back later or contact Jeff")
    
    return user

if __name__ == "__main__":
    # Clear terminal window
    clear()

    # Greet user until authorized
    user = greeting()

    # Once authorized, create service
    exchange = Exchange(user)

    # Start service
    exchange.start()

    # Once service returns, quit program
    sys.exit()
