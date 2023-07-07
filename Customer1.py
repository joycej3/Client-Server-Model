
from IPython.display import display, HTML
import pandas as pd
import numpy as np
import socket
import select
import errno
import random
import time
import sys

HEADER_LENGTH = 10
OPTION_LENGTH = 10

#Socket Setup
IP = socket.gethostname()
PORT = 1234

#Connect to specified socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)


def receive_message(client_socket):

    try:

        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            print("hero")
            return False

        message_length = int(message_header.decode('utf-8').strip())

        OPTION = client_socket.recv(OPTION_LENGTH)
        OPTION = OPTION.decode('utf-8')

        DATA = client_socket.recv(message_length)
        DATA = DATA.decode('utf-8')

        return {'header': message_header, 'option': OPTION , 'data': DATA}

    except:

        return False

def get_wardrobe(client_socket):
    message = receive_message(client_socket)
    if message == False:
        print("Error Wardrobe Message False")
    item = message['data']

    #items = serverDB['status'].where(serverDB['itemID'] == find)

    print('Wardrobe\n')

    while item != "9999":
        print(f'Item: {item}\n')
        message = receive_message(client_socket)
        item = message['data']
        if message == False:
            print("Error Wardrobe Message False")
            continue

verified = "1"
while verified == "1":
    #Customer1 id number 13579
    Client_ID = input("Enter username:")
    Client_Password = input("Enter password:")

    #Send Client id and placeholder sequence
    client = Client_ID.encode('utf-8')
    client_header = f"{len(client):<{HEADER_LENGTH}}".encode('utf-8')
    PH = "9"* OPTION_LENGTH
    ph = PH.encode('utf-8')
    client_socket.send(client_header + ph + client)

    #Send Client id and placeholder sequence
    clientpassword = Client_Password.encode('utf-8')
    client_header = f"{len(clientpassword):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(client_header + ph + clientpassword)

    time.sleep(1)
    confirm = receive_message(client_socket)
    if confirm is False:
        print("Error Confirm Message False")
        continue
    verified = confirm['data']

    print('Account verified:', str(verified), '\n')

#Customer can either buy or return items in their "Wardobe"

get_wardrobe(client_socket)
option = "999"
while option != "3":

    option = input("Would you like to buy or return an item: Enter\n 1:Buy\n 2:Return\n 3:Quit\n:")

    if option != "3":

        item_id = input("Enter the item id you would like to buy or return: ")

        message_option = str(option)
        message = str(item_id)

        try:
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            message_OPTION = f"{message_option:<{OPTION_LENGTH}}".encode('utf-8')
            client_socket.send(message_header + message_OPTION + message)

        except IOError as e:
            #To avoid crashes if theres no incoming data
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

            continue

        except Exception as e:
            # if a non io error occurs
            print('Reading error: '.format(str(e)))
            sys.exit()
