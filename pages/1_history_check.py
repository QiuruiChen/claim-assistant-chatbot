# -*- coding: utf-8 -*-
# @Author: Qiurui Chen
# @Date: 27/09/2023
# @Last Modified by: Qiurui Chen Contact: rachelchen0831@gmail.com

import streamlit as st
import time
import boto3
from datetime import datetime
import re
import openai
import streamlit as st

# this page is used for checking history data
st.set_page_config(page_title="Chat History Checking", page_icon="📈")
st.title("Chat history")
openai.api_key = st.secrets["OPENAI_API_KEY"]
AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]
REGION_NAME = st.secrets["REGION_NAME"]
OPENAI_SECRETS = st.secrets['OPENAI_API_KEY']

## Authentification
import components.authenticate as authenticate
# Check authentication when user lands on the page.
authenticate.set_st_state_vars()
# Add login/logout buttons
if st.session_state["authenticated"]:
    authenticate.button_logout()
else:
    authenticate.button_login()


dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          region_name=REGION_NAME
                          )

def savePersonData(message_list, login_mail):
    import datetime
    # Get current timestamp
    current_timestamp = datetime.datetime.now()
    # Convert timestamp to string
    string_timestamp = current_timestamp.strftime("%Y%m%d%H%M%S")

    # save pillar alignment into database
    st.warning("saving results to DB!")

    table = dynamodb.Table('claimPerPerson')
    userGenerateInfo = table.get_item(Key={'username': login_mail, "savetimestamp": string_timestamp})

    if ("Item" in userGenerateInfo):
        message = userGenerateInfo['message']
        message_list = message + message_list

        userGenerateInfo['message'] = message_list

        table.delete_item(Key={'username': login_mail, "savetimestamp": string_timestamp})
        table.put_item(Item=userGenerateInfo)
    else:
        print("no data is there, so insert items")
        #create the table
        table.put_item(
            Item = {
                'username': login_mail,
                'savetimestamp':string_timestamp,
                'message':message_list
            }
        )
    alert = st.success('Saving successfully', icon="✅")
    time.sleep(3)  # Wait for 3 seconds
    alert.empty()  # Clear the alert

def delete_history(login_mail,timestamp):
    # delete the chat history
    table = dynamodb.Table('claimPerPerson')
    try:
        table.delete_item(Key={'username': login_mail, "savetimestamp": timestamp})
        alert_plc = st.success('Delete Successfully', icon="✅")
        time.sleep(3)  # Wait for 3 seconds
        alert_plc.empty()  # Clear the alert
    except:
        error_plc = st.error('Delete Failed', icon="❌")
        time.sleep(3)  # Wait for 3 seconds
        error_plc.empty()  # Clear the alert

def retrievePersonData(login_mail):
    personClaims_table = dynamodb.Table('claimPerPerson')
    personClaims_responses = personClaims_table.scan()
    person_historys = [item for item in personClaims_responses['Items'] if item['username'] == login_mail]

    return person_historys


# if st.session_state["authenticated"] and "Underwriters" in st.session_state["user_cognito_groups"]:
if st.session_state["authenticated"]:
    login_mail = st.session_state["user_cognito_groups"]
    login_mail = "".join(login_mail)

    company_suffix = login_mail.split("@")[1]
    if(company_suffix in ["skimgroup.com","gmail.com"]): #if login with company account and personal gmail
        chatHistory = retrievePersonData(login_mail)
        chatData = [content['message'] for content in chatHistory]
        for idx,chat in enumerate(chatData):

            timestamp =chatHistory[idx]['savetimestamp']
            datetime_obj = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
            st.write("Chat:", datetime_obj)
            delete_chat = st.button("Delete", key=timestamp, on_click=delete_history,args=[login_mail,timestamp])

            # for each indivual chat, show chat history:
            for chatConetnt in chat:
                if(chatConetnt['role'] == "user"):
                    with st.chat_message("user"):
                        if (company_suffix != "skimgroup.com"):  # if you are not company staff, hide the detailed prompt
                            if (chatConetnt['content'].startswith("You are a senior brand communication strategist for Alpro. The goal is to create a new campaign slogan or message for Alpro to put on their packaging. The slogan or message is intended to convince consumers to buy Alpro, and make them feel emotionally connected to Alpro. The statements will be related to sustainability, but should be focused on the key benefits for the consumer that are a result of sustainability. You will provide 10 benefit statements")):

                                XXX = re.search(r"You will provide 10 benefit statements about '(.+?)'", chatConetnt['content']).group(1)
                                st.markdown("Give me 10 benefit statements about " + XXX + ".")
                            elif (chatConetnt['content'].startswith(
                                    "You are a senior brand communication strategist for Alpro. The goal is to create a new campaign slogan or message for Alpro to put on their packaging. The slogan or message is intended to convince consumers to buy Alpro, and make them feel emotionally connected to Alpro. The statements will be related to sustainability, but should be focused on the key benefits for the consumer that are a result of sustainability. You will provide 10 different alternative phrasings for word or phrase that I submit")):
                                XXX = re.search(r"The word or phrase is '(.+)'", chatConetnt['content']).group(1)
                                st.markdown("Give me ways to phrase " + XXX + ".")
                            elif (chatConetnt['content'].startswith(
                                    "You are a senior brand communication strategist for Alpro. The goal is to create a new campaign slogan or message for Alpro to put on their packaging. The slogan or message is intended to convince consumers to buy Alpro, and make them feel emotionally connected to Alpro. The statements will be related to sustainability, but should be focused on the key benefits for the consumer that are a result of sustainability. I will provide a claim that I would like for you to rephrase to improve it. The claim is")):
                                XXX = re.search( r"The claim is '(.+)'", chatConetnt['content']).group(1)
                                st.markdown("Give me 5 improved claims about " + XXX + ".")
                            else:
                                st.markdown(st.write(chatConetnt['content']))
                        else: #if you are company staff, show detailed prompts
                            st.write(chatConetnt['content'])

                if(chatConetnt['role'] == "assistant"):
                    with st.chat_message("assistant"):
                        st.write(chatConetnt['content'])

else:
    st.write("Please login!")
