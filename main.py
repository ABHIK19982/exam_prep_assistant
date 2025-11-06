from deepagents.backends import FilesystemBackend
from langchain.agents.middleware import TodoListMiddleware
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from prompt_templates.todo_prompts import *
from scripts.qna_tool import *
from deepagents import create_deep_agent
from deepagents.middleware import  FilesystemMiddleware, SubAgentMiddleware
from scripts.subagents import *

if __name__ == '__main__':
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
            Always consider all the past conversations while generating your answers. 
            The subagents are stateless and they wont remember any past conversations. 
            In case, there is an early stop due to MALFORMED_FUNCTION_CALL, restart the entire process once again. 
            
            #*** Instructions for Quizzing***
            During Quizzes, ask 5 multiple choice questions with 4 options in each. 
            These questions should have a single correct answer. 
            
            #**Handling Error Scenarios**
            -> In case, the get_wiki_content tool is returning an empty list, rerun the tool after modifying the search topic passed to the tool. 
            -> In general, there are any error in any tool or subagent, try to resolve the same by modifying the prompt and reruning the subagent or tool. 
            You can use the support-expert subagent as well to understand any tool/subagent failure and find probable solutions to the same. Use this subagent as your assistant whereever needed. 
            '''
    conf = read_config()
    cred = get_token(conf)
    agent = create_agent(
        name = "Competitive-exam-prep-Assistant",
        model = ChatGoogleGenerativeAI(model = "gemini-2.5-pro",credentials = cred , temperature = 0.4),
        tools = [get_wiki_content, gen_uuid, write_to_file, write_logs],
        system_prompt = sys_agent_prompt,
        middleware = [
        TodoListMiddleware(
            system_prompt = TODO_LIST_SYS_PROMPT
        ),
        SubAgentMiddleware(
          default_model = ChatGoogleGenerativeAI(model = "gemini-2.5-pro", credentials = cred, temperature = 0.4),
          subagents = [get_geography_qna_expert(), get_history_qna_expert(), get_history_research_expert(), get_geography_research_expert(), get_suppport_agent()]
        ),
        FilesystemMiddleware(
            backend = FilesystemBackend(root_dir = "/Users/abhikpramanik/Documents/pycharm_projects/CVproject/output"),
            system_prompt = '''Write to the filesystem after each and every step.
            For each user query create a new file at /Users/abhikpramanik/Documents/pycharm_projects/CVproject/output path.
            The file name should follow this format: AGENT_LOG_<timestamp yyyyMMddhhmmss>.txt. if this file exist then edit this file instead of creating a duplicate.
            Make sure for each user query we have one and only on log file in the directory. ''',
            custom_tool_descriptions={
                'ls': 'List all the files in the directory /Users/abhikpramanik/Documents/pycharm_projects/CVproject/output. This tool will be used to find any json files. ',
                'read_file': 'Read the content of a log files with the name format - TODO_<Request_id>.json. The input to this tool should be a valid file path.',
                'write_file': 'Write the Todo list for each request to a log files with the name format - TODO_<Request_id>.json. The input to this tool should be a valid file path and the content to be written to the file.',
                'edit_file': 'Use this tool to edit the content of log file with name format - TODO_<Request_id>.json. The input to this tool should be a valid file path and the content to be written to the file. Edit this file whenever there is an update to the todo List for a request'
            }
        )]
    )
    print(AIMessage(content="Hello Aspirant! How may i help you with your preparation today ? "))
    while True:
        user_input = input("Enter your query: ")

        if user_input.lower() == 'exit':
            break
        response = agent.invoke({"messages":[{"role": "user","content":user_input}]})
        print('------------------ Messages ---------------------')
        for i in response['messages']:
            if isinstance(i, HumanMessage):
                print('Human -> ', end = ' ')
            elif isinstance(i, AIMessage):
                print('AI -> ', end = ' ')
            elif isinstance(i , ToolMessage):
                print('Tool -> ', end = ' ')
            print(i)
        print('------------------ End of Messages ---------------------')
        for i in response.keys():
            if i != 'messages':
                print(i, ' -> ', response[i])

