import json

import autogen
from flask import request, jsonify
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
from autogen.agentchat.contrib.web_surfer import WebSurferAgent

from flask_restful import Resource



class AIIntegration(Resource):

    def post(self):
        data = request.get_json()
        article_url = data['article_url']
        images_url = data['images_url']

        # Start logging
        logging_session_id = autogen.runtime_logging.start(config={"dbname": "logs.db"})
        print("Logging session ID: " + str(logging_session_id))

        config_list_3 = autogen.config_list_from_dotenv(
            dotenv_file_path="../.env",
            model_api_key_map={"gpt-3.5-turbo": "OPENAI_API_KEY"},
            #model_api_key_map={"gpt-4o": "OPENAI_API_KEY"},
            filter_dict={
                "model": {
                    "gpt-3.5-turbo",
                    #"gpt-4o",
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

        web_surfer = WebSurferAgent(
            "web_surfer",
            llm_config=web_surfer_llm_config,
            summarizer_llm_config=summarizer_llm_config,
        )

        config_list_4 = autogen.config_list_from_dotenv(
            dotenv_file_path="../.env",
            #model_api_key_map={"gpt-4-turbo": "OPENAI_API_KEY"},
            model_api_key_map={"gpt-4o": "OPENAI_API_KEY"},
            filter_dict={
                "model": {
                    #"gpt-4-turbo",
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

        img_tags = []
        IMAGE_TAG_PREFIX = '<img'
        CLOSE_TAG_SUFFIX = '>'

        for img_url in images_url:
            img_tags.append(IMAGE_TAG_PREFIX + ' ' + img_url['url'] + CLOSE_TAG_SUFFIX)

        img_tags_string = ', '.join(img_tags)

        message = f"""
           You have the context of the image from web_surfer.
           Now, you need to answer: what is this picture of and describe everything in it based on the given context? {img_tags_string}>
       """

        chat_results = user_proxy.initiate_chats(
            [
                {
                    "recipient": web_surfer,
                    "message": f"Summarize the content of this website {article_url}",
                    "silent": False,
                },
                {
                    "recipient": image_agent,
                    "message": message,
                    "silent": False,
                }
            ]
        )

        autogen.runtime_logging.stop()

        chat_summary_list = [{'summary': chat_result.summary.replace('\n', ' ')} for chat_result in chat_results]

        return {"data": chat_summary_list}