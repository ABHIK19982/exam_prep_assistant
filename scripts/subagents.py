import os
import sys
from typing import Optional
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from prompt_templates.subagent_prompts import *
from langchain.agents.structured_output import ToolStrategy
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain.agents import create_agent
from deepagents.middleware import CompiledSubAgent
from scripts.output_schemas import *
from scripts.get_credentials import *


def get_qna_expert(model_name: Optional[str] = None):
    conf = read_config()
    target_model = model_name or "gemini-2.5-flash"

    if "gemini" in target_model:
            qamodel = ChatGoogleGenerativeAI(
            model=target_model,
            temperature=0.2,
            google_api_key=conf['GOOGLE']['API_KEY']
        )
    else:
        qamodel = ChatGoogleGenerativeAI(
            model=target_model,
            temperature=0.2
        )
    qaagent = create_agent(
        model=qamodel,
        name="qna-agent",
        response_format=ToolStrategy(QAOutputSchema),
        system_prompt=QNAAGENT_PROMPT
    )
    qna_subagent = CompiledSubAgent(
        name="qna_agent",
        description="Agent for answering and reasoning any question as well as quizzing in any topic",
        runnable=qaagent
    )
    return qna_subagent


def get_research_expert(model_name: Optional[str] = None):
    conf = read_config()
    target_model = model_name or "gemini-2.5-pro"

    if 'gemini' in target_model:
        model_kwargs = {
            "model": target_model,
            "temperature": 0.6,
            "google_api_key": conf['GOOGLE']['API_KEY']
        }
        if "pro" in target_model:
            model_kwargs.update({
                "thinking_budget": -1,
                "include_thoughts": True
            })

        qamodel = ChatGoogleGenerativeAI(**model_kwargs)
    else:
        qamodel = ChatGoogleGenerativeAI(
            model=target_model,
            temperature=0.6
        )

    qaagent = create_agent(
        model=qamodel,
        name="research-agent",
        response_format=ToolStrategy(ResearchSchema),
        system_prompt=RESEARCH_AGENT_PROMPT
    )
    qna_subagent = CompiledSubAgent(
        name="research-expert",
        description="Agent for performing deep research and analysis on any topic",
        runnable=qaagent
    )
    return qna_subagent