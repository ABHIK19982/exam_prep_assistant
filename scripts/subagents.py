import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from prompt_templates.subagent_prompts import *
from langchain.agents.structured_output import ToolStrategy
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_openai.chat_models import ChatOpenAI
from langchain.agents import create_agent
from deepagents.middleware import CompiledSubAgent
from pydantic import BaseModel, Field
from scripts.get_credentials import *

class QAOutputSchema(BaseModel):
    answer: str =  Field(description = "This field will contain the answer to the question asked. ")
    explanations: list[str] | str =  Field(description = "This Field will contain the explanations for the answer returned. It will provide proper reasoning as a list of strings. ")
    sources: list[str] | str = Field(description = "This Field will contain the list of sources used to answer the question. It will be a list of strings. ")

class SupportAgentOutputSchema(BaseModel):
    error: str = Field(description = "This field will contain the error message that the suuport agent is looking into. ")
    error_description: str = Field(description = "This field will contain the description of the error along with the probable cause of the error. ")
    solution_steps: list[str] = Field(description = "This field will contain the list of probable solution to try to resolve the error")

def get_geography_qna_expert(model_type = 'gemini'):
    conf = read_config()


    if model_type == 'gemini':
        cred = get_token(conf)
        qamodel = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2,
                                         #credentials=cred,
                                         google_api_key=conf['GOOGLE']['API_KEY'])
    elif model_type == 'openai':
        qamodel = ChatOpenAI(model="gpt-5-mini", temperature=0.2, api_key=conf['OPENAI']['API_KEY'])
    else:
        cred = get_token(conf)
        qamodel = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0.2,
                                         #credentials=cred,
                                         google_api_key=conf['GOOGLE']['API_KEY'])

    qaagent = create_agent(model = qamodel, name = "geo-qna-agent",
                           response_format = ToolStrategy(QAOutputSchema),
                           system_prompt = GEO_TUTOR_PROMPT)
    qna_subagent = CompiledSubAgent(
        name = "geography-tutor",
        description = "Agent for answering and reasoning any question as well as quizzing related to the subject Geography.",
        runnable = qaagent
    )
    return qna_subagent

def get_history_qna_expert(model_type = 'gemini'):
    conf = read_config()
    if model_type == 'gemini':
        cred = get_token(conf)
        qamodel = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2,
                                         #credentials=cred,
                                         google_api_key=conf['GOOGLE']['API_KEY'])
    elif model_type == 'openai':
        qamodel = ChatOpenAI(model="gpt-5-mini", temperature=0.2, api_key=conf['OPENAI']['API_KEY'])
    else:
        cred = get_token(conf)
        qamodel = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0.2,
                                         #credentials=cred,
                                         google_api_key=conf['GOOGLE']['API_KEY'])

    qaagent = create_agent(model=qamodel, name="hist-qna-agent",
                           response_format=ToolStrategy(QAOutputSchema),
                           system_prompt=HIST_TUTOR_PROMPT)
    qna_subagent = CompiledSubAgent(
        name="history-tutor",
        description="Specialized agent for answering and reasoning any question as well as quizzing related to the subject History.",
        runnable=qaagent
    )
    return qna_subagent

def get_geography_research_expert():
    conf = read_config()
    cred = get_token(conf)
    qamodel = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.6,
                                     thinking_budget = -1, include_thoughts = True,
                                     #credentials=cred,
                                     google_api_key=conf['GOOGLE']['API_KEY'])

    qaagent = create_agent(model = qamodel, name = "geo-qna-agent",
                           response_format = ToolStrategy(QAOutputSchema),
                           system_prompt = GEO_EXPERT_PROMPT)
    qna_subagent = CompiledSubAgent(
        name = "geography-research-expert",
        description = "Agent for answering and reasoning any question as well as quizzing related to the subject Geography.",
        runnable = qaagent
    )
    return qna_subagent

def get_history_research_expert():
    conf = read_config()
    cred = get_token(conf)
    qamodel = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.6,
                                     thinking_budget=-1, include_thoughts=True,
                                     #credentials=cred,
                                     google_api_key=conf['GOOGLE']['API_KEY'])

    qaagent = create_agent(model=qamodel, name="hist-qna-agent",
                           response_format=ToolStrategy(QAOutputSchema),
                           system_prompt=HIST_EXPERT_PROMPT)
    qna_subagent = CompiledSubAgent(
        name="history-research-expert",
        description="Specialized agent for answering and reasoning any question as well as quizzing related to the subject History.",
        runnable=qaagent
    )
    return qna_subagent


def get_suppport_agent():
    conf = read_config()
    cred = get_token(conf)
    qamodel = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.3,
                                     thinking_budget=-1,
                                     #credentials=cred,
                                     google_api_key=conf['GOOGLE']['API_KEY'])

    qaagent = create_agent(model=qamodel, name="support-agent",
                           response_format= ToolStrategy(SupportAgentOutputSchema),
                           system_prompt=SUPPORT_AGENT_PROMPT)
    subagent = CompiledSubAgent(
        name="support-expert",
        description="Specialized agent for looking into any error in any task and finding probable resolutions.",
        runnable=qaagent
    )
    return subagent