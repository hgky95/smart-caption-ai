import autogen
import os


class AIConfiguration:

    config_list_llama3 = [
        {
            "model": "llama3",
            "base_url": os.getenv('BASE_URL'),
            "api_key": "ollama",
        }
    ]

    web_surfer_llm_config = {
        "timeout": 600,
        "cache_seed": 11,
        "config_list": config_list_llama3,
        "temperature": 0,
    }

    summarizer_llm_config = {
        "timeout": 600,
        "cache_seed": 33,
        "config_list": config_list_llama3,
        "temperature": 0,
    }

    config_list_llava = [
        {
            "model": "llava",
            "base_url": os.getenv('BASE_URL'),
            "api_key": "ollama",
        }
    ]

    image_llm_config = {
        "config_list": config_list_llava,
        "temperature": 0.5,
        "max_tokens": 500,
        "cache_seed": 42
    }
