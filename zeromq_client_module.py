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
import pandas as pd
import json
import params

@ray.remote(scheduling_strategy="SPREAD")
def pull_client(zmq_ip,zmq_port,x,a,b,c,d,e,f,g,h):
    print("Instantiating ZeroMQ PULL worker ID : " + str(x + 1))
    context = zmq.Context()
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect("tcp://" + zmq_ip + ":" + zmq_port)
    print("Creating MongoDB Atlas serverless instance for ZeroMQ PULL worker ID : " + str(x + 1))
    cls_name = f + "-" + str(x + 1)
    mongodb_atlas_serverless_creation_status = create_atlas_serverless_instance(a,b,c,d,e,cls_name)
    if mongodb_atlas_serverless_creation_status == True:
        mongodb_client = connect_to_atlas(cls_name,g,h)
        if mongodb_client is None:
            print("Connection to MongoDB Atlas could not be established")
            return
        else:
            database_name = "log_worker_id_" + str(x)
            mongodb_client_connection = MongoClient(mongodb_client)
            mongodb_database = mongodb_client_connection[database_name]
            mongodb_collection = mongodb_database["apache"]
            print("MongoDB database and collection have been provisionned for ZeroMQ PULL worker ID : " + str(x + 1))
            while True:
                work = consumer_receiver.recv_string()
                print("ZeroMQ PULL worker ID " + str(x + 1) + " is pulling message from ZeroMQ PUSH server")
                json_work = convert_message_format(work)
                insert_json_work = mongodb_collection.insert_one(json_work)
                if insert_json_work != None:
                    print("ZeroMQ PULL worker ID " + str(x + 1) + " inserted the message into MongoDB - ObjectId : " + str(insert_json_work.inserted_id))

def convert_message_format(message_param):
    data = message_param.split()
    last_mile_data = []
    j = 0
    while j < (len(data) - 11):
        last_mile_data.append(data[11 + j])
        j += 1
    last_data = ' '.join(last_mile_data)
    data_length = len(data)
    supp_columns=["from_ip","client_id","user_id","date_time","time_offset","request_type","ressource_fetched","http_version","response_status_code","object_size","http_referrer","user_agent_0"]
    to_be_added = data_length - len(supp_columns)
    if to_be_added > 0:
        i = 1
        while i <= to_be_added:
            add_column = "user_agent_" + str(i)
            supp_columns.append(add_column)
            i += 1
        dataframe = pd.DataFrame([data],index=[0],columns=supp_columns)
        dataframe.at[0,"user_agent_0"] = last_data
        dataframe.loc[0,"request_type"] = dataframe.loc[0,"request_type"].split('"')[1]
        dataframe.loc[0,"http_version"] = dataframe.loc[0,"http_version"].split('"')[0]
        dataframe.loc[0,"http_referrer"] = dataframe.loc[0,"http_referrer"].split('"')[1]
        k = 1
        while k <= to_be_added:
            col_name = "user_agent_" + str(k)
            dataframe.drop([col_name],axis=1,inplace=True)
            k += 1
        df_2 = dataframe.to_dict(orient="list")
        return df_2
    
def connect_to_atlas(serverless_instance_param,username_param,password_param):
        username = urllib.parse.quote_plus(username_param)
        password = urllib.parse.quote_plus(password_param)
        mongodb_conn = "mongodb+srv://" + username + ":" + password + "@" + serverless_instance_param + ".vdddl.mongodb.net/?retryWrites=true&w=majority"
        print("Connection string for serverless instance : " + mongodb_conn)
        return mongodb_conn

def create_atlas_serverless_instance(atlas_public_api_key_param,atlas_private_api_key_param,atlas_project_id_param,cloud_provider_name_param,deployment_region_param,cluster_name_param):
    true = True
    false = False
    apiPublicKey  = atlas_public_api_key_param
    apiPrivateKey = atlas_private_api_key_param
    projectId   = atlas_project_id_param
    urlCreate = "https://cloud.mongodb.com/api/atlas/v1.0/groups/" + projectId + "/serverless"
    headers = {
        'Content-Type': 'application/json',
    }
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
    response = requests.post(urlCreate,json=serverless_config,auth=HTTPDigestAuth(apiPublicKey, apiPrivateKey),headers=headers)
    while True:
        if response.status_code == 201:
            urlStatus = "https://cloud.mongodb.com/api/atlas/v1.0/groups/" + projectId + "/serverless/" + cluster_name_param
            tmp_response = requests.get(urlStatus,auth=HTTPDigestAuth(apiPublicKey, apiPrivateKey))
            serverless_instance_state = tmp_response.json()["stateName"]
            if (serverless_instance_state == "IDLE"):
                print("MongoDB Atlas serverless instance " + cluster_name_param + " is ready")
                return True

if __name__ == '__main__':
    ray.init()
    parser = argparse.ArgumentParser(__file__, description="Distributed ZeroMQ Pull Consumers with Ray")
    parser.add_argument("--pull-workers", "-pw", dest='num_pull_workers', help="Number of ZeroMQ pull workers to generate", type=int, default=1)
    parser.add_argument("--zeromq-push-server-ip", "-zmqpsip", dest='zeromq_push_server_ip', help="IP address of ZeroMQ Push server", type=str)
    parser.add_argument("--zeromq-push-server-port", "-zmqpsport", dest='zeromq_push_server_port', help="port address of ZeroMQ Push server", type=str)
    parser.add_argument("--atlas-public-api-key", "-apubkey", dest="atlas_public_api_key", help="MongoDB Atlas public API key", type=str)
    parser.add_argument("--atlas-private-api-key", "-aprikey", dest="atlas_private_api_key", help="MongoDB Atlas private API key", type=str)
    parser.add_argument("--atlas-project-id", "-aprjid", dest="atlas_project_id", help="MongoDB Atlas project ID", type=str)
    parser.add_argument("--cloud-provider-name", "-cpn", dest="cloud_provider_name", help="Cloud provider name", type=str)
    parser.add_argument("--deployment-region", "-dr", dest="deployment_region", help="Deployment region", type=str)
    parser.add_argument("--cluster-name", "-cn", dest="cluster_name", help="Cluster name", type=str)
    parser.add_argument("--username", "-usr", dest="username", help="Atlas username", type=str)
    parser.add_argument("--password", "-pwd", dest="password", help="Atlas username's password", type=str)
    args = parser.parse_args()
    tmp_result = []
    for i in range(args.num_pull_workers):
        tmp_result.append(pull_client.remote(params.ZEROMQ_SERVER_IP,params.ZEROMQ_PUSH_PORT,i,params.ATLAS_PUBLIC_API_KEY,params.ATLAS_PRIVATE_API_KEY,params.ATLAS_PROJECT_ID,params.ATLAS_CLOUD_PROVIDER,params.DEPLOYMENT_REGION,params.ATLAS_CLUSTER_NAME_PREFIX,params.ATLAS_USERNAME,params.ATLAS_PASSWORD))
        time.sleep(15)
    ray.get(tmp_result)
