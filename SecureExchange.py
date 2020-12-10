# External imports
import sys
import os
# Custom imports
from welcome import welcome
from user import User

def clear():
    # Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # Mac/linux
    else:
        _ = os.system('clear')

def runClient(user):
    # Clear screen
    clear()

    # Create user
    # user = User()

    # Loop until quit
    while True:
        # List options for user
        print("What would you like to do?")
        print("(1) Send, (2) Refresh, (3) List Messages, (4) Read Message, (5) Quit")
        userInput = input("Enter an option number: ")

        # Check for valid input
        try:
            userInput = int(userInput)
        except ValueError:
            print("Invalid option, please enter the number only.")
            continue
        
        #Clear screen
        clear()

        # Parse user input
        if userInput == 1:
            while True:
                recipient = input("Who would you like to send the file to? ")
                # Check recipient exists - BACKEND FUNCTION
                path = "%s/test_files" % os.getcwd()
                allFiles = os.listdir(path)
                exists = False
                for i in allFiles:
                    if os.path.isdir("%s/%s" % (path, i)) and i == recipient:
                            exists = True
                            break
                if exists:
                    break
                else:
                    print("Please pick a valid recipient")
            while True:
                fileType = input("Would you like to send a message or a file? m/f: ")
                print(fileType)
                if fileType != "m" and fileType != "f":
                    print("Please pick a valid option.")
                else:
                    break

            if fileType == "m":
                while True:
                    subject = input("What is the subject of your message? ")
                    if len(subject.strip(" ")) == 0:
                        print("Please enter a valid subject")
                    else:
                        break

                print("What message would you like to send?")
                message = input()
                user.send(recipient, subject, message, True)
            else:
                print("Work in progress")
        elif userInput == 2:
            user.receive()
        elif userInput == 3:
            messages = user.getMessages()
            if len(messages) == 0:
                print("No messages!")
                continue
            for i in range(0, len(messages)):
                print("%i. %s from %s" % (i+1, messages[i]["subject"], messages[i]["sender"]))
        elif userInput == 4:
            user.readMessage()
        elif userInput == 5:
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid option, please enter a number from above.")


if __name__ == "__main__":
    # Show login screen
    success = False
    while not success:
        #clear()
        success = welcome()
        print(success)

    # Successful login
    runClient(success)
