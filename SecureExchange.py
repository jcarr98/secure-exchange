# External imports
import sys
from os import system, name
# Custom imports
from welcome import welcome
from user import User

def clear():
    # Windows
    if name == 'nt':
        _ = system('cls')
    # Mac/linux
    else:
        _ = system('clear')

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
            user.send("joff", "hello", "Test message", True)
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
        clear()
        success = welcome()
        print(success)

    # Successful login
    runClient(success)
