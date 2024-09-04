from typing import Optional
from abc import ABC, abstractmethod

from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

from dating_control.llms import CustomLLM
from dating_control.utils import get_logger

load_dotenv()

logger = get_logger("chats.py")


class CustomLLMChain:
    def __init__(self, llm: CustomLLM, prompt: str, history: Optional[str] = None, verbose=False) -> None:
        self.llm = llm
        self.prompt = prompt
        self.verbose = verbose
        self.inner_chain = LLMChain(llm=self.llm, prompt=self.prompt, verbose=self.verbose)
        self.history = self._init_history(history)

    @staticmethod
    def _init_history(history: Optional[str] = None) -> str:
        return history if history else "empty history"

    def _update_history(self, request: str, response: str):
        self.history = f"{self.history}\n{request}\n{response}"

    def run(self, **kwargs):
        for tries in range(3)
            response_full = self.inner_chain.run(text=kwargs["text"], history=self.history)
            if len(response_full):
                outer_response = response_full.strip()
                human_request = f"Human: {kwargs['text']}"
                response = f"Response: {outer_response}"

                self._update_history(human_request, response)
                break

        return outer_response


class BaseChat(ABC):
    def __init__(self):
        self.model = None
        self.conversation_memory = None

    @property
    def logger(self):
        return get_logger(self.__class__.__name__)

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
    def __init__(self, history: Optional[str] = None) -> None:
        super().__init__()
        self.model = None
        self.conversation_memory = None

        self._init_model()
        self._init_memory()
        self._init_prompts()
        self._init_chains(history)

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

    def _init_chains(self, history: Optional[str] = None) -> None:
        self.main_chain = CustomLLMChain(self.model, self.prompt, history=history, verbose=False)


class HistorySummaryChat:
    def __init__(self, verbose: bool = True) -> None:
        self.verbose = verbose
        self.llm = CustomLLM()
        self.prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    """
                    You are good at summarizing all thing in a world.
                    """
                ),
                HumanMessagePromptTemplate.from_template(
                    """
                    You have a conversation history:

                    {conversation}

                    end_history

                    Create a summary. Use only 30 tokens.

                    Summary:"""
                ),
            ],
        )
        self.summary_chain = LLMChain(llm=self.llm, prompt=self.prompt, verbose=self.verbose)
