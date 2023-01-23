# Log Ingestion with MongoDB Atlas Serverless, Ray & ZeroMQ




![Untitled-2022-10-06-1605 excalidraw](https://user-images.githubusercontent.com/84564830/213499031-7bd8937c-1594-4df1-80c3-47c3e4c12dcf.png)


## General Information
> The following demo aims to show the use of the MongoDB Atlas Serverless service as part of the need around the dynamic ingestion of logs.
> We will use the following technology components: 
* Pandas as the data analysis library
* ZeroMQ as the asynchronous messaging broker
* Ray as the Python framework for parallel, asychronous and distributed tasks


## Workflow
> We are going to create independent log generating modules. The execution of these processes will be done in parallel. 
> The orchestration of these executions will be done through Ray. 
> The generated log messages will be systematically transmitted to a ZeroMQ service supporting the req/rep mechanism.
> This service will forward each of the messages received to another ZeroMQ service operating in push/pull mode.
> In parallel with all this, we will have independent modules, ZeroMQ pull clients that will consume these message queues from the ZeroMQ broker, and then transmit them to a MongoDB Atlas serverless instance.
> Each of the ZeroMQ pull client module has a 1-to-1 relationship with an Atlas serverless intance.
> In short, the capture and write modules will be isolated and can have a dedicated allocation of server ressources.

### Step 1 : Provision AWS EC2 instance A - Log generating modules orchestrated through Ray
> The first instance will be hosting the log generating modules.
```
Name = log_gen_server
AMI = Amazon Linux 2 AMI (HVM) - kernel 5.10, SSD Volume Type
Architecture = 64-bit (x86)
Instance type = c5.4xlarge
Inbound security rule = SSH (TCP, 22) from your IP
```

### Step 2 : Provision AWS EC2 instance B - ZeroMQ message broker, REQ/REP and PUSH/PULL patterns
> The second instance will be hosting the log generating modules.
```
Name = zeromq_server
AMI = Amazon Linux 2 AMI (HVM) - kernel 5.10, SSD Volume Type
Architecture = 64-bit (x86)
Instance type = t2.xlarge
Inbound security rule = SSH (TCP, 22) from your IP
Inbound security rule = Custom TCP 5050 from your IP address of the first instance you previously created
Inbound security rule = Custom TCP 5252 from anywhere - or you could restrict it by choosing a subnet in which the third instance will be connected
```

### Step 3 : Provision AWS EC2 instance C - ZeroMQ PULL message client orchestratred through Ray
> The second instance will be hosting the log generating modules.
```
Name = zeromq_pull_and_atlas_serverless_client
AMI = Amazon Linux 2 AMI (HVM) - kernel 5.10, SSD Volume Type
Architecture = 64-bit (x86)
Instance type = c5.4xlarge
Inbound security rule = SSH (TCP, 22) from your IP
```

### Step 4 - MongoDB Atlas Network and Database Access Controls
> Whitelist the IP address of instance C into MongoDB Atlas
```
SECURITY > Network Access > IP Access List > Add IP Address
```
> Create a database user with read and write role to any database
```
SECURITY > Database Access - Add New Databasse User (SCRAM)
```

### Step 5 - Download GitHub Repo and Edit Parameters
> First, install Git on AWS EC2 AMI
```
sudo yum update
sudo yum install git
git clone https://github.com/JuicySantos06/dynamic-log-ingestion-mongodb-atlas-rayio-zeromq.git
```
> Edit the configuration file : params.py with the required values.
```
nano dynamic-log-ingestion-mongodb-atlas-rayio-zeromq/params.py
```
> The ZEROMQ_SERVER_IP paramater value has to be the IP address of the second AWS EC2 instance you created (i.e. AWS EC2 instance B)
> Edit both the ATLAS_PUBLIC_API_KEY and ATLAS_PRIVATE API_KEY parameters.
> The following link will guide you in creating the aforementioned keys : [Get Started with the Atlas Administration API] (https://www.mongodb.com/docs/atlas/configure-api-access/)
> Edit your MongoDB Atlas project ID : [Manage Project Settings] (https://www.mongodb.com/docs/atlas/tutorial/manage-project-settings/)
> Edit the username and password parameters with the user and password you created in the previous step


