import autogen
from flask import request
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
from autogen.agentchat.assistant_agent import AssistantAgent
from flask_restful import Resource
from concurrent.futures import ThreadPoolExecutor
from .ImageStorageService import ImageStorageService
from .AIConfiguration import AIConfiguration
from .Chat import Chat
import time
import os
import logging

logger = logging.getLogger(__name__)

class ImageToTextService(Resource):

    def __init__(self):
        self.proxy_agent = self.create_user_proxy_agent()
        self.image_agent = self.create_image_agent()
        self.summarizer_agent = self.create_content_summarizer_agent()
        self.image_storage_service = ImageStorageService()
        self.executor = ThreadPoolExecutor(max_workers=3)


    def post(self):
        start_time = time.time()

        data = request.get_json()
        article_content = data['article_content']
        images_url = data['images_url']
        news_source = data['news_source']

        logger.info(f"Request received for news source: {news_source} with {len(images_url)} images")

        if not self.validate_news_url(news_source):
            news_whitelist = os.getenv('NEWS_WHITELIST')
            logger.error(f"The {news_source} you entered is not supported at this time. We currently only support news from {news_whitelist}.")
            return {"message": f"The news source you entered is not supported at this time. We currently only support news from {news_whitelist}."}, 403

        chat_queues = []
        summary_chat = Chat(self.summarizer_agent, f"Summarize the main content of the HTML: {article_content}", False).toDict()
        chat_queues.append(summary_chat)
        self.add_image_chat_to_queues(chat_queues, self.image_agent, images_url)
        chat_results = self.proxy_agent.initiate_chats(chat_queues)

        # Only get the images summary
        chat_img_results = chat_results[1:]
        chat_img_summary_list = [{'summary': chat_img_result.summary.replace('\n', ' ')} for chat_img_result in chat_img_results]

        self.store_result(images_url, chat_img_summary_list)

        end_time = time.time()
        consumed_time = end_time - start_time
        logger.info(f"Time consumed: {consumed_time} seconds")
        return {"data": chat_img_summary_list}

    def store_result(self, images_url, chat_img_summary_list):
        self.executor.submit(self.image_storage_service.store_images_description, images_url, chat_img_summary_list)

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
            logger.info(f"Adding image to chat: {img_url['url']}")
            img_tag_formatted = image_tag_prefix + ' ' + img_url['url'] + close_tag_suffix
            message = AIConfiguration.get_image_description_instructions(img_tag_formatted)
            chat_queues.append(Chat(image_agent, message, False).toDict())

    def validate_news_url(self, news_source):
        news_whitelist = os.getenv('NEWS_WHITELIST')
        news_whitelist_list = news_whitelist.split(',')
        for domain in news_whitelist_list:
            if domain.strip() in news_source:
                return True
        return False
