import os
from dotenv import load_dotenv
load_dotenv('config/local.env', verbose = True, override = True)
from deepagents.backends import FilesystemBackend
from langchain.agents.middleware import TodoListMiddleware, SummarizationMiddleware
from prompt_templates.todo_prompts import *
from scripts.qna_tool import *
from deepagents.middleware import FilesystemMiddleware, SubAgentMiddleware
from scripts.subagents import *



sys_agent_prompt = '''
        #**Role:**
        You are an Exam prep Assistant whose main task is helping Students prepare for their exams.
        
        #**Objective**
        You need to help Aspirants of competitive exams prepare by 
         . solving their doubts in geography and History subjects 
         . helping users by answering their questions and providing more explanations on a topic.
         . Doing deep research on a topic provided by the user
         . Quizzing and Rating their preparations by asking questions from geography and History 
        
        #** Output Format **
        While answering, always include a clear explanation and the list of sources you have reffered to for answering the questions. 
        
        #** Instructions **
        Provide relevant reasoning while answering any questions in form of citations, web sources, books etc. 
        In case you get a question from subjects other than history and Geography simply answer that you are not aware of the subject
        The subagents are stateless and they wont remember any past conversations. 
        In case, there is an early stop due to MALFORMED_FUNCTION_CALL, restart the entire process once again. 
        
        #*** Instructions for Quizzing***
        During Quizzes, ask multiple choice questions with 4 options in each. 
        These questions should have a single correct answer. Keep asking questions until the user asks to stop. 
        Do not repeat questions. 
        
        
        '''
conf = read_config()
#cred = get_token(conf)
agent = create_agent(
    name = "Competitive-exam-prep-Assistant",
    model = ChatGoogleGenerativeAI(model = "gemini-2.5-pro",
                                   #credentials = cred ,
                                   temperature = 0.6,
                                   google_api_key=conf['GOOGLE']['API_KEY']),
    tools = [get_wiki_content, gen_uuid, write_to_file, write_logs],
    system_prompt = sys_agent_prompt,
    middleware = [
    TodoListMiddleware(
        system_prompt = TODO_LIST_SYS_PROMPT
    ),
    SubAgentMiddleware(
      default_model = ChatGoogleGenerativeAI(model = "gemini-2.5-pro",
                                             #credentials = cred,
                                             google_api_key=conf['GOOGLE']['API_KEY'],
                                             temperature = 0.4),
      subagents = [get_geography_qna_expert(), get_history_qna_expert(), get_history_research_expert(), get_geography_research_expert(), get_suppport_agent()]
    ),
    FilesystemMiddleware(
        backend = FilesystemBackend(root_dir = os.getenv("OUTPUT_LOG_LOC")),
        system_prompt = f'''Write to the filesystem after each and every step.
        For each user query create a new file at {os.getenv("OUTPUT_LOG_LOC")} path.
        The file name should follow this format: AGENT_LOG_<timestamp yyyyMMddhhmmss>.txt. If this file exist then edit this file instead of creating a duplicate.
        Make sure for each user query we have one and only on log file in the directory. ''',
    ),
    SummarizationMiddleware(
        model = ChatGoogleGenerativeAI(model = "gemini-2.5-flash-lite",
                                       #credentials = cred,
                                       google_api_key=conf['GOOGLE']['API_KEY'],temperature = 0.4),
        max_tokens_before_summary= 1500,
        messages_to_keep=10
    )]
)

def get_AI_response(messages, debug):
    #trunc_messages = messages[len(messages) - 10 if len(messages) > 10 else 0 : len(messages)]
    if not os.path.exists(os.getenv("OUTPUT_LOG_LOC")):
        os.mkdir(os.getenv('OUTPUT_LOG_LOC'),  0o755)
    response = agent.invoke({"messages":messages},{"recursion_limit": 100})
    if debug :
        for i in response['messages']:
            i.pretty_print()
    return response['messages'][-1].content

if __name__ == '__main__':
    print(TODO_LIST_SYS_PROMPT)
    print(get_AI_response("What is the cause of downfall of the mauryan empire?", debug = True))




