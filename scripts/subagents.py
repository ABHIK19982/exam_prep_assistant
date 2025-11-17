import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from prompt_templates.subagent_prompts import *
from langchain.agents.structured_output import ToolStrategy
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from deepagents.middleware import CompiledSubAgent
from scripts.output_schemas import *
from scripts.get_credentials import *


def get_qna_expert(model_type = 'gemini'):
    conf = read_config()


    if model_type == 'gemini':
        #cred = get_token(conf)
        qamodel = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2,
                                         #credentials=cred,
                                         google_api_key=conf['GOOGLE']['API_KEY'])
    else:
        #cred = get_token(conf)
        qamodel = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0.2,
                                         #credentials=cred,
                                         google_api_key=conf['GOOGLE']['API_KEY'])

    qaagent = create_agent(model = qamodel, name = "qna-agent",
                           response_format = ToolStrategy(QAOutputSchema),
                           system_prompt = QNAAGENT_PROMPT)
    qna_subagent = CompiledSubAgent(
        name = "qna_agent",
        description = "Agent for answering and reasoning any question as well as quizzing in any topic",
        runnable = qaagent
    )
    return qna_subagent


def get_research_expert():
    conf = read_config()
    #cred = get_token(conf)
    qamodel = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.6,
                                     thinking_budget = -1, include_thoughts = True,
                                     #credentials=cred,
                                     google_api_key=conf['GOOGLE']['API_KEY'])

    qaagent = create_agent(model = qamodel, name = "research-agent",
                           response_format = ToolStrategy(ResearchSchema),
                           system_prompt = RESEARCH_AGENT_PROMPT)
    qna_subagent = CompiledSubAgent(
        name = "research-expert",
        description = "Agent for performing deep research and analysis on any topic",
        runnable = qaagent
    )
    return qna_subagent