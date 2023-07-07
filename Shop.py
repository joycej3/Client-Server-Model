import socket
import select
from sys import version
import time
from datetime import datetime
#from IPython.display import display, HTML
import pandas as pd
import numpy
import bcrypt

HEADER_LENGTH = 10
OPTION_LENGTH =10

DBup = 'userPwdDB.xlsx'
uPwdDB = pd.read_excel(DBup, index_col=0)
DBserv = 'serverDataB.xlsx'
serverDB = pd.read_excel(DBserv, index_col=0)

#connect - login - login and authentication
#connect send message for username - header_field
#received
#send password
#received
#check if valid combination of username and password
#and immediately send items associated with that client, print wardrobe
#then prompt to buy/return/quit,
#send message to buy/return
#send response to say it has been bought/returned
#update database
#print wardrobe
#then prompt to buy/return/quit,



#wardrobe
#call send wardrobe on server side
#search db based on the client id
#send each item until it receives a finishing code




#set up socket
IP = socket.gethostname()
PORT = 1234
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()
sockets_list = [server_socket]


clients = {}

#Variables for Output
item_location = PORT
item_id = 987
item_status = "For Sale"


print(f'Listening for connections on {IP}:{PORT}...')

def receive_message(client_socket):

    try:

        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())

        OPTION = client_socket.recv(OPTION_LENGTH)
        OPTION = OPTION.decode('utf-8')

        DATA = client_socket.recv(message_length)
        DATA = DATA.decode('utf-8')

        return {'header': message_header, 'option': OPTION , 'data': DATA}

    except:


        return False

def send_wardrobe(client_socket, name):
    #search excel for items associated with client_id
    findName = int(name)
    animal = serverDB[serverDB['username'] == findName][['itemID']]
    itemArray = animal.to_numpy()
    itemArray = itemArray.flatten()
    itemArray = list(map(str, itemArray))
    print(itemArray)

    for i in range(0, len(itemArray)):
        item_header = f"{len(itemArray[i]):<{HEADER_LENGTH}}".encode('utf-8')
        PH = "9"* OPTION_LENGTH
        ph = PH.encode('utf-8')
        client_socket.send(item_header + ph + itemArray[i].encode('utf-8'))

    item = "9999" #set a value to be 9999 after the array is read through and send to client as cannot append 9999 to it due to the type of array it is
    item_header = f"{len(item):<{HEADER_LENGTH}}".encode('utf-8')
    PH = "9"* OPTION_LENGTH
    ph = PH.encode('utf-8')
    client_socket.send(item_header + ph + item.encode('utf-8'))


try:
    while True:

        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

        for notified_socket in read_sockets:

            if notified_socket == server_socket:

                client_socket, client_address = server_socket.accept()
                verified = False
                while not verified:
                    username = receive_message(client_socket)
                    password = receive_message(client_socket)
                    if username is False or password is False:
                        print("Eror in us")
                        continue


                    u = username['data']
                    p = password['data']
                    print(f'username: {u} password: {p}')

                    #check databasse for user + password
                    u_user = (u)
                    if u.isnumeric():
                        u_user = int(u)
                    p_user = str(p)
                    
                    #hash and salt password
                    salt = bcrypt.gensalt()
                    hashed = bcrypt.hashpw( p_user.encode('utf-8'), salt )
                     
                     #check if user in db
                    if u_user in uPwdDB['username'].tolist():
                        print('Username Found.')
                        #get row with user's username and password
                        row = uPwdDB[uPwdDB['username'] == u_user].index[0]
                        db_password = uPwdDB.at[row, 'password']  #get their password
                      
                        #check if password is in db
                        if bcrypt.checkpw(p_user.encode('utf-8'), db_password.encode('utf-8') ):
                            print("Correct Username and Password\n")
                            confirm = "2"
                            verified = True
                        else:
                            print("Wrong Password\n")
                            confirm = "1"
                    else:
                        print("Username Not Found\n")
                        confirm = "1"
                        verified = False

                    #send message to confirm
                    confirm_header = f"{len(confirm):<{HEADER_LENGTH}}".encode('utf-8')
                    PH = "9"* OPTION_LENGTH
                    ph = PH.encode('utf-8')
                    client_socket.send(confirm_header + ph + confirm.encode('utf-8'))



                sockets_list.append(client_socket)
                clients[client_socket] = username


                print('Accepted new connection from {}:{}, Client: {}'.format(*client_address, username['data']))
                send_wardrobe(client_socket, username['data'])


            else:

                message = receive_message(notified_socket)


                if message is False:
                    print('Closed connection from: {}'.format(clients[notified_socket]['data']))

                    sockets_list.remove(notified_socket)

                    del clients[notified_socket]

                    continue

                user = clients[notified_socket]
                client_name = int(user["data"])
                client_option = int(message["option"])
                client_data = int(message["data"])

                print(f'client_name: {str(client_name)}\n option: {str(client_option)}\n itemid: {str(client_data)}')
                #option 0 is buy 1 is returned
                if(client_option == 1):
                    #update shop database to say item is sold, change location to location of customer
                    wardrobe = {'username':client_name, 'itemID': client_data, 'status': client_option}
                    serverDB = serverDB.append(wardrobe, ignore_index = True)
                    serverDB.to_excel(DBserv)
                    #display(serverDB)
                    print ("bought")
                    #item_status = "bought"
                    #item_location = client_name

                elif(client_option == 2):
                    #item_status = "returned"
                    items = serverDB['status'].where(serverDB['itemID'] == client_data)
                    serverDB.status = numpy.where(serverDB.itemID == client_data, 2, serverDB.status)
                    serverDB.to_excel(DBserv)
                    print ("returned")


        #on exception, clear socket
        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]

finally:
    pass
