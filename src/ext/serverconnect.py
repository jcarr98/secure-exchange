# Python imports
import socket
import os

# Cryptography imports
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# Custom imports
from src.user import User
from src.ext.packet import Packet

class ServerConnect(object):
    def __init__(self) -> None:
        # Class variables
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # The socket connected to the server
        self.user = None  # The user interacting with the server, None until authed
        self.server_key = None  # The public RSA key of the server

    
    def auth(self, name, pwd):
        """Authenticate user to server
    
                Parameters:
                    user (str): username
                    pwd (str): password

                Returns:
                    True if authenticated, False if bad auth
        """
        # Check user exists on system
        if not os.path.isdir("{loc}/local_users/{name}".format(loc=os.getcwd(), name=name)):
            print("Bad username or password")
            return False

        # Connect to server
        print("initiating connection with {name}".format(name=name))
        self.__initiate_connection("127.0.0.1", 8008, name)

        # Create auth message
        msg = "{name},{password}".format(name=name, password=pwd)

        # Encrypt message with server's RSA key
        safeMsg = self.__encrypt_RSA(msg, self.server_key)

        # Create packet
        pack = Packet("AUTH")
        # Add encrypted data
        pack.add_encrypted(safeMsg)

        # Send packet to server
        self.sock.sendall(pack.send())

        # Receive AUTH packet
        resp = self.__receive_packet()

        # Done communicating with server, close socket
        self.sock.close()

        # If successful, packet should be:
        # OK, <session_key encrypted with user public key>
        semiResp = resp.split(",".encode('utf-8'), 1)

        if semiResp[0].decode('utf-8') != "OK":
            print("Bad username or password")
            return False

        # Load user
        self.user = User(name, "{loc}/local_users/{name}".format(loc=os.getcwd(), name=name))

        # Decrypt rest of data, should be session key
        sess = self.user.decryptRSA(semiResp[1])

        # Add session key to user
        self.user.save_session(sess)

        # Successful auth
        return True

    
    def register(self, user, pwd, pKey):
        # Connect to server
        self.__initiate_connection("127.0.0.1", 8008)

        # Create registration message
        msg = "{user},{pwd}".format(user=user, pwd=pwd)

        # Encrypt message with server's public key
        safeMsg = self.__encrypt_RSA(msg, self.server_key)

        # Craft registration packet
        # Format: <public key>,<username>,<password>
        pack = Packet("REGISTER")
        pack.add_encrypted(pKey)
        pack.add_encrypted(safeMsg)

        # Send request packet
        self.sock.sendall(pack.send())

        # Read response
        respCat, resp = self.__receive_packet()

        # Done sending messages
        self.sock.close()

        # Shouldn't be encrypted, so load into packet
        pack2 = Packet("REGISTER", resp)

        # Check response
        # Possibilties:
        # DONE,OK - User successfully registered
        # DONE,ERR - Error registering user with system
        return pack2.get_fields(1) == "OK"

    
    def login(self, username, password):
        # Connect to the server
        self.__initiate_connection("127.0.0.1", 8008)

        # Send the server a login request
        msg = "{user},{pwd}".format(user=username, pwd=password)

        # Encrypt message
        safeMsg = self.__encrypt_RSA(msg, self.server_key)

        # Craft packet
        lPack = Packet("AUTH")
        lPack.add_encrypted(safeMsg)

        # Send login packet
        self.sock.sendall(lPack.send())

        # Wait for response
        lResp = self.__receive_packet()
        print(lResp)

        # Response format should be:
        # DONE,SUCC,<token (fernet)>,<key (rsa)>
        # DONE,ERR
        
        # Separate all fields
        respParsed = lResp.split(",".encode('utf-8'))

        # Check for success
        if respParsed[1] == "ERR":
            print("Login error")
            return False
        
        # Create user
        user = User(username, "{loc}/existing_user/{user}".format(loc=os.getcwd(), user=username))

        # Get key
        key = user.decryptRSA(respParsed[3])

        user.save_session(key)

        return user

    
    def check_username(self, user):
        # Connect to server
        self.__initiate_connection("127.0.0.1", 8008)

        # Encrypt message with server's rsa key
        safeMsg = self.__encrypt_RSA(user, self.server_key)

        # Craft request packet
        pack = Packet("USER")
        pack.add_encrypted(safeMsg)

        # Send request pack
        self.sock.sendall(pack.send())

        # Read response
        respHeader, resp = self.__receive_packet()

        # Done sending messages
        self.sock.close()

        # Shouldn't be encrypted, so load into packet
        pack = Packet(respHeader, resp)

        # Check response
        # Possibilities:
        # YES - User exists
        # NO - User does not exist
        # BAD - Error
        if pack.get_fields(0) == "YES":
            return True
        elif pack.get_fields(0) == "NO":
            return False
        else:
            raise("Error retrieving username information.")

    
    def get_user(self):
        return self.user

    
    def __initiate_connection(self, ip, port):
        # Create socket and connect to server
        self.sock.connect((ip, port))
        self.server_key = self.__handshake()


    def __handshake(self):
        """Performs initial handshake with server and gets server's RSA
    
            Parameters:
                sock: socket connected to server

            Returns:
                Server's public RSA key
        """
        # Craft HELLO packet
        # Format: HELLO,SecureClient
        pack = Packet("HANDSHAKE", "HELLO,SecureClient")

        # Send HELLO packet
        self.sock.sendall(pack.send())

        # Wait for server's response, should be server's key
        header, resp = self.__receive_packet()

        # Since this shouldn't be encrypted, we can turn it directly into a packet to manipulate
        pack = Packet("HANDSHAKE", resp)

        # Format of server HELLO should be:
        # HELLO,SecureServer,key
        if pack.get_fields(0) != "HELLO" or pack.get_fields(1) != "SecureServer":
            print("Bad handshake with server")
            return False

        # Create key from string
        key = serialization.load_pem_public_key(
            pack.get_fields(2).encode('utf-8'),
            backend=default_backend()
        )

        # Return server key
        return key

    
    def __receive_packet(self):
        # Receive first chunk of packet
        pkt = self.sock.recv(1024)

        # Separate by comma, but can't decode encrypted data
        separator = ",".encode('utf-8')

        # Get length of header
        headerLength = int(pkt.split(separator, 1)[0].decode('utf-8'))

        try:
            # Get entire header, should not be more than 1024 bytes
            header = pkt[0:headerLength]

            # Header should be in format header_length, data_length, packet_type
            header = header.decode('utf-8')
        except:
            print("Header error")
            return None

        # Get length of data
        length = int(header.split(",")[1])
        
        # Separate data, encode back into bytes to maintain size counter
        try:
            data = pkt[headerLength+1:]
        except IndexError:
            # If header was exactly 1024 (should never happen)
            data = bytes(0)

        # Get bytes left to collect
        remaining = length - len(data)

        # Keep collecting bytes until there are none left
        while remaining > 0:
            # Collect new data
            newData = self.sock.recv(1024)
            # Updated bytes remaining
            remaining -= len(newData)
            # Append onto already collected data
            data += newData

        return header, data


    def __encrypt_RSA(self, file, key):
        # Encrypt file
        print(key)
        print(file)
        safeFile = key.encrypt(
            file.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return safeFile