from cryptography.fernet import Fernet
import os
import json

class User:
    def __init__(self, username):
        # Load user info
        with open(("test_files/%s/userInfo.json" % username), "r") as f:
            self.user = json.load(f)

        # To check if the program is currently doing something
        self.busy = False

    def send(self, recipient, subject, file, message=False):
        self.busy = True
        if message:
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
        initialName = subject
        name = initialName
        # Make sure name is unique
        # Method: add a unique number to the end of the file
        allFiles = os.listdir("%s/test_files/sent_files" % os.getcwd())
        cleanFiles = []
        # Strip extensions
        for item in allFiles:
            item = item.split(".")[0]
            cleanFiles.append(item)

        print(cleanFiles)
        i = 1
        while True:
            if name in cleanFiles:
                name = initialName + str(i)
                print("Changing name to %s" % name)
                i += 1
            else:
                break
        
        print("Saved as %s" % name)
        # Generate key
        key = Fernet.generate_key()
        # Save key
        with open(("%s/test_files/sent_files/%s.key" % (os.getcwd(), name)), "wb") as f:
            f.write(key)
            f.close()

        # Start encrypting
        encryptor = Fernet(key)
        safeFile = encryptor.encrypt(fullFile)

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
            "file": ("%s.%s" % (name, ext)),
            "key": ("%s.key" % name)
        }

        with open("%s/test_files/sent_files/combos.json" % os.getcwd(), "w") as f:
            json.dump(combos, f)
            f.close()
        
        print("Sent message %s" % file)
        self.busy = False

    def receive(self):
        self.busy = True
        print("Received 1 new message!")
        self.busy = False
    
    def listMessages(self):
        self.busy = True
        if len(self.allMessages) == 0:
            print("You have no messages!")
            return
        
        print("Your messages:")
        for i in range(0, len(self.allMessages)):
            print("%i. %s" % (i+1, self.allMessages[i]))
        
        print("\n") # Add space for readability
        self.busy = False

    def readMessage(self):
        self.busy = True
        # List out messages for user to pick
        while True:
            if len(self.allMessages) == 0:
                print("You have no messages to read!")
                return
            
            print("Pick a message to read")
            self.listMessages()
            messageToRead = input("Please enter a message number: ")

            try:
                messageToRead = int(messageToRead)
            except ValueError:
                print("Please enter a number.")
                continue

            if (messageToRead <= 0) or (messageToRead > len(self.allMessages)):
                print("Please enter a valid message number.")
            else: 
                break
        
        print("Reading message %i" % messageToRead)
        print(self.allMessages[messageToRead-1])
        print("\n\n")  # Add some spacing for readability

        self.busy = False

    def __refresh(self):
        pass