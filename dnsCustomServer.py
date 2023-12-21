import socket
from cryptography.fernet import Fernet
import dns.message
import dns.name
import dns.query
import dns.zone
import os

# Generate a key for AES encryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Create a socket for receiving connections
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 53))
server_socket.listen(10)
print("Listening for connections...")

while True:
    connection, address = server_socket.accept()
    print("Received connection from", address)
    
    # Receive encrypted data from the client
    received_data = b''
    while len(received_data) < 4096:
        chunk = connection.recv(4096 - len(received_data))
        if not chunk:
            break
        received_data += chunk
        
    decrypted_data = cipher_suite.decrypt(received_data)
    message = dns.message.Message.from_wire(decrypted_data)
    question = message.question[0]
    rrset = dns.rrset.RRset.create((question.name, question.rdtype, question.rdclass), message.answer[0])
    filename = str(rrset)[2:-1].split(", ")[-1]

    # Save the received file
    open(filename, 'wb').write(connection.recv(os.path.getsize(filename)))
    print("File saved:", filename)

    connection.close()