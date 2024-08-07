import logging
from abc import ABC

import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline

from dating_llm.utils import StdOutHandler

logger = logging.getLogger("llm_service")
logger.addHandler(StdOutHandler)
logger.setLevel(logging.DEBUG)


class BaseTextGenerationLLM(ABC):
    ...


class BaseTextGenerationLLM(BaseTextGenerationLLM):
    def __init__(
        self,
        model_name: str,
        torch_dtype=torch.float16,
        device_map: str = "cuda",
    ) -> None:
        super().__init__()
        logger.info(f"model_name: {model_name}")
        self.model_name = model_name
        self.torch_dtype = torch_dtype
        self.device_map = device_map

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        config = AutoConfig.from_pretrained(self.model_name, trust_remote_code=True)
        config.max_position_embeddings = 8096

        # bnb_config = BitsAndBytesConfig(
        #     load_in_4bit=True,
        #     bnb_4bit_quant_type="nf4",
        #     bnb_4bit_use_double_quant=True,
        # )

        bnb_config = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_threshold=200.0
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            config=config,
            quantization_config=bnb_config,
            torch_dtype=self.torch_dtype,
            trust_remote_code=True,
        )
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            torch_dtype=self.torch_dtype,
        )

    def generate(self, prompt: str) -> str:
        sequences = self.pipe(
            prompt,
            do_sample=True,
            max_new_tokens=100,
            temperature=0.98,
            top_k=50,
            top_p=0.95,
            num_return_sequences=1,
        )
        print(f"sequences[0]: {sequences[0]}")
        response = sequences[0]['generated_text']
        print(f"response: {response}")
        return response
