from cryptography.fernet import Fernet
import os
import json

class User:
    def __init__(self, username):
        # Load user info
        with open(("test_files/%s/userInfo.json" % username), "r") as f:
            self.user = json.load(f)

        self.messages = []


    def send(self, recipient, subject, file, message=False):
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
        # Save key
        with open(("%s/test_files/sent_files/%s.key" % (os.getcwd(), name)), "wb") as f:
            f.write(key)
            f.close()

        # Encrypt file
        safeFile = self.__encrypt(key)

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


    def receive(self):
        print("Received 1 new message!")
    

    def getMessages(self):
        # Load items from database
        with open("%s/test_files/sent_files/combos.json" % os.getcwd(), "r") as f:
            databaseInfo = json.load(f)
            f.close()

        messages = []

        # Get all messages available to user
        for i in databaseInfo:
            if databaseInfo[i]["recipient"] == self.user["username"] and databaseInfo[i]["message"]:
                messages.append(databaseInfo[i])

    def getFiles(self):
        # Get list of all items available to user
        with open("%s/test_files/sent_files/combos.json" % os.getcwd(), "r") as f:
            databaseInfo = json.load(f)
            f.close()
        
        files = []
        # Download all items from database
        for i in databaseInfo:
            if databaseInfo[i]["recipient"] == self.user["username"] and not databaseInfo[i]["message"]:
                files.append(databaseInfo[i])

        return files


    def readMessage(self):
        messages = self.getMessages()

        if len(messages) == 0:
            print("No messages to read")
            return

        # List out messages for user to pick
        while True:
            print("Pick a message to read")
            for i in range(0, len(messages)):
                print("%i. %s from %s" % (i+1, messages[i]["subject"], messages[i]["sender"]))

            messageToRead = input("Please enter a message number: ")

            try:
                messageToRead = int(messageToRead)
            except ValueError:
                print("Please enter a number.")
                continue

            if (messageToRead <= 0) or (messageToRead > len(messages)):
                print("Please enter a valid message number.")
            else:
                break
        
        messageToRead = messages[messageToRead]

        # Get file key
        with open("%s/test_files/sent_files/%s" % (os.getcwd(), messageToRead["key"]), "rb") as f:
            key = f.read()
            f.close()

        # Get message
        with open("%s/test_files/sent_files/%s" % (os.getcwd(), messageToRead["file"]), "rb") as f:
            file = f.read()
            f.close()

        # Decrypt message
        message = self.__decrypt(file, key)

        print(message)
        print("\n")
        save = input("Would you like to save this message? y/n: ")
        
        if save == "y":
            print("Not implemented yet...")
        
        print("\n\n")  # Add some spacing for readability


    def viewFiles(self):
        pass


    def __encrypt(self, file, key):
        encryptor = Fernet(key)

        return encryptor.encrypt(file)


    def __decrypt(self, file, key):
        decryptor = Fernet(key)

        return decryptor.decrypt(file)

    
    def __save(self, location, file):
        pass


    def __refresh(self):
        pass