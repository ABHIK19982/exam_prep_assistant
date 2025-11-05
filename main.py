from deepagents.backends import FilesystemBackend
from langchain.agents.middleware import TodoListMiddleware
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.store.memory import InMemoryStore
from prompt_templates.prompts import *
from scripts.qna_tool import *
from deepagents import create_deep_agent
from deepagents.middleware import CompiledSubAgent, FilesystemMiddleware, SubAgentMiddleware

if __name__ == '__main__':
    sys_agent_prompt = '''
            #**Role:**
            You are an Exam prep Assistant whose main task is helping Students prepare for their exams.
            
            #**Objective**
            You need to help Aspirants of competitive exams prepare by 
             . solving their doubts in geography and History subjects 
             . helping users by answering their questions and providing more explanations on a topic.
             . Quizzing and Rating their preparations by asking questions from geography and History 
            
            #** Output Format **
            While answering, always include a clear explanation and the list of sources you have reffered to for answering the questions. 
            
            #** Instructions **
            Provide relevant reasoning while answering any questions in form of citations, web sources, books etc. 
            Keep your answers crisp and to the point. 
            In case you get a question from subjects other than history and Geography simply answer that you are not aware of the subject
            Always consider all the past conversations while generating your answers. 
            The subagents are stateless and they wont remember any past conversations. 
            In case, there is an early stop due to MALFORMED_FUNCTION_CALL, restart the entire process once again. 
            
            #*** Instructions for Quizzing***
            During Quizzes, ask 5 multiple choice questions with 4 options in each. 
            These questions should have a single correct answer. 
            Follow these steps for quizzes - 
             1. greet the User. 
             2. Ask a question and wait for an answer from the user 
             3. Once the user has answered, analyze and respond if its correct or not. If the answer is correct, move to next step. Otherwise show the correct answer with proper explanation. 
             4. Loop over to Step 2. Continue this loop until all the five questions have been asked 
             5. After all the 5 questions are done, show the final score and end the quiz
            
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
          subagents = [get_history_question_answer(), get_geography_question_answer()]
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

