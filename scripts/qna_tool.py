
from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from scripts.get_credentials import *
import os

@tool(description = """This tool will be used to fetch details on any topic from Wikipedia using beautifulSoup""")
def get_wiki_content(topic):
    conf = read_config('config/web_scraps.ini')
    url = requests.get(f"{conf['WIKI']['URL']}/{topic}")
    soup = BeautifulSoup(url.content, 'html.parser')
    data = [p.text for p in soup.find_all('p')]
    return '\n'.join(data)

@tool(description = "This tool will be used to generate an UUID before starting to execute a request")
def gen_uuid():
    import uuid
    return 'REQ_'+str(uuid.uuid4())

@tool(description = "This tool will be used to write to a file on the filesystem. The input to this tool should be a valid file path and the content to be written to the file.")
def write_to_file(file_path , content):
    with open(file_path , 'a') as f:
        f.write(content+'\n')
    f.close()

@tool(description = "This tool will be used to write the output from each tool and subagents to a log file")
def write_logs(req_id, content):
    with open(f'{os.getenv("OUTPUT_LOG_LOC")}/LOG_{req_id}.log','a') as f:
        f.write(content+'\n')
    f.close()
@tool(description = "This tool will be used to read the log files containing all Quiz Questions")
def read_quiz_logs(req_id):
    with open(f'{os.getenv("OUTPUT_LOG_LOC")}/QUIZ_LOG_{req_id}.log','r') as f:
        data = f.read().split('\n')

