import json
import os
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM

load_dotenv()


llm_url = os.getenv("LOCAL_LLM_URL")


class CustomLLM(LLM):
    n: int = 0

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        resp = requests.post(llm_url, data=json.dumps({"prompt": prompt}))
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        return resp.json()["response"]

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model_name": "CustomChatModel"}

    @property
    def _llm_type(self) -> str:
        return "custom"
