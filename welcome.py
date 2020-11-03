class Welcome:
    def __init__(self):
        pass

    def printWelcome(self) -> bool:
        """Print the welcome text to user"""
        # Print messages
        print("Welcome to Secure Excange, where you can send files securely to other users! Please either login or register.\n")
        print("To login, use the following command: 'login <username> <password>' with no quotes and replacing <username> with your username and <password> with your password.\n")
        print("To register, use the following command: 'register <username> <password>' with no quotes and replacing <username> with your desired username and <password> with your desired password.\n")
        print("Type 'register help' to see specifc username and password requirements.\n")
        print("A note to anyone using this program: this is a practice encryption program by me, so I cannot guarantee actual security on anything you send/receive.\n")

        userAnswer = input("Please login or register to continue: ")
        return self.__parseWelcome(userAnswer)

    def __parseWelcome(self, cmd) -> bool:
        # Parse user input
        parsedCmd = cmd.split(" ")

        # Check for keywords 'register' or 'login' and execute accordingly
        if len(parsedCmd) == 2 and parsedCmd[0] == "register" and parsedCmd[1] == "help":
            outcome = self.__registerHelp()
        elif parsedCmd[0] == "register" and len(parsedCmd) == 3:
            outcome = self.__register(parsedCmd[1], parsedCmd[2])
        elif parsedCmd[0] == "login" and len(parsedCmd) == 3:
            outcome = self.__login(parsedCmd[1], parsedCmd[2])
        elif parsedCmd[0] == "admin":
            outcome = self.__admin()
        else:
            print("Invalid command, try again.")
            self.printWelcome()
            return False
        
        return outcome

    def __login(self, user, pwd) -> bool:
        """Allow users to login to the system"""
        return False

    def __register(self, user, pwd) -> bool:
        """Allow users to register with the system"""
        return False

    def __admin(self) -> bool:
        """This is only for testing, it MUST be deleted after deployment"""
        print("Success! Logged in as admin")
        return True

    def __registerHelp(self) -> bool:
        print("Username requirements: 16 characters or less.")
        print("Password requirements: 32 characters or less.")
        self.printWelcome()
        return False