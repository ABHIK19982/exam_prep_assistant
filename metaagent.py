import os
from functools import lru_cache
from typing import Optional
from deepagents.backends import FilesystemBackend
from langchain.agents.middleware import TodoListMiddleware, SummarizationMiddleware
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from prompt_templates.todo_prompts import *
from scripts.qna_tool import *
from deepagents.middleware import FilesystemMiddleware, SubAgentMiddleware
from scripts.subagents import *


sys_agent_prompt = METAAGENT_PROMPT
conf = read_config()

AVAILABLE_MODELS = [
    {"id": "gemini-2.5-flash", "label": "Gemini 2.5 Flash"},
    {"id": "gemini-2.5-flash-lite", "label": "Gemini 2.5 Flash Lite"},
    {"id": "gemini-2.5-pro", "label": "Gemini 2.5 Pro"},
    {"id": "openai/gpt-oss-20b:fireworks-ai", "label": "GPT OSS:20B"},
    {"id": "MiniMaxAI/MiniMax-M2:novita", "label":"MiniMax-M2"}
]
DEFAULT_MODEL = AVAILABLE_MODELS[0]["id"]
_MODEL_IDS = {model["id"] for model in AVAILABLE_MODELS}


def _resolve_model(model_name: Optional[str]) -> str:
    if model_name and model_name in _MODEL_IDS:
        return model_name
    return DEFAULT_MODEL


@lru_cache(maxsize=8)
def _build_agent(model_name: str):
    selected_model = _resolve_model(model_name)
    if 'gpt' in selected_model or 'MiniMax' in selected_model:
        default_subagent_model = ChatOpenAI(
            model=selected_model,
            base_url = conf['OPENAI']['INFERENCE_PROVIDER'],
            temperature=0.4,
            api_key = conf['HUGGING_FACE']['HF_TOKEN']
        )
        base_model = ChatOpenAI(
            model=selected_model,
            base_url = conf['OPENAI']['INFERENCE_PROVIDER'],
            temperature=0.4,
            api_key = conf['HUGGING_FACE']['HF_TOKEN']
        )
    elif 'gemini' in  selected_model:
        default_subagent_model = ChatGoogleGenerativeAI(
            model=selected_model,
            google_api_key=conf['GOOGLE']['API_KEY'],
            temperature=0.4
        )
        base_model = ChatGoogleGenerativeAI(
            model=selected_model,
            google_api_key=conf['GOOGLE']['API_KEY'],
            temperature=0.2
        )
    else:
        default_subagent_model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=conf['GOOGLE']['API_KEY'],
            temperature=0.4
        )
        base_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                               # credentials = cred ,
                               temperature=0.6,
                               google_api_key=conf['GOOGLE']['API_KEY']),

    return create_agent(
        name="Competitive-exam-prep-Assistant",
        model= base_model,
        tools=[get_wiki_content, gen_uuid],
        system_prompt=sys_agent_prompt,
        middleware=[
            TodoListMiddleware(
                system_prompt=TODO_LIST_SYS_PROMPT
            ),
            SubAgentMiddleware(
                default_model=default_subagent_model,
                subagents=[get_qna_expert(selected_model), get_research_expert(selected_model)]
            ),
            FilesystemMiddleware(
                backend=FilesystemBackend(root_dir=os.getenv("OUTPUT_LOG_LOC")),
                system_prompt=f'''Write to the filesystem after each and every step.
        For each user query create a new file at {os.getenv("OUTPUT_LOG_LOC")} path.
        The file name should follow this format: AGENT_LOG_<timestamp yyyyMMddhhmmss>.txt. If this file exist then edit this file instead of creating a duplicate.
        Make sure for each user query we have one and only on log file in the directory. ''',
            ),
            SummarizationMiddleware(
                model=ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash-lite",
                    google_api_key=conf['GOOGLE']['API_KEY'],
                    temperature=0.4
                ),
                max_tokens_before_summary=1500,
                messages_to_keep=10
            )
        ]
    )


def get_AI_response(messages, debug, model_name=None):
    trunc_messages = messages[len(messages) - 10 if len(messages) > 10 else 0 : len(messages)]
    if not os.path.exists(os.getenv("OUTPUT_LOG_LOC")):
        os.mkdir(os.getenv('OUTPUT_LOG_LOC'),  0o755)
    agent = _build_agent(_resolve_model(model_name))
    response = agent.invoke({"messages": trunc_messages}, {"recursion_limit": 100})
    if debug:
        for i in response['messages']:
            i.pretty_print()
    return response['messages'][-1].content


if __name__ == '__main__':
    print(TODO_LIST_SYS_PROMPT)
    print(get_AI_response("What is the cause of downfall of the mauryan empire?", debug=True))
