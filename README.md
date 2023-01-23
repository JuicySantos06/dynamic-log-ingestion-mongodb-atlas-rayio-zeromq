# Log Ingestion with MongoDB Atlas Serverless, Ray & ZeroMQ




![Untitled-2022-10-06-1605 excalidraw](https://user-images.githubusercontent.com/84564830/213499031-7bd8937c-1594-4df1-80c3-47c3e4c12dcf.png)


## General Information
> The following demo aims to show the use of the MongoDB Atlas Serverless service as part of the need around the dynamic ingestion of logs.
> We will use the following technology components: 
* Pandas as the data analysis library
* ZeroMQ as the asynchronous messaging broker
* Ray as the Python framework for parallel, asychronous and distributed tasks.


## Workflow
> We are going to create independent log generating modules. The execution of these processes will be done in parallel. 
> The orchestration of these executions will be done through Ray. 
> The generated log messages will be systematically transmitted to a ZeroMQ service supporting the req/rep mechanism.
> This service will forward each of the messages received to another ZeroMQ service operating in push/pull mode.
> In parallel with all this, we will have independent modules, ZeroMQ pull clients that will consume these message queues from the ZeroMQ broker, and then transmit them to a MongoDB Atlas serverless instance.
> Each of the ZeroMQ pull client module has a 1-to-1 relationship with an Atlas serverless intance.
> In short, the capture and write modules will be isolated and can have a dedicated allocation of server ressources.

### Step 1 : Provision 3 AWS EC2 instances
