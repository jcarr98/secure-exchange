from pymongo import MongoClient

class User:
    def __init__(self):
        # Spawn second thread to continuously look for updates
        self.allMessages = ["Hi Jeff from the future!", "This is from Sara"]

    def send(self, file):
        print("Sent message %s" % file)

    def receive(self):
        print("Received 1 new message!")
    
    def listMessages(self):
        if len(self.allMessages) == 0:
            print("You have no messages!")
            return
        
        print("Your messages:")
        for i in range(0, len(self.allMessages)):
            print("%i. %s" % (i+1, self.allMessages[i]))
        
        print("\n") # Add space for readability

    def readMessage(self):
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
            except:
                print("Please enter a number.")
                continue

            if (messageToRead <= 0) or (messageToRead > len(self.allMessages)):
                print("Please enter a valid message number.")
            else: 
                break
        
        print("Reading message %i" % messageToRead)
        print(self.allMessages[messageToRead-1])
        print("\n\n")  # Add some spacing for readability

    def __refresh(self):
        pass