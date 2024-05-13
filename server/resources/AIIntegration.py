import autogen
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
from autogen.agentchat.contrib.web_surfer import WebSurferAgent

img_url = "https://ichef.bbci.co.uk/news/1024/cpsprodpb/1567B/production/_133257678_gettyimages-2150435928.jpg.webp"

config_list_3 = autogen.config_list_from_dotenv(
    dotenv_file_path="../.env",
    model_api_key_map={"gpt-3.5-turbo": "OPENAI_API_KEY"},
    filter_dict={
        "model": {
            "gpt-3.5-turbo",
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
    "cache_seed": None,
    "config_list": config_list_3,
    "temperature": 0,
}

web_surfer = WebSurferAgent(
    "web_surfer",
    llm_config=web_surfer_llm_config,
    summarizer_llm_config=summarizer_llm_config,
)

config_list_4 = autogen.config_list_from_dotenv(
    dotenv_file_path="../.env",
    model_api_key_map={"gpt-4-turbo": "OPENAI_API_KEY"},
    filter_dict={
        "model": {
            "gpt-4-turbo",
        }
    }
)

image_llm_config = {
    "config_list": config_list_4,
    "temperature": 0.5,
    "max_tokens": 500,
    "cache_seed": 42
}

image_agent = MultimodalConversableAgent(
    name="image-explainer",
    llm_config=image_llm_config
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    code_execution_config=False,
    max_consecutive_auto_reply=0,
)

message = f"""
    You have the context of the image from web_surfer.
    Now, you need to answer: what is this picture of and describe everything in it based on the given context? <img {img_url}>
"""

chat_result = user_proxy.initiate_chats(
    [
        {
            "recipient": web_surfer,
            "message": "Summarize the content of this website 'https://www.bbc.com/news/world-us-canada-68937775'",
            "silent": False,
        },
        {
            "recipient": image_agent,
            "message": message,
            "silent": False,
        }
    ]
)

print(chat_result[-1].summary)
