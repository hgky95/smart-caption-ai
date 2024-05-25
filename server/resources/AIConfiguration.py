import autogen


class AIConfiguration:
    config_list_3 = autogen.config_list_from_dotenv(
        dotenv_file_path="../.env",
        model_api_key_map={"gpt-3.5-turbo": "OPENAI_API_KEY"},
        # model_api_key_map={"gpt-4o": "OPENAI_API_KEY"},
        filter_dict={
            "model": {
                "gpt-3.5-turbo",
                # "gpt-4o",
            }
        }
    )

    web_surfer_llm_config = {
        "timeout": 600,
        "cache_seed": 11,
        "config_list": config_list_3,
        "temperature": 0,
    }

    summarizer_llm_config = {
        "timeout": 600,
        "cache_seed": 33,
        "config_list": config_list_3,
        "temperature": 0,
    }

    config_list_4 = autogen.config_list_from_dotenv(
        dotenv_file_path="../.env",
        # model_api_key_map={"gpt-4-turbo": "OPENAI_API_KEY"},
        model_api_key_map={"gpt-4o": "OPENAI_API_KEY"},
        filter_dict={
            "model": {
                # "gpt-4-turbo",
                "gpt-4o",
            }
        }
    )

    image_llm_config = {
        "config_list": config_list_4,
        "temperature": 0.5,
        "max_tokens": 500,
        "cache_seed": 42
    }
