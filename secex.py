# Python imports
import sys
import os
import time
import threading

# Custom imports
import src.ext.serverconnect as serverconnect

class Exchange(object):
    def __init__(self, user) -> None:
        self.user = user  # User interacting with the program
        self.session = None  # The session key established with the server this session

        # Timer stuff
        self.time_thread = threading.Thread(target=self.__timing, args=(1200,))  # Thread keeping track of time
        self.time_lock = threading.Lock()  # Lock for changing time
        self.interaction = time.monotonic()  # Time since last interaction
    
    def start(self):
        # Start timer thread
        try:
            self.time_thread.start()
        except SystemExit:
            self.__quit()

        # Run the program
        self.__run()

    def __run(self):
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
                "1": self.__send,
                "2": self.__refresh,
                "3": self.__list_messages,
                "4": self.__read_message,
                "5": self.__quit
            }

            # Get action user chooses
            action = choices.get(cmd, lambda: "Invalid input. Please enter the number only.")

            # Perform action
            action()

    def __send(self):
        """Gets additional details about data to send and relays information to """

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
            
            # Get user message and encode it
            print("What message would you like to send?")
            file = input().encode('utf-8')
        else:
            print("Work in progress")

        # Pass information to serverconnect

    def __refresh(self):
        pass

    def __list_messages(self):
        pass

    def __read_message(self):
        pass

    def __quit(self):
        print("Goodbye!")
        sys.exit()

    def __timing(self, max):
        """Keeps track of timing and auto-quits when user idles longer than max seconds
        
                Parameters:
                    max (number): The max amount of seconds before program auto quits

                Returns:
                    None
        """
        while True:
            if time.monotonic() - self.interaction > max:
                print("Idled too long, quitting...")
                sys.exit()

    def __clear(self):
        # Windows
        if os.name == 'nt':
            _ = os.system('cls')

        # Mac/linux
        else:
            _ = os.system('clear')