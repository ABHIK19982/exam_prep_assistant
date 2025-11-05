from langchain.agents.structured_output import ToolStrategy
from langchain.tools import tool
import requests
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from deepagents.middleware import CompiledSubAgent
from pydantic import BaseModel, Field
from scripts.get_credentials import *
from bs4 import BeautifulSoup

class QAOutputSchema(BaseModel):
    answer: str =  Field(description = "This field will contain the answer to the question asked. ")
    explanations: list[str] | str =  Field(description = "This Field will contain the explanations for the answer returned. It will provide proper reasoning as a list of strings. ")
    sources: list[str] | str = Field(description = "This Field will contain the list of sources used to answer the question. It will be a list of strings. ")

@tool(description = """This tool will be used to fetch details on any topic from Wikipedia using beautifulSoup""")
def get_wiki_content(topic):
    conf = read_config('web_scraps.ini')
    url = requests.get(f"{conf['WIKI']['URL']}/{topic}")
    soup = BeautifulSoup(url.content, 'html.parser')
    data = [p.text for p in soup.find_all('p')]
    return data

@tool(description = "This tool will be used to generate an UUID before starting to execute a request")
def gen_uuid():
    import uuid
    return 'REQ_'+str(uuid.uuid4())

@tool(description = "This tool will be used to write to a file on the filesystem. The input to this tool should be a valid file path and the content to be written to the file.")
def write_to_file(file_path , content):
    with open(file_path , 'w') as f:
        f.write(content)
    f.close()

@tool(description = "This tool will be used to write the output from each tool and subagents to a log file")
def write_logs(req_id, content):
    with open(f'output/LOG_{req_id}.log','w') as f:
        f.write(content)
    f.close()
@tool(description = "This tool will be used to read the log files containing all Quiz Questions")
def read_quiz_logs(req_id):
    with open(f'output/QUIZ_LOG_{req_id}.log','r') as f:
        data = f.read().split('\n')

def get_geography_question_answer():
    conf = read_config()
    cred = get_token(conf)
    qamodel = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.2,
                                     credentials=cred,
                                     google_api_key=conf['GOOGLE']['API_KEY'])

    qaagent = create_agent(model = qamodel, name = "geo-qna-agent",
                           response_format = ToolStrategy(QAOutputSchema),
                           system_prompt = '''You are a teacher who has a vast knowledge in geography. 
                           Your task is to help users by answering their questions as well as quizzing them questions on specific topics. 
            Provide relevant reasoning while answering any questions in form of citations, web sources, books etc. Keep your answers crisp and to the point.
            While quizzing, not need to include any explanations. Only respond with the question and the options. 
            Strictly adhere to the fact that you will only take up requests related to geography and no other subjects. 
            ''')
    qna_subagent = CompiledSubAgent(
        name = "geography-expert",
        description = "Specialized agent for answering and reasoning any question as well as quizzing related to the subject Geography.",
        runnable = qaagent
    )
    return qna_subagent

def get_history_question_answer():
    conf = read_config()
    cred = get_token(conf)
    qamodel = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.2,
                                     credentials=cred,
                                     google_api_key=conf['GOOGLE']['API_KEY'])

    qaagent = create_agent(model=qamodel, name="hist-qna-agent",
                           response_format=ToolStrategy(QAOutputSchema),
                           system_prompt='''You are a teacher who has a vast knowledge in History. 
                           Your task is to help users by answering their questions as well as quizzing them questions on specific topics. 
            Provide relevant reasoning while answering any questions in form of citations, web sources, books etc. Keep your answers crisp and to the point.
            While quizzing, not need to include any explanations. Only respond with the question and the options. 
            Strictly adhere to the fact that you will only take up requests related to geography and no other subjects. ''')
    qna_subagent = CompiledSubAgent(
        name="history-expert",
        description="Specialized agent for answering and reasoning any question as well as quizzing related to the subject History.",
        runnable=qaagent
    )
    return qna_subagent

