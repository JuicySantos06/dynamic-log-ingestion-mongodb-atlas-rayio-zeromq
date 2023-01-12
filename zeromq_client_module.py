import argparse
import time
import zmq
import ray
import os
import requests
from requests.auth import HTTPDigestAuth
import argparse
from pymongo import MongoClient
import urllib.parse

#ZeroMQ pull client function definition - the function will connect to a ZeroMQ Push server and retrieve data from it
@ray.remote(scheduling_strategy="SPREAD")
def pull_client(zmq_ip,zmq_port,x,a,b,c,d,e,f,g,h):
    print("Instantiating Pull worker ID : " + str(x))
    context = zmq.Context()
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect("tcp://" + zmq_ip + ":" + zmq_port)
    #Create MongoDB Atlas serverless instance which will be mapped to self
    print("Creating MongoDB Atlas serverless instance for Pull worker ID : " + str(x))
    mongodb_atlas_serverless_creation_status = create_atlas_serverless_instance(a,b,c,d,e,f)
    if mongodb_atlas_serverless_creation_status == True:
        username = urllib.parse.quote_plus(g)
        password = urllib.parse.quote_plus(h)
        #Update cluster name for each new instance
        cls_name = f + "-" + x
        mongodb_conn = "mongodb+srv://" + username + ":" + password + "@" + cls_name + ".vdddl.mongodb.net/?retryWrites=true&w=majority"
        mongodb_client = MongoClient(mongodb_conn)
        mongodb_database = mongodb_client["log_worker_id_" + x]
        mongodb_collection = mongodb_database["apache"]
        while True:
            work = consumer_receiver.recv_string()
            print("Pull worker ID " + str(x) + " is pulling message : " + work)
            mongodb_collection.insert_one(work)
            print("Pull worker ID " + str(x) + " inserted message into MongoDB : ")


#MongoDB Atlas Serverless instance function definition - the function will provision a serverless Atlas instance
def create_atlas_serverless_instance(atlas_public_api_key_param,atlas_private_api_key_param,atlas_project_id_param,cloud_provider_name_param,deployment_region_param,cluster_name_param):
    #Assign boolean value to object
    true = True
    false = False
    #Map internal variables to parameters
    apiPublicKey  = atlas_public_api_key_param
    apiPrivateKey = atlas_private_api_key_param
    projectId   = atlas_project_id_param
    #Define url object
    urlCreate = "https://cloud.mongodb.com/api/atlas/v1.0/groups/" + projectId + "/serverless"
    #Define headers
    headers = {
        'Content-Type': 'application/json',
    }
    #Define payload
    serverless_config = {
        "name": cluster_name_param,
        "providerSettings": {
            "backingProviderName": cloud_provider_name_param,
            "providerName": "SERVERLESS",
            "regionName": deployment_region_param
        },
        "serverlessBackupOptions": {
            "serverlessContinuousBackupEnabled": true
        },
        "terminationProtectionEnabled": false
    }
    #Send POST request
    response = requests.post(urlCreate,json=serverless_config,auth=HTTPDigestAuth(apiPublicKey, apiPrivateKey),headers=headers)
    #Check server response status
    while True:
        if response.status_code == 201:
            print("MongoDB Atlas serverless instance is being created...")
            urlStatus = "https://cloud.mongodb.com/api/atlas/v1.0/groups/" + projectId + "/serverless/" + cluster_name_param
            tmp_response = requests.get(urlStatus,auth=HTTPDigestAuth(apiPublicKey, apiPrivateKey))
            serverless_instance_state = tmp_response.json()["stateName"]
            print("MongoDB Atlas serverless instance state : " + serverless_instance_state)
            if (serverless_instance_state == "IDLE"):
                return True

if __name__ == '__main__':
    
    ray.init()

    #Create parser object
    parser = argparse.ArgumentParser(__file__, description="Distributed ZeroMQ Pull Consumers with Ray")
    
    #Add argument for number of ZeroMQ pull workers
    parser.add_argument("--pull-workers", "-pw", dest='num_pull_workers', help="Number of ZeroMQ pull workers to generate", type=int, default=1)

    #Add argument for ZeroMQ Push server ip address
    parser.add_argument("--zeromq-push-server-ip", "-zmqpsip", dest='zeromq_push_server_ip', help="IP address of ZeroMQ Push server", type=str)

    #Add argument for ZeroMQ Push server port
    parser.add_argument("--zeromq-push-server-port", "-zmqpsport", dest='zeromq_push_server_port', help="port address of ZeroMQ Push server", type=str)

    #Add argument for MongoDB Atlas public API key
    parser.add_argument("--atlas-public-api-key", "-apubkey", dest="atlas_public_api_key", help="MongoDB Atlas public API key", type=str)

    #Add argument for MongoDB Atlas private API key
    parser.add_argument("--atlas-private-api-key", "-aprikey", dest="atlas_private_api_key", help="MongoDB Atlas private API key", type=str)

    #Add argument for MongoDB Atlas group ID
    parser.add_argument("--atlas-project-id", "-aprjid", dest="atlas_project_id", help="MongoDB Atlas project ID", type=str)

    #Add argument for MongoDB Atlas Cloud provider name
    parser.add_argument("--cloud-provider-name", "-cpn", dest="cloud_provider_name", help="Cloud provider name", type=str)

    #Add argument for MongoDB deployment region
    parser.add_argument("--deployment-region", "-dr", dest="deployment_region", help="Deployment region", type=str)

    #Add argument for MongoDB Serverless instance cluster name
    parser.add_argument("--cluster-name", "-cn", dest="cluster_name", help="Cluster name", type=str)

    #Add argument for MongoDB username
    parser.add_argument("--username", "-usr", dest="username", help="Atlas username", type=str)

    #Add argument for MongoDB password
    parser.add_argument("--password", "-pwd", dest="password", help="Atlas username's password", type=str)

    #Parse arguments from standard input
    args = parser.parse_args()

    tmp_result = []
    for i in range(args.num_pull_workers):
        tmp_result.append(pull_client.remote(args.zeromq_push_server_ip,args.zeromq_push_server_port,i,args.atlas_public_api_key,args.atlas_private_api_key,args.atlas_project_id,args.cloud_provider_name,args.deployment_region,args.cluster_name,args.username,args.password))

    ray.get(tmp_result)


