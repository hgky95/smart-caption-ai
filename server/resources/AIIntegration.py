import autogen
from flask import request
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
from autogen.agentchat.assistant_agent import AssistantAgent
from flask_restful import Resource

from .AIConfiguration import AIConfiguration
from .Chat import Chat
import time


class AIIntegration(Resource):

    def post(self):
        start_time = time.time()

        data = request.get_json()
        article_content = data['article_content']
        images_url = data['images_url']

        # Start logging
        logging_session_id = autogen.runtime_logging.start(config={"dbname": "logs.db"})
        print("Logging session ID: " + str(logging_session_id))

        # Create agents
        summarizer_agent = self.create_content_summarizer_agent()
        image_agent = self.create_image_agent()
        user_proxy = self.create_user_proxy_agent()

        # Create chat queues
        chat_queues = []
        summary_chat = Chat(summarizer_agent, f"Summarize the main content of the HTML: {article_content}", False).toDict()
        chat_queues.append(summary_chat)
        self.add_image_chat_to_queues(chat_queues, image_agent, images_url)
        chat_results = user_proxy.initiate_chats(chat_queues)

        autogen.runtime_logging.stop()

        # Only get the images summary
        chat_img_results = chat_results[1:]
        # Format response
        chat_img_summary_list = [{'summary': chat_img_result.summary.replace('\n', ' ')} for chat_img_result in chat_img_results]

        end_time = time.time()
        consumed_time = end_time - start_time
        print(f"Time consumed: {consumed_time} seconds")
        return {"data": chat_img_summary_list}

    def create_user_proxy_agent(self):
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            code_execution_config=False,
            max_consecutive_auto_reply=0,
        )
        return user_proxy

    def create_image_agent(self):
        image_agent = MultimodalConversableAgent(
            name="image-explainer",
            llm_config=AIConfiguration.image_llm_config
        )
        return image_agent

    def create_content_summarizer_agent(self):
        summarizer_agent = AssistantAgent(
            name="content-summarizer",
            llm_config=AIConfiguration.content_summarizer_config,
            system_message=AIConfiguration.content_summarizer_system_message
        )
        return summarizer_agent

    def add_image_chat_to_queues(self, chat_queues, image_agent, images_url):
        image_tag_prefix = '<img'
        close_tag_suffix = '>'
        for img_url in images_url:
            img_tag_formatted = image_tag_prefix + ' ' + img_url['url'] + close_tag_suffix
            message = f"""
                           You have the context of the image provided by the web_surfer. 
                           Now, based on the given context of the image, you need to describe the image in details {img_tag_formatted}.
                           Besides with describing the image, you also need to mentioned the context of this image. 
                           Keep the description to a maximum of four sentences."""
            chat_queues.append(Chat(image_agent, message, False).toDict())
