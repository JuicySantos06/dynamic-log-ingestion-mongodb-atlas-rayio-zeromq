#Parameters

#Number of log generator module to be created
LOG_GEN_WORKERS = 100

#Number of ZeroMQ pull workers to be created
PULL_WORKERS = 10

#ZeroMQ Server ip adress
ZEROMQ_SERVER_IP = "127.0.0.1"

#ZeroMQ req server port
ZEROMQ_REP_PORT = "5050"

#ZeroMQ push server port
ZEROMQ_PUSH_PORT = "5252"

#Number of log messages to be generated per batch
LOG_LOAD_BATCH = 100000

#MongoDB Atlas public api key
ATLAS_PUBLIC_API_KEY = "<INSERT-VALUE>"

#MongoDB Atlas private api key
ATLAS_PRIVATE_API_KEY = "<INSERT-VALUE>"

#MongoDB Atlas project id
ATLAS_PROJECT_ID = "<INSERT-VALUE>"

#MongoDB Atlas cloud provider
ATLAS_CLOUD_PROVIDER = "AWS"

#Cloud provider deployment region
DEPLOYMENT_REGION = "EU_WEST_1"

#MongoDB Atlas cluster name prefix
ATLAS_CLUSTER_NAME_PREFIX = "zmq-serverless"

#MongoDB Atlas username
ATLAS_USERNAME = "<INSERT-VALUE>"

#MongoDB Atlas passwrod
ATLAS_PASSWORD = "<INSERT-VALUE>"
