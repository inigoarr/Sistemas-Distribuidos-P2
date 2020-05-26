import pywren_ibm_cloud as pywren
# from cos_backend import COSBackend
import time
import pickle
import ibm_boto3
from ibm_botocore.client import Config, ClientError

N_SLAVES = 10
BUCKET = "sistemasdistribuidos2"
TIME = 0.3
config_os = {'endpoint': 'https://s3.eu-gb.cloud-object-storage.appdomain.cloud',
             'secret_key': 'a4a6ae4a4866e326ab7358b8ccf6dc291ce039e6ac0dbee0',
             'acces_key': 'ddae3ad7a436482480024fe6507f75bf'}
config_cf = {'pywren': {'storage_bucket': BUCKET},

             'ibm_cf': {'endpoint': 'https://eu-gb.functions.cloud.ibm.com',
                        'namespace': 'inigo.arriazu@estudiants.urv.cat_dev',
                        'api_key': '67bcc1e5-6e77-4c4b-abab-4c48a5e1113d:En4tKcPGEdkkvUXGACGGFkUOpV8X6ZbRKviFVjERQhxRQBRnyyoncnzbLwz4QkKZ'},

             'ibm_cos': {'endpoint': 'https://s3.eu-gb.cloud-object-storage.appdomain.cloud',
                         'private_endpoint': 'https://s3.private.eu-gb.cloud-object-storage.appdomain.cloud',
                         'api_key': 'IJh1pZFpraju8B4zTS3Czhw7PLZ4AQKtfycjeebwStF8'}}


def master(x, ibm_cos):
    write_permission_list = []
    ibm_cos.put_object(Bucket=BUCKET, Key="results.txt", Body="")
    while ibm_cos.list_objects_v2(Bucket=BUCKET, Prefix="p_write_")['KeyCount'] == 0:
        time.sleep(x)
    itemsList = sorted(ibm_cos.list_objects_v2(Bucket=BUCKET, Prefix="p_write_")['Contents'],
                       key=lambda ultimo: ultimo['LastModified'])
    while(itemsList != 0):
        ident = itemsList[0]["Key"].split("_")
        lastUpdate = ibm_cos.list_objects(
            Bucket=BUCKET, Prefix="results.txt")['Contents'][0]['LastModified']

        ibm_cos.put_object(Bucket=BUCKET, Key="write_" + str(ident[2]))
        ibm_cos.delete_object(Bucket=BUCKET, Key=itemsList[0]["Key"])
        write_permission_list.append(int(ident[2]))
        while(lastUpdate == ibm_cos.list_objects_v2(Bucket=BUCKET, Prefix="results.txt")['Contents'][0]['LastModified']):
            time.sleep(x)
        ibm_cos.delete_object(Bucket=BUCKET, Key="write_" + str(ident[2]))
        time.sleep(x)
        if ibm_cos.list_objects_v2(Bucket=BUCKET, Prefix="p_write_")['KeyCount'] > 0:
            itemsList = sorted(ibm_cos.list_objects_v2(Bucket=BUCKET, Prefix="p_write_")['Contents'],
                               key=lambda ultimo: ultimo['LastModified'])
        else:
            itemsList = 0

    return write_permission_list


def slave(id, x, ibm_cos):
    ibm_cos.put_object(Bucket=BUCKET, Key="p_write_" + str(id))
    while(ibm_cos.list_objects_v2(Bucket=BUCKET, Prefix="write_" + str(id))['KeyCount'] == 0):
        time.sleep(x)
    results = list(ibm_cos.get_object(
        Bucket=BUCKET, Key="results.txt")['Body'])
    results.append(id)
    ibm_cos.put_object(Bucket=BUCKET, Key="results.txt",
                       Body=pickle.dumps(results))


if __name__ == '__main__':
    param = []
    if (N_SLAVES <= 0 or N_SLAVES >= 100):
        N_SLAVES = 10

    print("el nnumero de esclavos es:", N_SLAVES)
    pw = pywren.ibm_cf_executor(config_cf)
    pw.call_async(master, TIME)
    for num in range(N_SLAVES):
        param.append([TIME])
    pw.map(slave, param)
    write_permission_list = pw.get_result()

    client = ibm_boto3.client("s3",
                              ibm_api_key_id="fJVjVJo8_8gU1pSjdTKenMDxtal4k3aRguqw324vdMUP",
                              ibm_service_instance_id="crn:v1:bluemix:public:cloud-object-storage:global:a/bb98325721d249ba9ba1db1dfd78fd7c:23ce5539-c8b5-460a-9ab8-3a3b71b08103::",
                              ibm_auth_endpoint="https://iam.cloud.ibm.com/identity/token",
                              config=Config(signature_version="oauth"),
                              endpoint_url='https://s3.eu-de.cloud-object-storage.appdomain.cloud')
    a = client.get_object(Bucket=BUCKET, Key="results.txt")['Body'].read()
    results = a
    if results == write_permission_list:
        print("Todo ha ido correctamente.")
    else:
        print(results)
        print(write_permission_list)
    client.delete_object(Bucket=BUCKET, Key="results.txt")
