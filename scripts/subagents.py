import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from prompt_templates.subagent_prompts import *
from langchain.agents.structured_output import ToolStrategy
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from deepagents.middleware import CompiledSubAgent
from pydantic import BaseModel, Field
from scripts.get_credentials import *

class QAOutputSchema(BaseModel):
    answer: str =  Field(description = "This field will contain the answer to the question asked. ")
    explanations: list[str] | str =  Field(description = "This Field will contain the explanations for the answer returned. It will provide proper reasoning as a list of strings. ")
    sources: list[str] | str = Field(description = "This Field will contain the list of sources used to answer the question. It will be a list of strings. ")

class ResearchSchema(BaseModel):
    topic: str =  Field(description = "This field will contain the name of the topic that the research agent is looking into. ")
    thoughts: list[str] | str = Field(description = "This Field will contain the chain of thought that the agent is doing to answer the question. It will be a list of strings. ")
    synopsis: str = Field(description = "This field will contain the research that the agent does")
    sources: list[str] | str = Field(description = "This Field will contain the list of sources used to answer the question. It will be a list of strings. ")

class SupportAgentOutputSchema(BaseModel):
    error: str = Field(description = "This field will contain the error message that the suuport agent is looking into. ")
    error_description: str = Field(description = "This field will contain the description of the error along with the probable cause of the error. ")
    solution_steps: list[str] = Field(description = "This field will contain the list of probable solution to try to resolve the error")

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