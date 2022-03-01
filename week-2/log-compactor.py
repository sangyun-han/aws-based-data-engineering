from datetime import datetime
from datetime import timedelta
import os
import random
import sys
import boto3

SOURCE_DATABASE = os.getenv('SOURCE_DATABASE')
SOURCE_TABLE_NAME = os.getenv('SOURCE_TABLE_NAME')
NEW_DATABASE = os.getenv('NEW_DATABASE')
NEW_TABLE_NAME = os.getenv('NEW_TABLE_NAME')
BUCKET_NAME = os.getenv('BUCKET_NAME')
COLUMN_NAMES = os.getenv('COLUMN_NAMES', '*')
WORK_GROUP = os.getenv('WORK_GROUP', 'primary')

# default compression of JSON format : GZIP
# default compression of Parquet format : SNAPPY
# default compression of ORC format : ZLIB
CTAS_QUERY_FMT = '''CREATE TABLE {new_database}.tmp_{new_table_name}
WITH (
  external_location='{location}',
  format = 'JSON',
  bucketed_by=ARRAY['time'],
  bucket_count=1)
AS SELECT {columns}
FROM {source_database}.{source_table_name}
WHERE time between timestamp '{start_time}' and timestamp '{end_time}'
WITH DATA
'''

#tmp_compacted_log_202203010520
def drop_tmp_table(athena_client, now_timestamp, prev_timestamp):
    output_location = 's3://{bucket_name}/tmp'.format(bucket_name=BUCKET_NAME)
    prev_table_name = '{table}_{year}{month:02}{day:02}{hour:02}{minute:02}'.format(table=NEW_TABLE_NAME,year=prev_timestamp.year,month=prev_timestamp.month,day=prev_timestamp.day,hour=prev_timestamp.hour,minute=prev_timestamp.minute)
    query = 'DROP TABLE IF EXISTS {database}.tmp_{table_name}'.format(database=NEW_DATABASE,table_name=prev_table_name)

    print('[LOG] QueryString:\n{}'.format(query), file=sys.stderr)
    print('[LOG] OutputLocation: {}'.format(output_location), file=sys.stderr)

    response = athena_client.start_query_execution(
        QueryString=query,
        ResultConfiguration={
            'OutputLocation': output_location
        },
        WorkGroup=WORK_GROUP
    )
    print('[LOG] the response of DROP TABLE IF EXISTS query : ', response)
    print('[LOG] QueryExecutionId: {}'.format(response['QueryExecutionId']), file=sys.stderr)


def run_ctas(athena_client, now_timestamp, prev_timestamp):
    year, month, day, hour, minute = (now_timestamp.year, now_timestamp.month, now_timestamp.day, now_timestamp.hour, now_timestamp.minute)

    new_table_name = '{table}_{year}{month:02}{day:02}{hour:02}{minute:02}'.format(table=NEW_TABLE_NAME,year=year,month=month,day=day,hour=hour,minute=minute)

    output_location = 's3://{bucket_name}/tmp'.format(bucket_name=BUCKET_NAME)
    external_location = 's3://{bucket_name}/{dir}'.format(bucket_name=BUCKET_NAME, dir=new_table_name)

    now = '{year}-{month:02}-{day:02} {hour:02}:{minute:02}'.format(year=year, month=month, day=day, hour=hour, minute=minute)
    prev = '{year}-{month:02}-{day:02} {hour:02}:{minute:02}'.format(year=prev_timestamp.year, month=prev_timestamp.month, day=prev_timestamp.day, hour=prev_timestamp.hour, minute=prev_timestamp.minute)
    
    query = CTAS_QUERY_FMT.format(new_database=NEW_DATABASE, new_table_name=new_table_name,
                                  source_database=SOURCE_DATABASE, source_table_name=SOURCE_TABLE_NAME, columns=COLUMN_NAMES,
                                  start_time=prev, end_time=now,
                                  location=external_location)

    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': NEW_DATABASE
        },
        ResultConfiguration={
            'OutputLocation': output_location
        },
        WorkGroup=WORK_GROUP
    )
    
    print('[LOG] QueryString:\n{}'.format(query), file=sys.stderr)
    print('[LOG] ExternalLocation: {}'.format(external_location), file=sys.stderr)
    print('[LOG] OutputLocation: {}'.format(output_location), file=sys.stderr)
    print('[LOG] the response of CTAS query : ', response)
    print('[LOG] QueryExecutionId: {}'.format(response['QueryExecutionId']), file=sys.stderr)

    return new_table_name


def lambda_handler(event, context):
    client = boto3.client('athena')

    now_timestamp = datetime.now()
    prev_timestamp = now_timestamp - timedelta(minutes=5)

    run_ctas(client, now_timestamp, prev_timestamp)
    drop_tmp_table(client, now_timestamp, prev_timestamp)


    return {
        'statusCode': 200
    }