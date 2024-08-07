import os
from typing import Any, Dict, List, Optional
import re
import requests
import json
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.chains import LLMChain

load_dotenv()


class CustomLLM(LLM):
    n: int = 0

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        import json

        import requests
        resp = requests.post("http://localhost:4321/query", data=json.dumps({"prompt": prompt}))
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        return resp.json()["response"]

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model_name": "CustomChatModel"}

    @property
    def _llm_type(self) -> str:
        return "custom"



class CustomLLMChain:
    def __init__(self, llm: CustomLLM, prompt: str, verbose=False) -> None:
        self.llm = llm
        self.prompt = prompt
        self.verbose = verbose
        self.inner_chain = LLMChain(llm=self.llm, prompt=self.prompt, verbose=self.verbose)
        self.history = "empty history"

    def _update_history(self, request: str, response: str):
        # print(f"prev self.history: {self.history}")
        # print("******************")
        # print()
        # print(f"request: {request}")
        # print()
        # print(f"response: {response}")
        # print()
        self.history = f"{self.history}\n{request}\n{response}"
        # print(f"updated self.history: {self.history}")
        # print()
        # print("########################")
        # print()

    def run(self, **kwargs):
        response_full = self.inner_chain.run(text=kwargs["text"], history=self.history)

        print("********************")
        print(response_full)
        print("********************")

        dialog = response_full[list(re.finditer("Human", response_full))[0].end():]
        human_request = "Human: " + dialog[list(re.finditer("end_history", dialog))[-1].end(): list(re.finditer("BfBot response", dialog))[-1].start()].strip()  # noqa: E501
        response = dialog[list(re.finditer("BfBot response", dialog))[-1].start():].strip()

        self._update_history(human_request, response)

        return response
    
    
if __name__ == "__main__":
    llm = CustomLLM()
    prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
        """
        You are a boyfriend bot. Your name is bfBot. 
        Introduce yourself once. 
        You ask questions and try to make a human more happy.
        try to find out about the history of people.
        YOU MUST GIVE A RESPONSE. THATS ALL.
        """
                ),
                HumanMessagePromptTemplate.from_template(
                    """
        start history

{history}

        end_history

        {text}
        
BfBot response:"""
                ),
            ],
        )
    chain = CustomLLMChain(llm=llm, prompt=prompt)
    
    chain.run(text="hello")
    chain.run(text="how are you?")
    chain.run(text="how old are you?")