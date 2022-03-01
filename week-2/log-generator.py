import json
import boto3
from datetime import datetime
import random
import uuid

Bucket = boto3.resource('s3').Bucket('learningspoons-sy')
dir_name = "generated_log"

def lambda_handler(event, context):
    device_name = "Device-" + str(random.randint(0, 10))
    metric = random.random()
    timestamp = datetime.now().isoformat(" ")
    log = "{0},{1},{2}".format(timestamp, device_name, metric)
    
    # ex> generated_log/device-log-afb50108-f453-4189-b802-db20ed9cf223.csv
    file_name = dir_name + "/" + "device-log-" + str(uuid.uuid4())+ ".csv"
    Bucket.put_object(Key=file_name, Body=log)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
