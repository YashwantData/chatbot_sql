import os
import sqlalchemy
from langchain.sql_database import SQLDatabase
from langchain.llms import OpenAI
from langchain.agents import AgentType
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
import streamlit as st
from langchain.prompts.prompt import PromptTemplate

# storing history in session states
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state["messages"]:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with  st.chat_message("assistant"):
            st.markdown(message["content"])

#Header of the Page
st.header("Get your Database Info")

#Sidebar Content
with st.sidebar:
    key = st.text_input("Add your API Key")
    os.environ["OPENAI_API_KEY"] = key
    print(key)
    llm = OpenAI(temperature=0)
    st.markdown('''
    ## About APP:

    The app's primary resource is utilised to create::

    - [streamlit](https://streamlit.io/)
    - [Langchain](https://docs.langchain.com/docs/)
    - [OpenAI](https://openai.com/)

    ## About me:

    - [Linkedin](https://www.linkedin.com/in/yashwant-rai-2157aa28b)

    ''')

    st.write('💡All about SQL Database based chatbot, created by Yashwant Rai')

# Create an SQLAlchemy engine for the MSSQL database
db_url_1 = os.environ.get('DB_CONNECTION',
                          'mssql+pyodbc://DESKTOP-SVULHV9\SQLEXPRESS/AdventureWorksLT2022?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
# db_url_2 = os.environ.get('DB_CONNECTION','mssql+pyodbc://DESKTOP-SVULHV9\SQLEXPRESS/AdventureWorksDW2019?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')


engine = sqlalchemy.create_engine(db_url_1)

db = SQLDatabase(engine)

# Create a SQLDatabaseToolkit instance using the SQLDatabase and OpenAI instances
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Now you can use the 'toolkit' to perform SQL-related operations on your MSSQL database
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

# Accept user questions/query
query = st.chat_input(placeholder="Ask questions about your Database:")

if query:
    chat_history = []
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})
    custom_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question. At the end of standalone question add this 'Answer the question in English language.' If you do not know the answer reply with 'I am sorry'.
                            Chat History:
                            {chat_history}
                            Follow Up Input: {question}
                            Standalone question:
                            Remember to greet the user with hi welcome to pdf chatbot how can i help you? if user asks hi or hello """

    CUSTOM_QUESTION_PROMPT = PromptTemplate.from_template(custom_template)

    response = agent_executor.run(query)

    # st.write(response["answer"])
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    chat_history.append((query, response))
