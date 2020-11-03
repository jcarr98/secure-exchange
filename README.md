# secure-exchange
A platform to securely exchange files and messages

# Why?
I'm making this as a personal cybersecurity project to not only show what I know about cybersecurity but also to learn more about how these techniques work 
in practice.

# How it Works
I'm using Python3 to write most of this code. When a user
registers, the program creates an RSA public/private key pair. The private key is stored on the user's machine and the public key is stored in a database. When
a users wishes to send another file, they encrypt the message using AES-256. Their program then encrypts the key using the server's public RSA key and sends it
to the database to be stored. The user then sends the AES encrypted data to the database. Then, when a user wants to retrieve the message/file that was sent to
them, they first retrieve the AES key, which the server encrypts in the user's public RSA key. They then retrieve the AES encoded data. Now they can extract the
AES key and decrypt the data that was sent to them. A small diagram is below for clarity.

User sending data:\
ServerRSA(aes_key) --> database\
AES(data) --> database

User receiving data:\
database --> UserRSA(aes_key)
database --> AES(data)

# Future Plans
Currently, I am using pyca/cryptography to encrypt/decrypt the data, however I'm hoping someday to write my own RSA/AES algorithm to get a better understanding of how they
work. Also for now it is only a command-line program, but maybe someday in the future I'll create a GUI for it.
