# -*- coding: utf-8 -*-
# @Author: Qiurui Chen
# @Date: 26/09/2023
# @Last Modified by: Qiurui Chen Contact: rachelchen0831@gmail.com

# -*- coding: utf-8 -*-
# @Author: Qiurui Chen
# @Date: 27/02/2023
# @Last Modified by: Qiurui Chen Contact: rachelchen0831@gmail.com

import boto3
from decouple import config
from botocore.exceptions import ClientError
from decimal import Decimal  # for dynamodb change decimal into float
import json

# from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
# from dynamodb_encryption_sdk.identifiers import CryptoAction
# from dynamodb_encryption_sdk.material_providers.aws_kms import AwsKmsCryptographicMaterialsProvider
# from dynamodb_encryption_sdk.structures import AttributeActions

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
REGION_NAME = config("REGION_NAME")
aws_cmk_id = config('AWSCMKID')

# dydb save username, instanceID

# create security group
# import requests
# ip = requests.get('https://checkip.amazonaws.com').text.strip()
# create_vpc(ip)

# 'SecurityGroupRuleId': 'sgr-02e8a4100897e9c45',
# 'GroupId': 'sg-00be75cbfd06f4f0b',

# messageTable = dyDB_resource.Table('skimVerse2')

# Create a normal table resource.
# table = boto3.resource("dynamodb").Table('skimVerse2')  # generated code confuse pylint: disable=no-member
# Create a crypto materials provider using the specified AWS KMS key.
import botocore.session

botocore_session = botocore.session.Session()
botocore_session.set_credentials(access_key=AWS_ACCESS_KEY_ID, secret_key=AWS_SECRET_ACCESS_KEY)

ddb_resource = boto3.session.Session(
    botocore_session=botocore_session,
    region_name=REGION_NAME,
)
# aws_kms_cmp = AwsKmsCryptographicMaterialsProvider(key_id=aws_cmk_id, botocore_session=botocore_session)
# # Create attribute actions that tells the encrypted table to encrypt all attributes except one.
# actions = AttributeActions(
#     default_action=CryptoAction.ENCRYPT_AND_SIGN
# )
# Use these objects to create an encrypted table resource.
# messageTable = EncryptedTable(table=table, materials_provider=aws_kms_cmp, attribute_actions=actions)

# not encrypted table
# TerminatedIns = boto3.resource(
#     'dynamodb',
#     aws_access_key_id=AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#     region_name=REGION_NAME
# ).Table('skimVerseTerminatedIns')

# messageTable, username, prompt,

messageTable = boto3.resource(
    'dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION_NAME
).Table('messageTable')


# until Sun 30 Jan 2022, AWS do not currently support the update_item method.
# when user first login, retrive all theier info
def get_project_info(projectID):
    response = messageTable.get_item(
        Key={'projectID': projectID}
        # AttributesToGet=['currentIP','insStatus','instanceId','insName','unitPrice',
        #                  'createTime','lastCost','activeTime', 'rstudioPass','rstudioUser',
        #                  'rstudioIP','sg','totalCost','totalTime','myIP','notFreq']
    )
    if "Item" in response:
        return response['Item']
    else:
        return None

def update_message(projectID,message):
    # delete the old and insert the new
    try:
        # userInfo = messageTable.get_item(Key={'userName': email})["Item"]
        userInfo = messageTable.get_item(Key={'projectID': projectID})["message"]
        userInfo['myIP'] = ip
        messageTable.delete_item(Key={'userName': email})
        messageTable.put_item(Item=userInfo)
        # messageTable.update_item(
        #     Key={
        #         'userName': email
        #     },
        #     UpdateExpression="set myIP=:p",
        #     ExpressionAttributeValues={
        #         ':p': ip,
        #     }
        # )
        return "Updated"
    except ClientError as error:
        print(error)
        return None


def update_unitPrice(email, unitPriceList):
    '''
    :param email:
    :param unitPriceList: is a float list, for example [0.02,0.04]
    :return:
    '''
    try:
        userInfo = messageTable.get_item(Key={'userName': email})["Item"]
        userInfo['unitPrice'] = [Decimal(str(price)) for price in unitPriceList]
        messageTable.delete_item(Key={'userName': email})
        messageTable.put_item(Item=userInfo)
        # unitPriceList = [Decimal(str(item)) for item in unitPriceList] #convert into dynamdb acceptes formats
        # messageTable.update_item(
        #     Key={
        #         'userName': email
        #     },
        #     UpdateExpression="set unitPrice=:p",
        #     ExpressionAttributeValues={
        #         ':p': unitPriceList,
        #     }
        # )
        return "Updated"
    except ClientError as error:
        print(error)
        return None


def update_insName(email, insNameList):
    try:
        userInfo = messageTable.get_item(Key={'userName': email})["Item"]
        userInfo['insName'] = insNameList
        messageTable.delete_item(Key={'userName': email})
        messageTable.put_item(Item=userInfo)

        # messageTable.update_item(
        #     Key={
        #         'userName': email
        #     },
        #     UpdateExpression="set insName=:p",
        #     ExpressionAttributeValues={
        #         ':p': insNameList,
        #     }
        # )
        return "Updated"
    except ClientError as error:
        print(error)
        return None


# print(update_insName('q.chen@skimgroup.com',['ins1']))

# userName,currentIP, insStatus,insId,unitPrice,createTime, lastCost,activeTime
def update_user_info(updatedUserinfo):
    '''
    :param updatedUserinfo:
    :return:
    '''
    # userInfo = messageTable.get_item(Key={'userName': email})["Item"]
    # userInfo['insName'] = insNameList
    updatedUserinfo = json.loads(json.dumps(updatedUserinfo), parse_float=Decimal)
    messageTable.delete_item(Key={'userName': updatedUserinfo['userName']})
    response = messageTable.put_item(Item=updatedUserinfo)

    # response = messageTable.update_item(
    #     Key={
    #         'userName': updatedUserinfo['userName']
    #     },
    #     AttributeUpdates={
    #         'insStatus': {
    #             'Value': updatedUserinfo['insStatus'],
    #             'Action': 'PUT'  # available options -> DELETE(delete), PUT(set), ADD(increment)
    #         },
    #         'instanceId': {
    #             'Value': updatedUserinfo['instanceId'],
    #             'Action': 'PUT'
    #         },
    #         'insName':{
    #             'Value': updatedUserinfo['insName'],
    #             'Action': 'PUT'
    #         },
    #         'activeTime': {
    #             'Value': updatedUserinfo['activeTime'],
    #             'Action': 'PUT'
    #         },
    #         'currentIP':{
    #             'Value': updatedUserinfo['currentIP'],
    #             'Action': 'PUT'
    #         },
    #         'unitPrice':{
    #              'Value': updatedUserinfo['unitPrice'],
    #               'Action': 'PUT'
    #         },
    #         'createTime':{
    #             'Value': updatedUserinfo['createTime'],
    #             'Action': 'PUT'
    #         },
    #         'lastCost': {
    #             'Value': updatedUserinfo['lastCost'],
    #             'Action': 'PUT'
    #         },
    #         'rstudioPass': {
    #             'Value': updatedUserinfo['rstudioPass'],
    #             'Action': 'PUT'
    #         },
    #         'rstudioUser': {
    #             'Value': updatedUserinfo['rstudioUser'],
    #             'Action': 'PUT'
    #         },
    #         'rstudioIP': {
    #             'Value': updatedUserinfo['rstudioIP'],
    #             'Action': 'PUT'
    #         },
    #         'sg': {
    #             'Value': updatedUserinfo['sg'],
    #             'Action': 'PUT'
    #         },
    #         'totalCost': {
    #             'Value': updatedUserinfo['totalCost'],
    #             'Action': 'PUT'
    #         },
    #         'totalTime': {
    #             'Value': updatedUserinfo['totalTime'],
    #             'Action': 'PUT'
    #         },
    #         'myIP': {
    #             'Value': updatedUserinfo['myIP'],
    #             'Action': 'PUT'
    #         },
    #         'notFreq':{
    #             'Value': updatedUserinfo['notFreq'],
    #             'Action': 'PUT'
    #         }
    #     },
    #     ReturnValues="UPDATED_NEW"  # returns the new updated values
    # )
    return response


def insert_user(insertUserInfo):
    insertData = json.loads(json.dumps(insertUserInfo), parse_float=Decimal)

    # insert into live db
    response = messageTable.put_item(
        Item=insertData
    )

    return response


def insert_terminat_data(insertData):
    # insert into terminated db
    insertData = json.loads(json.dumps(insertData), parse_float=Decimal)
    # insert into live db
    response = TerminatedIns.put_item(
        Item=insertData
    )

    return response


def delete_user(userName):
    response = messageTable.delete_item(
        Key={
            'userName': userName
        }
    )
    return response


def getAllIns():
    allItems = messageTable.scan()
    allItems = allItems['Items']

    return (allItems)


def get_all_terminatedIns():
    allItems = TerminatedIns.scan()
    allItems = allItems['Items']

    return (allItems)


def update_terminated_info(terminated_info):
    updatedUserinfo = json.loads(json.dumps(terminated_info), parse_float=Decimal)
    TerminatedIns.delete_item(Key={'userName': updatedUserinfo['userName']})
    response = TerminatedIns.put_item(Item=updatedUserinfo)
    return response

# userInfo = get_user_info('haha')
# print(userInfo)
# if user exists, it returns below content:
# {'currentIP': ['12.3.2.1.1', '12.3.1.1.1'], 'insStatus': ['running', 'stopped'], 'instanceId': ['ins1', 'ins2'], 'unitPrice': [Decimal('2.3'), Decimal('5')], 'createTime': ['2012-08-09 05:09', '2021-08-21 21:23'], 'lastCost': [Decimal('0'), Decimal('12')], 'activeTime': ['2012-09-21 12:23', '2021-09-23 12:34']}
# if user doesn't exist, it returns None

# currentIP, insStatus,insId,unitPrice,createTime, lastCost,activeTime


# userInfo = insert_user('haha',
#                        ['12.3.2.1.1', '12.3.1.1.1'],
#                        ['running', 'stopped'],
#                        ['ins1', 'ins2'],
#                        [12.3,0.8],
#                        ['2012-08-09 05:09', '2021-08-21 21:23'],
#                        [12,89],
#                        ['2012-08-09 05:09', '2021-08-21 21:23']
#                        )
# print(userInfo)

# print(delete_user('haha'))
# {'ResponseMetadata': {'RequestId': '6O5U1VJLLFFVC8TBS6Q3I0IUDFVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Wed, 12 Jan 2022 12:17:06 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '2', 'connection': 'keep-alive', 'x-amzn-requestid': '6O5U1VJLLFFVC8TBS6Q3I0IUDFVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '2745614147'}, 'RetryAttempts': 0}}

# print(update_user_info({
#     'userName':'testUser',
#     'currentIP':['12.3.2.1.1', '12.3.1.1.1'],
#     'insStatus': ['running', 'stopped'],
#     'instanceId': ['ins1', 'ins2'],
#     'unitPrice':[12.3, 0.8],
#     'createTime': ['2012-08-09 05:09', name 'insertUserInfo' is not defined '2021-08-21 22:23'],
#     'lastCost':[12,89],
#     'activeTime': ['2012-08-09 05:09', '2021-08-21 21:23']
#     }
# ))

