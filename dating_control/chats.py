import json
import logging
import os
from abc import ABC, abstractmethod

import requests
from dotenv import load_dotenv

from dating_control.utils import StdOutHandler

load_dotenv()


class CustomChain:
    def __init__(self):
        self.url: str = os.getenv("LOCAL_LLM_URL")

        self.role: str = """
            Your name is DatingBot.
            You should just ask questions about a person who you are talking right now.
            Use only 10 words.

            ##################

            {prompt}

            ##################
            Response:
        """

    def run(self, prompt: str) -> str:
        resp = requests.post(self.url, data=json.dumps({"prompt": self.role.format(prompt=prompt)}))
        return resp.json()["response"]


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
        ...

    def _init_memory(self) -> None:
        ...

    def _init_prompts(self) -> None:
        ...

    def _init_chains(self) -> None:
        self.main_chain = CustomChain()
