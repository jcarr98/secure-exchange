# Python imports
import sys
import os

# Custom imports
import welcome
from user import User

def clear():
    # Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # Mac/linux
    else:
        _ = os.system('clear')

def login():
    user = None
    while user is None:
        # Print welcome message
        welcome.print_welcome()

        # Wait for user feedback
        cmd = input("Please login (l), register (r), or quit (q) to continue. For help type 'help': ")

        # Parse user input
        parsedCmd = cmd.split(" ")

        # Check for keywords 'register' or 'login' and execute accordingly
        if parsedCmd[0] == "help":
            # Print help
            welcome.print_help()
        elif parsedCmd[0] == "register" or parsedCmd[0] == "r":
            # Check if correct command
            if len(parsedCmd) > 3:
                print("Too many inputs! There should only be 3 words.")
            else:
                # Attempt to register user with system
                user, message = welcome.register(parsedCmd[1], parsedCmd[2])
        elif parsedCmd[0] == "login" or parsedCmd[0] == "l":
            if len(parsedCmd) > 3:
                print("Too many inputs! There should only be 3 words.")
            else:
                # Attempt to log user in
                user, message = welcome.login(parsedCmd[1], parsedCmd[2])
        elif parsedCmd[0] == "quit" or parsedCmd[0] == "q":
            # Quit program
            print("Goodbye!")
            sys.exit()
        else:
            user, message = None, "Invalid command, try again."
        
        clear()
        print(message)
        print("\n")
    
    return user


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
    user = login()

    # Successful login
    runClient(user)
