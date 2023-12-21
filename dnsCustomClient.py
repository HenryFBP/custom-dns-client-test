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

# Send a request to the server asking for a specific file
requested_file = "/etc/passwd"
question = dns.message.Question(dns.name.Name(requested_file), dns.dtypes.TXT, dns.name.root)
msg = dns.message.Message()
msg.add_question(question)

# Encrypt the request using AES
encrypted_request = cipher_suite.encrypt(msg.to_wire())

# Connect to the server (UDP since it's faster than TCP)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.sendto(encrypted_request, ('localhost', 53))

# Get the response from the server
response, _ = client_socket.recvfrom(4096)
message = dns.message.Message.from_wire(response)
answer = message.answer[0]
filename = answer.items()[0][1].to_text().strip('"\n')

# Download the requested file
with open(filename, 'wb') as f:
    while True:
        chunk = client_socket.recv(1024)
        if not chunk:
            break
        f.write(chunk)

print("File downloaded:", filename)