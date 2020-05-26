import pywren_ibm_cloud as pywren
import time
import pickle
import ibm_boto3
from ibm_botocore.client import Config, ClientError
N_SLAVES = 100

BUCKET = ""
TIME = 0.1

config_cf = {'pywren': {'storage_bucket': BUCKET},

             'ibm_cf': {'endpoint': '',
                        'namespace': '',
                        'api_key': ''},

             'ibm_cos': {'endpoint': '',
                         'private_endpoint': '',
                         'api_key': ''}}


def master(x, ibm_cos):
    write_permission_list = []
    ibm_cos.put_object(Bucket=BUCKET, Key="results.txt",
                       Body=pickle.dumps([0]))
    while ibm_cos.list_objects_v2(Bucket=BUCKET, Prefix="p_write_")['KeyCount'] == 0:
        time.sleep(1)
    itemsList = sorted(ibm_cos.list_objects_v2(Bucket=BUCKET, Prefix="p_write_")['Contents'],
                       key=lambda ultimo: ultimo['LastModified'])
    while(len(write_permission_list) < N_SLAVES):
        ident = itemsList[0]["Key"].split("_")
        lastUpdate = ibm_cos.list_objects(
            Bucket=BUCKET, Prefix="results.txt")['Contents'][0]['LastModified']
        ibm_cos.delete_object(Bucket=BUCKET, Key="p_write_"+str(ident[2]))
        write_permission_list.append(int(ident[2]))
        ibm_cos.put_object(Bucket=BUCKET, Key="write_" + str(ident[2]) + '_')
        while(lastUpdate == ibm_cos.list_objects_v2(Bucket=BUCKET, Prefix="results.txt")['Contents'][0]['LastModified']):
            time.sleep(x)
        ibm_cos.delete_object(
            Bucket=BUCKET, Key="write_" + str(ident[2]) + '_')
        while ((ibm_cos.list_objects_v2(Bucket=BUCKET, Prefix="p_write_")['KeyCount'] == 0)and(len(write_permission_list) < N_SLAVES)):
            time.sleep(x)
            ibm_cos.put_object(Bucket=BUCKET, Key="PRUEBA"+str(
                ibm_cos.list_objects_v2(Bucket=BUCKET, Prefix="p_write_")['KeyCount']))
        if(len(write_permission_list) < N_SLAVES):
            itemsList = sorted(ibm_cos.list_objects_v2(Bucket=BUCKET, Prefix="p_write_")['Contents'],
                               key=lambda ultimo: ultimo['LastModified'])

    return write_permission_list


def slave(id, x, ibm_cos):
    id = id+1
    ibm_cos.put_object(Bucket=BUCKET, Key="p_write_" + str(id))
    while(ibm_cos.list_objects_v2(Bucket=BUCKET, Prefix="write_" + str(id) + '_')['KeyCount'] == 0):
        time.sleep(x)
    results = pickle.loads(ibm_cos.get_object(
        Bucket=BUCKET, Key="results.txt")['Body'].read())
    if(results == [0]):
        results = []
    results.append(id)
    ibm_cos.put_object(Bucket=BUCKET, Key="results.txt",
                       Body=pickle.dumps(results))


if __name__ == '__main__':
    param = []
    if N_SLAVES >= 100:
        N_SLAVES = 99
    if N_SLAVES < 0:
        N_SLAVES = 1
    pw = pywren.ibm_cf_executor(config_cf)
    pw.call_async(master, TIME)
    for num in range(N_SLAVES):
        param.append([TIME])
    pw.map(slave, param)
    write_permission_list = pw.get_result()
    pw.clean()

    client = ibm_boto3.client("s3",
                              ibm_api_key_id="",
                              ibm_service_instance_id="",
                              ibm_auth_endpoint="",
                              config=Config(signature_version="oauth"),
                              endpoint_url='')

    results = pickle.loads(client.get_object(
        Bucket=BUCKET, Key="results.txt")['Body'].read())
    if results == write_permission_list:
        print("Todo ha ido correctamente.")
    else:
        print(results)
        print(write_permission_list)
    client.delete_object(Bucket=BUCKET, Key="results.txt")
