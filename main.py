import os
#from dotenv import load_dotenv
import openai
import requests
import json
import argparse

import time
import logging
from datetime import datetime
import streamlit as st

ASSISTANT_ID = "asst_EOtEe4M07VFzKfXdiNjMw6QH"
BASE_URL = "https://gw.petgenius.info"
AUTH_HEADER = {"Authorization": "Basic d3NmYXJtaW5hX3plbmRlc2s6Vy1zMzEzMkAkemVuZA=="}

def initialize_client(api_key):
    return openai.OpenAI(api_key=api_key)


def parse_json_and_list_values(json_string):
    """
    Converts a JSON string to a list of key-value tuples.

    Parameters:
    json_string (str): A string containing JSON formatted data.

    Returns:
    list of tuples: Each tuple contains a key and its corresponding value, or an empty list if JSON is invalid.
    """
    try:
        # Parse the JSON string into a Python dictionary
        parsed_data = json.loads(json_string)
        # Convert the dictionary into a list of tuples and return
        return [(key, value) for key, value in parsed_data.items()]
    except json.JSONDecodeError as e:
        # Handle the exception if json_string is not a valid JSON and return an empty list
        print(f"Error decoding JSON: {e}")
        return []


def find_customer_bymail(email):
    payload = {
        "country": "US",
        "customerId": "",
        "email": email,
        "lite": False,
        "name": "",
        "phone": "",
        "primaryContactOnly": False,
        "surname": ""
    }
    url = BASE_URL + "/wfservice/z1/customers/list"
    response = requests.post(url, headers=AUTH_HEADER, json=payload)
    print(response.json())
    return response.json()

# API function to list pets
def list_pets(country, customer_id, lite, pet_id):
    payload = {
        "country": country,
        "customerId": customer_id,
        "lite": lite,
        "petId": pet_id
    }
    url = BASE_URL + "/wfservice/z1/pets/list"
    response = requests.post(url, headers=AUTH_HEADER, json=payload)
    print(response.json())
    return response.json()
    

def add_pet(customer_id, typePet, petName, gender, country, weight, breed = "", birthday =  "", body_condition =  "", daily_activities =  "" , gestation =  "", lactation =  "", life_stage  =  "", neutered =  "", pet_id =  "", size =  ""):
    payload = {
        "birthday": birthday,
        "type" : typePet,
        "bodyCondition": body_condition,
        "breed": breed,
        "country": country,
        "customerId": customer_id,
        "dailyActivities": daily_activities,
        "gender": gender,
        "gestation": gestation,
        "lactation": lactation,
        "lifeStage": life_stage,
        "name": petName,
        "neutered": neutered,
        "petId": pet_id,
        "size": size,
        "weight": weight
    }
    url = BASE_URL + "/wfservice/z1/pets/add"
    response = requests.post(url, headers=AUTH_HEADER, json=payload)
    print(response.json())
    return response.json()

def process_message_with_citations(message):
    """Extract content and annotations from the message and format citations as footnotes."""
    message_content = message.content[0].text
    annotations = (
        message_content.annotations if hasattr(message_content, "annotations") else []
    )
    citations = []

    # Iterate over the annotations and add footnotes
    for index, annotation in enumerate(annotations):
        # Replace the text with a footnote
        message_content.value = message_content.value.replace(
            annotation.text, f" [{index + 1}]"
        )

        # # Gather citations based on annotation attributes
        # if file_citation := getattr(annotation, "file_citation", None):
        #     # Retrieve the cited file details (dummy response here since we can't call OpenAI)
        #     cited_file = {
        #         "filename": "cryptocurrency.pdf"
        #     }  # This should be replaced with actual file retrieval
        #     citations.append(
        #         f'[{index + 1}] {file_citation.quote} from {cited_file["filename"]}'
        #     )
        # elif file_path := getattr(annotation, "file_path", None):
        #     # Placeholder for file download citation
        #     cited_file = {
        #         "filename": "cryptocurrency.pdf"
        #     }  # TODO: This should be replaced with actual file retrieval
        #     citations.append(
        #         f'[{index + 1}] Click [here](#) to download {cited_file["filename"]}'
        #     )  # The download link should be replaced with the actual download path

    # Add footnotes to the end of the message content
    full_response = message_content.value + "\n\n" + "\n".join(citations)
    return full_response




def main(api_key):
    client = initialize_client(api_key)

    # Outras funções e o restante do código...
    assis_id = "asst_VgdE1cNOaYsfSq3x47cWtYwO"

    # Initialize all the session
    if "file_id_list" not in st.session_state:
        st.session_state.file_id_list = []

    if "start_chat" not in st.session_state:
        st.session_state.start_chat = False

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None


    # Set up our front end page
    st.set_page_config(page_title="Genius Nutritional consultant", page_icon=":books:")


    # # ==== Function definitions etc =====
    # def upload_to_openai(filepath):
    #     with open(filepath, "rb") as file:
    #         response = client.files.create(file=file.read(), purpose="assistants")
    #     return response.id


    # # === Sidebar - where users can upload files
    # file_uploaded = st.sidebar.file_uploader(
    #     "Upload a file to be transformed into embeddings", key="file_upload"
    # )

    # # Upload file button - store the file ID
    # if st.sidebar.button("Upload File"):
    #     if file_uploaded:
    #         with open(f"{file_uploaded.name}", "wb") as f:
    #             f.write(file_uploaded.getbuffer())
    #         another_file_id = upload_to_openai(f"{file_uploaded.name}")
    #         st.session_state.file_id_list.append(another_file_id)
    #         st.sidebar.write(f"File ID:: {another_file_id}")

    # Display those file ids
    # if st.session_state.file_id_list:
    #     st.sidebar.write("Uploaded File IDs:")
    #     for file_id in st.session_state.file_id_list:
    #         st.sidebar.write(file_id)
    #         # Associate each file id with the current assistant
    #         assistant_file = client.beta.assistants.files.create(
    #             assistant_id=assis_id, file_id=file_id
    #         )
    # Define the function to process messages with citations

    #chat_thread = client.beta.threads.create()
    # Button to initiate the chat session
    if st.sidebar.button("Start Chatting..."):
        # st.write("clicou")
    #    if st.session_state.file_id_list:
        # Create a new thread for this chat session
        chat_thread = client.beta.threads.create()
        # st.write("Chat Thread ID:", chat_thread.id)
        # st.write("Assistant ID:", assis_id)
        
        st.session_state.thread_id = chat_thread.id
        # st.write(st.session_state.thread_id)

    #    else:
            # st.sidebar.warning(
            #     "No files found. Please upload at least one file to get started."
            # )

    # chat_thread = client.beta.threads.create()
    # st.session_state.thread_id = chat_thread.id
    # st.session_state.start_chat = True
    # the main interface ...
    st.title("Genius Nutritional Consultant")
    st.write("Test interface")


    # Check sessions
    # if st.session_state.start_chat  == True:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4-turbo"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show existing messages if any...
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # chat input for the user
    if prompt := st.chat_input("What's new?"):
        # Add user message to the state and display on the screen
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # st.write("Vai escrever")
        # add the user's message to the existing thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id, role="user", content=prompt
        )

        # Create a thread with a message.
        #chat_thread
        #     messages=[
        #         {
        #             "role": "user",
        #             # Update this with the query you want to use.
        #             "content": "Hi",
        #         }
        #     ]
        # )
        # st.write("Thread ID:", st.session_state.thread_id)
        # # Create a run with additioal instructions
        # run = client.beta.threads.runs.create(
        #     thread_id=st.session_state.thread_id,
        #     assistant_id=assis_id,
        #     # instructions="""Please answer the questions using the knowledge provided in the files.
        #     # when adding additional information, make sure to distinguish it with bold or underlined text.""",
        # )
        st.write("**********************************************************************************")
        st.write(st.session_state.thread_id)
        st.write(ASSISTANT_ID)
        # Submit the thread to the assistant (as a new run).
        run = client.beta.threads.runs.create(thread_id=st.session_state.thread_id, assistant_id=ASSISTANT_ID)
        

        tool_outputs = []
        # Show a spinner while the assistant is thinking...
        with st.spinner("Wait... Generating response..."):
            while run.status != "completed":
                # check_messages(client, run) 
                print(st.session_state.thread_id)
                print(run.status)
                time.sleep(1)
                # st.write("Run ID:", run.id)
                if run.status == "requires_action":
                    # Loop through each tool in the required action section
                    for tool in run.required_action.submit_tool_outputs.tool_calls:
                        print(tool.function.name)
                        arguments = list(parse_json_and_list_values(tool.function.arguments))
                        if tool.function.name == "find_customer_by_email":
                            print(arguments)
                            mail = arguments[0]
                            strcall = ""
                            strcall = json.dumps(find_customer_bymail(mail[1]), indent=2)
                            tool_outputs.append({
                            "tool_call_id": tool.id,
                            "output": str.replace( strcall, "\n", "")
                            })
                        if tool.function.name == "list_pets":
                            print(arguments)
                            Country = arguments[0]
                            CustomerID = arguments[1]
                            strcall = ""
                            strcall = json.dumps(list_pets(Country[1], CustomerID[1], "", ""), indent=2)
                            tool_outputs.append({
                            "tool_call_id": tool.id,
                            "output": str.replace( strcall, "\n", "")
                            })
                        if tool.function.name == "add_pet":
                            print(arguments)
                            typepet = arguments[1]
                            Name = arguments[2]
                            CustomerID = arguments[0]
                            Gender = arguments[3]
                            Country = arguments[4]
                            strcall = ""
                            strcall = json.dumps(add_pet(petName=Name, country=Country, customer_id=CustomerID, typePet=typepet, gender=Gender), indent=2)
                            tool_outputs.append({
                            "tool_call_id": tool.id,
                            "output": str.replace( strcall, "\n", "")
                            })
                    # Submit all tool outputs at once after collecting them in a list
                if tool_outputs:
                    try:
                        run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id,
                        tool_outputs= tool_outputs
                        )
                        time.sleep(5)
                        tool_outputs = []
                        print("Tool outputs submitted successfully.")
                    except Exception as e:
                        print("Failed to submit tool outputs:", e)
                        tool_outputs= []
                else:
                    print("No tool outputs to submit.")
                    tool_outputs= []
    
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id, run_id=run.id
                    
                )
            # Retrieve messages added by the assistant
            check_messages(client, run)        
            # # Retrieve messages added by the assistant
            # messages = client.beta.threads.messages.list(
                
            #     thread_id=st.session_state.thread_id
            # )
            # # st.write("Messages", messages)
            # # Process and display assis messages
            # assistant_messages_for_run = [
            #     message
            #     for message in messages
            #     if message.run_id == run.id and message.role == "assistant"
            # ]

            # for message in assistant_messages_for_run:
            #     # st.write("Message", message)
            #     full_response = process_message_with_citations(message)
            #     st.session_state.messages.append(
            #         {"role": "assistant", "content": full_response}
            #     )
            #     with st.chat_message("assistant"):
            #         st.markdown(full_response, unsafe_allow_html=True)

    else:
        # Promopt users to start chat
        st.write(
            "Say hello to the Genius Nutritional Consulant"
        )

def check_messages(client, run):
    messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )
    if not messages:
        return
            # st.write("Messages", messages)
            # Process and display assistant messages, sorting by last added first
    assistant_messages_for_run = [
                message
                for message in messages
                if message.run_id == run.id and message.role == "assistant"
            ]

            # Sort messages in descending order before processing
    assistant_messages_for_run.sort(key=lambda x: x.created_at, reverse=False)
   
    for message in assistant_messages_for_run:
        print( message)
        full_response = process_message_with_citations(message)
        st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )
        with st.chat_message("assistant"):
            st.markdown(full_response, unsafe_allow_html=True)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OpenAI API key needed to run this script.')
    parser.add_argument('api_key', type=str, help='The API key for OpenAI')
    args = parser.parse_args()

    # load_dotenv()  # Ainda pode ser útil se estiver usando outras variáveis de ambiente
    main(args.api_key)

# load_dotenv()

# client = openai.OpenAI(

# # model = "gpt-4-1106-preview"  # "gpt-3.5-turbo-16k"
# ASSISTANT_ID = "asst_VgdE1cNOaYsfSq3x47cWtYwO"

# BASE_URL = "https://gw.petgenius.info"
# AUTH_HEADER = {"Authorization": "Basic d3NmYXJtaW5hX3plbmRlc2s6Vy1zMzEzMkAkemVuZA=="}
