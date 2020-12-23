# Python imports
import sys
import os

# Custom imports
from secex import Exchange
import src.welcome as welcome

def clear():
    """Clears terminal window"""
    # Windows
    if os.name == 'nt':
        _ = os.system('cls')

    # Mac/linux
    else:
        _ = os.system('clear')

def greeting():
    user = None
    # Print welcome message
    welcome.print_welcome()

    # Wait for user feedback
    cmd = input("Please login (l), register (r), or quit (q) to continue. For help type 'help': ")

    # Parse user input
    parsedCmd = cmd.split(" ")

    # Message holder
    message = ""

    # Check for keywords 'login', 'register', 'help', or 'quit' and execute accordingly
    if parsedCmd[0] == "help":
        # Clear screen for readability
        clear()
        # Print help
        welcome.print_help()

        # Allow user to read help
        input("Press ENTER to continue.")

        user = None
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
            user = welcome.login(parsedCmd[1], parsedCmd[2])
    elif parsedCmd[0] == "quit" or parsedCmd[0] == "q":
        # Quit program
        print("Goodbye!")
        sys.exit()
    else:
        user, message = None, "Invalid command, try again."
    
    return user

if __name__ == "__main__":
    # Clear terminal window
    clear()

    # Greet user until authorized
    user = None
    while user is None:
        clear()
        user = greeting()

    # Once authorized, create service
    exchange = Exchange(user)

    # Start service
    exchange.start()

    # Once service returns, quit program
    sys.exit()
