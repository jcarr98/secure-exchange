# External imports
import sys
from os import system, name
# Custom imports
from welcome import Welcome
from user import User

def clear():
    # Windows
    if name == 'nt':
        _ = system('cls')
    # Mac/linux
    else:
        _ = system('clear')

def performWelcome():
    # Clear screen
    clear()

    # Welcome users
    welcomeScreen = Welcome()
    return welcomeScreen.printWelcome()

def runClient():
    # Clear screen
    clear()

    # Create user
    user = User()

    # Loop until quit
    while True:
        # List options for user
        print("What would you like to do?")
        print("(1) Send, (2) Refresh, (3) List Messages, (4) Read Message, (5) Quit")
        userInput = input("Enter an option number: ")

        # Check for valid input
        try:
            userInput = int(userInput)
        except:
            print("Invalid option, please enter the number only.")
            continue
        
        #Clear screen
        clear()

        # Parse user input
        if userInput == 1:
            user.send("Test message")
        elif userInput == 2:
            user.receive()
        elif userInput == 3:
            user.listMessages()
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
        success = performWelcome()

    # Successful login
    runClient()
