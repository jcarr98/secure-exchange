# Python imports
import os
import json

# Cryptography imports
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class User:
    def __init__(self, name, directory):
        self.name = name
        self.session = None

        # Check user exists
        if not os.path.isdir(directory):
            return None
        else:
            self.directory = directory


    def send(self, recipient, subject, file, message=False):
        if message:
            # Put full message into data and add extension
            fullFile = file
            ext = "txt"
        else:
            # Get file contents
            f = open(file, "r")
            fullFile = f.read()
            f.close()

            # Get extension type
            ext = file.split(".")[-1]

        # Encode message
        fullFile = fullFile.encode('utf-8')

        # Create file name
        initialName = subject.strip(".")
        name = initialName
        # Make sure name is unique
        # Method: add a unique number to the end of the file
        allFiles = os.listdir("%s/test_files/sent_files" % os.getcwd())
        cleanFiles = []
        # Strip extensions
        for item in allFiles:
            item = item.split(".")[0]
            cleanFiles.append(item)

        i = 1
        while True:
            if name in cleanFiles:
                name = initialName + str(i)
                i += 1
            else:
                break
        
        # Generate key
        key = Fernet.generate_key()

        # Encrypt key
        safeKey = self.__encryptRSA(recipient, key)

        # Save key
        with open(("%s/test_files/sent_files/%s.key" % (os.getcwd(), name)), "wb") as f:
            f.write(safeKey)
            f.close()

        # Encrypt file
        safeFile = self.__encrypt(fullFile, key)

        # Save this file
        with open(("%s/test_files/sent_files/%s.%s" % (os.getcwd(), name, ext)), "wb") as f:
            f.write(safeFile)
            f.close()

        # Save file info
        with open("%s/test_files/sent_files/combos.json" % os.getcwd(), "r") as f:
            combos = json.load(f)
            f.close()

        combos[name] = {
            "recipient": recipient,
            "sender": self.user["username"],
            "subject": subject,
            "message": message,
            "file": ("%s.%s" % (name, ext)),
            "key": ("%s.key" % name)
        }

        with open("%s/test_files/sent_files/combos.json" % os.getcwd(), "w") as f:
            json.dump(combos, f)
            f.close()
        
        print("Sent message %s" % file)


    def list_possessions(self):
        pass

    
    def retrieve_file(self, file):
        """Interact with the specified file"""
        pass

    
    def encryptRSA(self, file, key):
        """Encrypt and sign a file using RSA public keys
        
                Parameters:
                    file (bytes): the file to be encrypted
                    key (RSAPublicKey): public key to encrypt files with

                Returns:
                    (file, signature) where file=encrypted file and signature=signature of file
        """
        # Load private key
        try:
            with open("%s/keys/privatekey.pem" % self.directory, "rb") as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
        except:
            # Someday, create custom exceptions
            print("Error signing message")
            return

        # Sign file
        signature = private_key.sign(
            file,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Encrypt file
        safeFile = key.encrypt(
            file,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return (safeFile, signature)

    
    def get_name(self):
        return self.name

    
    def save_session(self, key):
        self.session = key

    
    def decryptRSA(self, file):
        pass
        

    def __encrypt(self, file, key=None):
        # Use session key if no key is provided
        if key is None:
            encryptor = Fernet(self.session)
        else:
            encryptor = Fernet(key)

        return encryptor.encrypt(file)


    def __decrypt(self, file, key=None):
        # Use session key if no key is provided
        decryptor = Fernet(self.session)

        return decryptor.decrypt(file)

    
    def __save(self, location, file):
        pass


    def __refresh(self):
        pass