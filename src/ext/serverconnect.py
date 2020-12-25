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
        msg = "AUTH,{name},{password}".format(name=name, password=pwd)

        # Encrypt message with server's RSA key
        safeMsg = self.__encrypt_RSA(msg, self.server_key)

        # Create packet
        pack = Packet()
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

        # Create reg packet
        msg = "REGISTER,{user},{pwd},{key}".format(user=user, pwd=pwd, key=pKey)

        # Encrypt message with server's public key
        safeMsg = self.__encrypt_RSA(msg, self.server_key)

        # Craft reg packet
        pack = Packet()
        pack.add_encrypted(safeMsg)

        # Send request packet
        self.sock.sendall(pack.send())

        # Read response
        resp = self.__receive_packet()

        # Done sending messages
        self.sock.close()

        # Shouldn't be encrypted, so load into packet
        pack2 = Packet(resp)

        # Check response
        # Possibilties:
        # DONE,OK - User successfully registered
        # DONE,ERR - Error registering user with system
        return pack2.get_fields(1) == "OK"

    
    def check_username(self, user):
        # Connect to server
        self.__initiate_connection("127.0.0.1", 8008)

        # Create request message
        msg = "USER,{req}".format(req=user)

        # Encrypt this message with server's rsa key
        safeMsg = self.__encrypt_RSA(msg, self.server_key)

        # Craft request packet
        pack = Packet()
        pack.add_encrypted(safeMsg)

        # Send request pack
        self.sock.sendall(pack.send())

        # Read response
        resp = self.__receive_packet()

        # Done sending messages
        self.sock.close()

        # Shouldn't be encrypted, so load into packet
        pack = Packet(resp)
        print(pack.get_fields())

        # Check response
        # Possibilities:
        # USER,YES - User exists
        # USER,NO - User does not exist
        # USER,BAD - Error
        if pack.get_fields(1) == "YES":
            return True
        elif pack.get_fields(1) == "NO":
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
        pack = Packet("HELLO,SecureClient")

        # Send HELLO packet
        self.sock.sendall(pack.send())

        # Wait for server's response, should be server's key
        resp = self.__receive_packet()

        # Since this shouldn't be encrypted, we can turn it directly into a packet to manipulate
        pack = Packet(resp)

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

        # Get length of packet
        length = int(pkt.split(separator, 1)[0].decode('utf-8'))
        
        # Separate data, encode back into bytes to maintain size counter
        data = pkt.split(separator, 1)[1]

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

        return data


    def __encrypt_RSA(self, file, key):
        # Encrypt file
        safeFile = key.encrypt(
            file.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return safeFile