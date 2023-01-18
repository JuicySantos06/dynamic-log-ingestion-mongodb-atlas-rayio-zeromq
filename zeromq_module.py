import time
import zmq
import params

HOST = "localhost"

if __name__ == '__main__':

    #REQ messaging pattern definition
    context = zmq.Context()
    req_socket = context.socket(zmq.REP)
    req_socket.bind("tcp://*:" + params.ZEROMQ_REP_PORT)

    #PUSH messaging pattern definition
    context = zmq.Context()
    push_socket = context.socket(zmq.PUSH)
    push_socket.bind("tcp://" + params.ZEROMQ_SERVER_IP + ":" + params.ZEROMQ_PUSH_PORT)

    while True:
        # Wait for next request from client
        message = req_socket.recv()
        print("----------------------------------------")
        print("Received request from ZeroMQ REQ client \n" + str(message, 'utf-8'))
        print("----------------------------------------\n")

        #Send message through push_socket server
        print("-------------------------------------------------")
        print("Forwarding message to internal ZeroMQ PUSH module")
        print("------------------------------------------------- \n")
        push_socket.send_string(str(message, 'utf-8'))

        # Send reply back to client
        req_socket.send_string("Acknowledge message")