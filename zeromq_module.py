import time
import zmq

HOST = "localhost"

if __name__ == '__main__':

    #REQ messaging pattern definition
    context = zmq.Context()
    req_socket = context.socket(zmq.REP)
    req_socket.bind("tcp://*:5050")

    #PUSH messaging pattern definition
    context = zmq.Context()
    push_socket = context.socket(zmq.PUSH)
    push_socket.bind("tcp://127.0.0.1:5252")

    while True:
        # Wait for next request from client
        message = req_socket.recv()
        print("Received request from ZeroMQ client : \n" + str(message, 'utf-8'))

        #Send message through push_socket server
        print("Sending message to internal ZeroMQ PUSH module \n")
        push_socket.send_string(str(message, 'utf-8'))

        # Send reply back to client
        req_socket.send_string("ACK - log data received")