import streamlit as st
import time
import numpy as np
import boto3
import openai
import streamlit as st

st.set_page_config(page_title="Claim Assistant", page_icon="📈")

st.title("Claim chatbot")
openai.api_key = st.secrets["OPENAI_API_KEY"]
AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]
REGION_NAME = st.secrets["REGION_NAME"]
OPENAI_SECRETS = st.secrets['OPENAI_API_KEY']

import components.authenticate as authenticate
# Check authentication when user lands on the page.
authenticate.set_st_state_vars()
# Add login/logout buttons
if st.session_state["authenticated"]:
    authenticate.button_logout()
else:
    authenticate.button_login()

# TODO: load history into chatbot

dynamodb = boto3.resource('dynamodb',aws_access_key_id=AWS_ACCESS_KEY_ID,  aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=REGION_NAME)
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
        #create the table
        table.put_item(
            Item = {
                'username': login_mail,
                'savetimestamp':string_timestamp,
                'message':message_list
            }
        )
    st.success('Saving successfully', icon="✅")

from llama_index import StorageContext, load_index_from_storage

# chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True, system_prompt="You are an expert on the Streamlit Python library and your job is to answer technical questions. Assume that all questions are related to the Streamlit Python library. Keep your answers technical and based on facts – do not hallucinate features.")


if "chat_engine" not in st.session_state.keys():
    # Rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir="knowlege_index")
    # Load index from the storage context
    index = load_index_from_storage(storage_context)
    st.session_state.chat_engine = index.as_chat_engine(verbose=True)


def rerun_app():
    # prompt = None
    del st.session_state.chat_engine
    del st.session_state.messages
    del st.session_state.radio_value
    # st.stop()
    # st.rerun()

# if st.session_state["authenticated"] and "Underwriters" in st.session_state["user_cognito_groups"]:
if st.session_state["authenticated"]:
    login_mail = st.session_state["user_cognito_groups"]
    login_mail = "".join(login_mail)
    company_suffix = login_mail.split("@")[1]
    if(company_suffix in ["skimgroup.com","gmail.com"]):
        if "openai_model" not in st.session_state:
            st.session_state["openai_model"] = "gpt-3.5-turbo"
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "radio_value" not in st.session_state:
            st.session_state.radio_value = "No quick fixes"

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        prompt = st.chat_input("What is up?")

        # print("len(st.session_state.messages)", len(st.session_state.messages))
        if (len(st.session_state.messages) == 0):
            placeholder = st.empty()
            with placeholder.container():
                col1,col2 = st.columns(2)
                with col1:
                    brand_name = st.text_input("Brand name",placeholder="Please enter brand name", key="init_brand_name")
                with col2:
                    product_name = st.text_input("Product name",placeholder="Please provide product name", key="init_product_name")

                st.write("Provide Benefit Statements (Please also enter brand name and product name)")
                if(company_suffix=="skimgroup.com"):
                    st.write("The detailed prompt is: You are a senior brand communication strategist for Alpro. The goal is to create a new campaign slogan or message for Alpro to put on their packaging. The slogan or message is intended to convince consumers to buy Alpro, and make them feel emotionally connected to Alpro. The statements will be related to sustainability, but should be focused on the key benefits for the consumer that are a result of sustainability. You will provide 10 benefit statements about 'XXX' to speak to users and non-users of the brand. The brand name is BRAND_NAME, as well as the product name PRODUCT_NAME. Organize the output in a bulleted list. Is that clear?")
                init_benefits = st.text_input("Give me 10 benefit statements about 'X'.",
                                              placeholder="Product Enter X",
                                              key="init_benefits")

                st.write("Phrasing Assistance (Please also enter brand name and product name)")
                if (company_suffix == "skimgroup.com"):
                    st.write("You are a senior brand communication strategist for Alpro. The goal is to create a new campaign slogan or message for Alpro to put on their packaging. The slogan or message is intended to convince consumers to buy Alpro, and make them feel emotionally connected to Alpro. The statements will be related to sustainability, but should be focused on the key benefits for the consumer that are a result of sustainability. You will provide 10 different alternative phrasings for word or phrase that I submit. The word or phrase is 'XXXX'. The brand name is BRAND_NAME, as well as the product name PRODUCT_NAME. Organize the output in a bulleted list. Is that clear?")
                init_phrase = st.text_input("Give me ways to phrase 'X'.",
                                            placeholder="Please enter X",
                                            key="init_phrase")

                st.write("Refining (Please also enter brand name and product name)")
                if (company_suffix == "skimgroup.com"):
                    st.write("You are a senior brand communication strategist for Alpro. The goal is to create a new campaign slogan or message for Alpro to put on their packaging. The slogan or message is intended to convince consumers to buy Alpro, and make them feel emotionally connected to Alpro. The statements will be related to sustainability, but should be focused on the key benefits for the consumer that are a result of sustainability. I will provide a claim that I would like for you to rephrase to improve it. The claim is 'XXX'. The brand name is BRAND_NAME, as well as the product name PRODUCT_NAME. Focus on providing better grammar, clearer and more compelling language, and use the golden rules you were provided as context. Suggest 5 improved claims to speak to users and non-users of the brand. Organize the output in a bulleted list. Is that clear?")
                init_refine = st.text_input("Give me 5 improved versions of the following claim.",
                                            placeholder="Please enter the claim",
                                            key="init_refine")

            if brand_name and product_name:
                if init_benefits:
                    prompt = "You are a senior brand communication strategist for Alpro. The goal is to create a new campaign slogan or message for Alpro to put on their packaging. The slogan or message is intended to convince consumers to buy Alpro, and make them feel emotionally connected to Alpro. The statements will be related to sustainability, but should be focused on the key benefits for the consumer that are a result of sustainability. You will provide 10 benefit statements about '"+init_benefits+"' to speak to users and non-users of the brand. The brand name is "+brand_name+", as well as the product name "+product_name+". Organize the output in a bulleted list. Is that clear?"
                    placeholder.empty()
                if init_phrase:
                    prompt = "You are a senior brand communication strategist for Alpro. The goal is to create a new campaign slogan or message for Alpro to put on their packaging. The slogan or message is intended to convince consumers to buy Alpro, and make them feel emotionally connected to Alpro. The statements will be related to sustainability, but should be focused on the key benefits for the consumer that are a result of sustainability. You will provide 10 different alternative phrasings for word or phrase that I submit. The word or phrase is '"+init_phrase+"'. The brand name is "+brand_name+", as well as the product name "+product_name+". Organize the output in a bulleted list. Is that clear?"
                    placeholder.empty()
                if init_refine:
                    prompt ="You are a senior brand communication strategist for Alpro. The goal is to create a new campaign slogan or message for Alpro to put on their packaging. The slogan or message is intended to convince consumers to buy Alpro, and make them feel emotionally connected to Alpro. The statements will be related to sustainability, but should be focused on the key benefits for the consumer that are a result of sustainability. I will provide a claim that I would like for you to rephrase to improve it. The claim is '"+init_refine+"'. The brand name is "+brand_name+", as well as the product name "+product_name+". Focus on providing better grammar, clearer and more compelling language, and use the golden rules you were provided as context. Suggest 5 improved claims to speak to users and non-users of the brand. Organize the output in a bulleted list. Is that clear?"
                    placeholder.empty()

        # add sidebar buttons
        with st.sidebar:
            # in the end, provide save DB button
            st.write("Welcome!"+login_mail)

            st.divider()
            col1,col2= st.columns([2,2])
            with col1:
                saveDB = st.button("Save to DB", key="save_to_db")
            with col2:
                newChat = st.button("New Chat", key="new_chat",on_click=rerun_app)
            st.divider()
            quick_fix = st.radio(
                "Quick Fixes",
                ["No quick fixes",
                 "Make more concise.",
                 "Fix grammar",
                 "Simplify words.",
                 "Simplify sentence structure.",
                 "Generate a catchy lead-in.",
                 "Expand on the catchy lead-in with 1-2 relevant sentences.",
                 "Make more professional.",
                 "Make more informal.",
                 "Make more informational (add proof points/the “how”/more detail)",
                 "Categorize these messages into themes."
                 ],
                key="radio_value"
                # captions=["Laugh out loud.", "Get the popcorn.", "Never stop learning."]
            )

            if st.session_state.radio_value != "No quick fixes" and saveDB is False and prompt is None and len(st.session_state.messages) != 0:
                prompt = quick_fix


        if prompt is not None:
            with st.chat_message("user"):
                show_prompt = prompt
                if (company_suffix != "skimgroup.com"): # if not skimmers, hide the prompt
                    if(prompt.startswith("You are a senior brand communication strategist for Alpro. The goal is to create a new campaign slogan or message for Alpro to put on their packaging. The slogan or message is intended to convince consumers to buy Alpro, and make them feel emotionally connected to Alpro. The statements will be related to sustainability, but should be focused on the key benefits for the consumer that are a result of sustainability. You will provide 10 benefit statements")):
                        show_prompt = "Give me 10 benefit statements about "+init_benefits+"."
                    elif(prompt.startswith("You are a senior brand communication strategist for Alpro. The goal is to create a new campaign slogan or message for Alpro to put on their packaging. The slogan or message is intended to convince consumers to buy Alpro, and make them feel emotionally connected to Alpro. The statements will be related to sustainability, but should be focused on the key benefits for the consumer that are a result of sustainability. You will provide 10 different alternative phrasings for word or phrase that I submit")):
                        show_prompt = "Give me ways to phrase "+init_phrase+"."
                    elif(prompt.startswith("You are a senior brand communication strategist for Alpro. The goal is to create a new campaign slogan or message for Alpro to put on their packaging. The slogan or message is intended to convince consumers to buy Alpro, and make them feel emotionally connected to Alpro. The statements will be related to sustainability, but should be focused on the key benefits for the consumer that are a result of sustainability. I will provide a claim that I would like for you to rephrase to improve it. The claim is")):
                        show_prompt = "Give me 5 improved claims about "+init_refine+"."

                st.markdown(show_prompt)

            st.session_state.messages.append({"role": "user", "content": show_prompt})
            with st.chat_message("assistant"):
                # message_placeholder = st.empty()
                # full_response = ""
                # for response in openai.ChatCompletion.create(
                #         model=st.session_state["openai_model"],
                #         messages=[
                #             {"role": m["role"], "content": m["content"]}
                #             for m in st.session_state.messages
                #         ],
                #         stream=True,
                # ):
                #     full_response += response.choices[0].delta.get("content", "")
                #     message_placeholder.markdown(full_response + "▌")
                # message_placeholder.markdown(full_response)
                with st.spinner("Thinking..."):
                    response = st.session_state.chat_engine.chat(prompt)
                    st.write(response.response)
                    st.session_state.messages.append({"role": "assistant", "content": response.response})

        # save to DB
        if saveDB:
            # save into database
            savePersonData(st.session_state.messages, login_mail)

    else:
        st.write("You do not have access. Only skimmers can use this functionality.Please contact the administrator.")
else:
    # if st.session_state["authenticated"]:
    #     st.write("You do not have access. Please contact the administrator.")
    # else:
    st.write("Please login!")



def saveMessageGeneration(username,projectCode,message,prompt_text,authenticated):
    if authenticated:
        # save pillar alignment into database
        st.warning("saving results to DB!")
        projectCode = projectCode.strip()  # remove starting and ending whitespace
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('messageGenerationScratch')
        userGenerateInfo = table.get_item(Key={'username': username, "projectID": projectCode})

        from datetime import datetime
        # Get today's date
        today = datetime.now()
        # Format it in 'YYYY-MM-DD' format
        date_string = today.strftime("%Y-%m-%d")

        if ("Item" in userGenerateInfo):
            userGenerateInfo = userGenerateInfo["Item"]
            message_list = userGenerateInfo['message']
            prompt_list = userGenerateInfo['prompt']
            created_date_list = userGenerateInfo['createdDate']
            message_list = message_list + message
            prompt_list = prompt_list + prompt_text
            created_date_list = created_date_list + date_string

            userGenerateInfo['message'] = message_list
            userGenerateInfo['prompt'] = prompt_list
            userGenerateInfo['createdDate'] = created_date_list
            table.delete_item(Key={'username': username, "projectID": projectCode})
            table.put_item(Item=userGenerateInfo)
        else:
            #create the table
            table.put_item(
                Item = {
                    'projectID': projectCode,
                    'username': username,
                    'prompt':prompt_text,
                    'message':message,
                    'createdDate': date_string
                }
            )
        success_plc = st.success('Saving successfully', icon="✅")
        time.sleep(3)  # Wait for 3 seconds
        success_plc.empty()  # Clear the alert
    else:
        warning_plc = st.warning("Please login in first!")
        time.sleep(3)  # Wait for 3 seconds
        warning_plc.empty()  # Clear the alert

