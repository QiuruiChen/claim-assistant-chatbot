# -*- coding: utf-8 -*-
# @Author: Qiurui Chen
# @Date: 05/10/2023
# @Last Modified by: Qiurui Chen Contact: rachelchen0831@gmail.com
import streamlit as st
import components.authenticate as authenticate
import os
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
from llama_index import SimpleDirectoryReader

# Check authentication when user lands on the page.
authenticate.set_st_state_vars()
# Add login/logout buttons
if st.session_state["authenticated"]:
    authenticate.button_logout()
else:
    authenticate.button_login()

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        print(f"Loaded {len(docs)} docs") # Could it read pdf, csv and excel data files?
        service_context = ServiceContext.from_defaults(
            llm=OpenAI(model="gpt-3.5-turbo",
                       temperature=0.5,
                       system_prompt="You are an expert on the Streamlit Python library and your job is to answer technical questions. Assume that all questions are related to the Streamlit Python library. Keep your answers technical and based on facts – do not hallucinate features."))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index



def list_files(directory):
    file_list = []
    for root, directories, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


# if st.session_state["authenticated"] and "Underwriters" in st.session_state["user_cognito_groups"]:
if st.session_state["authenticated"]:
    login_mail = st.session_state["user_cognito_groups"]
    login_mail = "".join(login_mail)
    print("login_mail", login_mail)
    company_suffix = login_mail.split("@")[1]
    if(company_suffix == "skimgroup.com"): #if(company_suffix in ["skimgroup.com","gmail.com"]):
        st.markdown("You can upload files to your SKIM knowledge database."
                    "Please convert slides into pdf. "
                    "Currently it only supports pdf, docx, doc, and xlsx.")

        uploaded_file_raw = st.file_uploader("Choose a file",
                                             accept_multiple_files=True,
                                             type=["pdf", "doc", "docx", "xlsx"])
        # Usage
        directory_path = "./data"
        files = list_files(directory_path)
        try:
            files.remove('./data/.DS_Store')
        except:
            pass

        st.markdown("Currently these files are in SKIM database:\n\n" + "\n\n".join(files))

        if st.button("Generate"):
            if uploaded_file_raw is not None:
                for uploaded_file in uploaded_file_raw:
                    with open(os.path.join("data", uploaded_file.name), "wb") as f:
                        f.write(uploaded_file.getbuffer())
                index = load_data()
                # Persist index to disk
                index.storage_context.persist("naval_index")
                st.success("SKIM Knowledge is ready!")
            else:
                st.warning("No files are uploaded!")
    else:
        st.warning("You dont have the right to manage SKIM knowledge!") #only comapny staff have the right to manage the company content!
else:
    st.write("Please login!")