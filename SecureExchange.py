# Python imports
import sys
import os

# Custom imports
import src.welcome as welcome
import src.ext.serverconnect as server

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
            "1": __send,
            "2": __refresh,
            "3": __list_messages,
            "4": __list_messages,
            "5": __quit
        }

        # Get action user chooses
        action = choices.get(cmd, lambda: "Invalid input. Please enter the number only.")

        # Perform action
        action()

def __send(user):
    # Get recipient to send user to, make sure it is at least one character
    while True:
        recipient = input("Who would you like to send the file to?\n")
        if len(recipient.strip(" ")) == 0:
            print("Please enter a valid recipient.")
        else:
            break

    # Get type of data
    while True:
        fileType = input("Would you like to send a message or a file? (m/f)\n")
        print(fileType)
        if fileType != "m" and fileType != "f":
            print("Please pick either m or f.")
        else:
            break

    # Deal with message
    if fileType == "m":
        # Get subject of message
        while True:
            subject = input("What is the subject of your message?\n")
            if len(subject.strip(" ")) == 0:
                print("Please enter a valid subject.")
            else:
                break
        
        # Get user message
        print("What message would you like to send?")
        message = input()

        # Send message
        user.send(recipient, subject, message, True)
    else:
        print("Work in progress")

def __refresh(user):
    user.receive()

def __list_messages(user):
    messages = user.getMessages()
    if len(messages) == 0:
        print("No messages!")
    for i in range(0, len(messages)):
        print("%i. %s from %s" % (i+1, messages[i]["subject"], messages[i]["sender"]))

def __read_message(user):
    user.readMessage()

def __quit():
    print("Goodbye!")
    sys.exit()


if __name__ == "__main__":
    # Clear screen
    clear()
    # Show login screen
    user = greeting()

    # Successful login
    runClient(user)
