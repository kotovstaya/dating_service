import logging
import re
from abc import ABC, abstractmethod

from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

from dating_control.llms import CustomLLM
from dating_control.utils import StdOutHandler

load_dotenv()


class CustomLLMChain:
    def __init__(self, llm: CustomLLM, prompt: str, verbose=False) -> None:
        self.llm = llm
        self.prompt = prompt
        self.verbose = verbose
        self.inner_chain = LLMChain(llm=self.llm, prompt=self.prompt, verbose=self.verbose)
        self.history = "empty history"

    def _update_history(self, request: str, response: str):
        self.history = f"{self.history}\n{request}\n{response}"

    def run(self, **kwargs):
        response_full = self.inner_chain.run(text=kwargs["text"], history=self.history)

        dialog = response_full[list(re.finditer("Human", response_full))[0].end():]
        human_request = "Human: " + dialog[list(re.finditer("end_history", dialog))[-1].end(): list(re.finditer("BfBot response", dialog))[-1].start()].strip()  # noqa: E501
        response = dialog[list(re.finditer("BfBot response", dialog))[-1].start():].strip()
        outer_response = dialog[list(re.finditer("BfBot response", dialog))[-1].end():].strip()

        self._update_history(human_request, response)

        return outer_response


class BaseChat(ABC):
    def __init__(self):
        self.model = None
        self.conversation_memory = None

    @property
    def logger(self):
        logger = logging.getLogger(self.__class__.__name__)
        logger.addHandler(StdOutHandler)
        logger.setLevel(logging.DEBUG)
        return logger

    @abstractmethod
    def _init_model(self) -> None:
        ...

    @abstractmethod
    def _init_memory(self) -> None:
        ...

    @abstractmethod
    def _init_chains(self) -> None:
        ...

    @abstractmethod
    def _init_prompts(self) -> None:
        ...


class LocalUserChat(BaseChat):
    def __init__(self):
        super().__init__()
        self.model = None
        self.conversation_memory = None

        self._init_model()
        self._init_memory()
        self._init_prompts()
        self._init_chains()

    def _init_model(self) -> None:
        self.model = CustomLLM()

    def _init_memory(self) -> None:
        ...

    def _init_prompts(self) -> None:
        self.prompt = ChatPromptTemplate(
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

    def _init_chains(self) -> None:
        self.main_chain = CustomLLMChain(self.model, self.prompt, verbose=False)
