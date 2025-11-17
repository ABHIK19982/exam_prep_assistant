from pydantic import BaseModel, Field

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

class MetaAgentSchema(BaseModel):
    Response: str = Field(description = "This field will contain the response from the meta agent. ")
    sources: list[str] = Field(description = "This field will contain the list of sources used to answer the question. It will be a list of strings. ")