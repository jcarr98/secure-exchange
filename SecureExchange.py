# Python imports
import sys
import os

# Custom imports
import welcome

def clear():
    # Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # Mac/linux
    else:
        _ = os.system('clear')

def greeting():
    user = None
    while user is None:
        # Print welcome message
        welcome.print_welcome()

        # Wait for user feedback
        cmd = input("Please login (l), register (r), or quit (q) to continue. For help type 'help': ")

        # Parse user input
        parsedCmd = cmd.split(" ")

        # Message holder
        message = ""

        # Check for keywords 'register' or 'login' and execute accordingly
        if parsedCmd[0] == "help":
            # Clear screen for readability
            clear()
            # Print help
            welcome.print_help()
            continue
        elif parsedCmd[0] == "register" or parsedCmd[0] == "r":
            # Check for correct command syntax
            if len(parsedCmd) > 3:
                user, message = None, "Too many inputs! There should only be 3 words."
            elif len(parsedCmd) < 3:
                user, message = None, "Not enough inputs! There should be 3 words."
            else:
                # Attempt to register user with system
                user, message = welcome.register(parsedCmd[1], parsedCmd[2])
        elif parsedCmd[0] == "login" or parsedCmd[0] == "l":
            # Check for correct command syntax
            if len(parsedCmd) > 3:
                user, message = None, "Too many inputs! There should only be 3 words."
            elif len(parsedCmd) < 3:
                user, message = None, "Not enough inputs! There should be 3 words."
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
    """Hub that redirects code to appropriate command
    
            Parameters:
                user (User): The user to perform actions on
    """
    # Loop until quit
    while True:
        # List options for user
        print("What would you like to do?")
        print("(1) Send, (2) Refresh, (3) List Messages, (4) Read Message, (5) Quit")
        cmd = input("Enter an option number: ")

        choices = {
            "1": send,
            "2": refresh,
            "3": list_messages,
            "4": list_messages,
            "5": quit
        }

        action = choices.get(cmd, lambda: "Invalid input. Please enter the number only.")

        action()

def send(user):
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

def refresh(user):
    user.receive()

def list_messages(user):
    messages = user.getMessages()
    if len(messages) == 0:
        print("No messages!")
    for i in range(0, len(messages)):
        print("%i. %s from %s" % (i+1, messages[i]["subject"], messages[i]["sender"]))

def read_message(user):
    user.readMessage()

def quit():
    print("Goodbye!")
    sys.exit()


if __name__ == "__main__":
    # Clear screen
    clear()
    # Show login screen
    user = greeting()

    # Successful login
    runClient(user)
