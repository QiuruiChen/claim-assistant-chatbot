# -*- coding: utf-8 -*-
# @Author: Qiurui Chen
# @Date: 26/09/2023
# @Last Modified by: Qiurui Chen Contact: rachelchen0831@gmail.com

import logging
import boto3

logger = logging.getLogger(__name__)
dynamodb = boto3.resource('dynamodb')

MAX_GET_SIZE = 100  # Amazon DynamoDB rejects a get batch larger than 100 items.

# create table
def create_table(tableName):
    try:
        dynamodb.create_table(
            TableName=tableName, #pillarAlignment
            AttributeDefinitions=[
                {
                    "AttributeName": "savetimestamp", #generate the unique ID
                    "AttributeType": "S"
                },
                {
                    "AttributeName": "username",
                    "AttributeType": "S"
                }
            ],
            KeySchema=[
                {
                    "AttributeName": "savetimestamp", #generate the unique ID
                    "KeyType": "HASH"
                },
                {
                    "AttributeName": "username",
                    "KeyType": "RANGE"
                }
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 1,
                "WriteCapacityUnits": 1
            }
        )
        print("Table created successfully.")
    except Exception as e:
        print("Could not create table. Error:")
        print(e)


def list_all_tables():
    # list all tables
    dynamodb = boto3.resource('dynamodb')
    return(list(dynamodb.tables.all()))

def delete_table(tableName):
    # delete table
    dynamodb = boto3.client('dynamodb')
    try:
        dynamodb.delete_table(TableName=tableName)
        return "succeed"
    except Exception as e:
        print("delete table failed. Error:",e)
        return "failed"

def insert_data_into_table(tableName,itemData): # itemData is a dictionary, for example, {'projectID': 'Fxxxx','username': 'q.chen@skimgroup.com','prompt':["prompt1","prompt2","prompt3"], 'message':["mesage1","mesage2","mesage3"],}
    # Insert data into the table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    response = table.put_item(
        Item = itemData
    )
    return response

## batch insert messages
def batch_insert_messages(tableName, message_list): # message list is [{xxx},{xxx}]
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    with table.batch_writer() as batch:
        for message_item in message_list:
            batch.put_item(Item=message_item)
    return "batch insert messages successfully"

## read items
def read_item(tableName,projectID,username):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    # boto3 dynamodb getitem
    response = table.get_item(
        Key={
            'username': username,
            'savetimestamp': projectID
        }
    )
    return(response['Item'])

def scan_items(tableName):
    ## Scan items =========
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    response = table.scan()
    # response['Items']
    return(response['Items'])

    # response_items = [item['projectID'] =="F71923" for item in response['Items']]
    # print("response_items")
    # print(response_items)

# ## update items ==========
def update_items(tableName,projectID,username,update_key,update_value):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    response = table.update_item(
        Key={
            'username': username,
            'savetimestamp': projectID
        },
        UpdateExpression="set "+update_key+"=:u",
        ExpressionAttributeValues={
            ':u': update_value
        },
        ReturnValues="UPDATED_NEW"
    )
    return response


# check all tables
alltables = list_all_tables()
print(alltables)
# delete all tables, in the app, users can click save to save tables
delete_table("claimPerPerson")
# create all tables
create_table("claimPerPerson")

