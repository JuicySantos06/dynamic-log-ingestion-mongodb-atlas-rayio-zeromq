import time
import zmq
import params

if __name__ == '__main__':
    req_context = zmq.Context()
    req_socket = req_context.socket(zmq.REP)
    req_socket.bind("tcp://*:" + params.ZEROMQ_REP_PORT)
    push_context = zmq.Context()
    push_socket = push_context.socket(zmq.PUSH)
    push_socket.bind("tcp://" + params.ZEROMQ_SERVER_IP + ":" + params.ZEROMQ_PUSH_PORT)
    while True:
        message = req_socket.recv()
        print("----------------------------------------")
        print("Received request from ZeroMQ REQ client \n" + str(message, 'utf-8'))
        print("----------------------------------------\n")
        print("-------------------------------------------------")
        print("Forwarding message to internal ZeroMQ PUSH module")
        print("------------------------------------------------- \n")
        push_socket.send_string(str(message, 'utf-8'))
        req_socket.send_string("Acknowledge message")