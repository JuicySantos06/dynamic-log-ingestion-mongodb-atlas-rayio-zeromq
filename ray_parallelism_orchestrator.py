from functools import wraps
import ray
import os
import time
import params

#Ray remote function definition, leverage every single core and spread execution over them
@ray.remote(scheduling_strategy="SPREAD")
def log_generator_call(m,n,k):
    p = 0
    while p < 100 :
        command = 'python log_generator.py -n ' + str(k) + ' -zmqsip ' + n + ' -o LOG -p web_' + str(p) + '_agent_id_' + str(m)
        os.system(command)
        p += 1


if __name__ == '__main__':
    
    ray.init()
    
    op_result = []
    for i in range(params.LOG_GEN_WORKERS):
        op_result.append(log_generator_call.remote(i,params.ZEROMQ_SERVER_IP,params.LOG_LOAD_BATCH))

    ray.get(op_result)
