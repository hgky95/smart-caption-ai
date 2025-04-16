import asyncio
import autogen
from flask import request
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
from autogen.agentchat.assistant_agent import AssistantAgent
from flask_restful import Resource
from concurrent.futures import ThreadPoolExecutor
from .ImageStorageService import ImageStorageService
from .AIConfiguration import AIConfiguration
from .Chat import Chat
from .ImageDownloader import download_image
import time
import os
import logging

logger = logging.getLogger(__name__)

class ImageToTextService(Resource):

    RESTRICTED_IMAGE_DOMAINS = os.getenv('RESTRICTED_IMAGE_DOMAINS').split(',')
    NEWS_WHITELIST = os.getenv('NEWS_WHITELIST').split(',')

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
        chat_results = self.proxy_agent.initiate_chats(chat_queues)
        article_summary = chat_results[0].summary
        
        chat_img_results = asyncio.run(self.process_images(images_url, article_summary))
        
        chat_img_summary_list = [
            {'summary': chat_img_results[idx].replace('\n', ' ')} 
            for idx in sorted(chat_img_results.keys())
        ]

        self.store_result(images_url, chat_img_summary_list)

        end_time = time.time()
        consumed_time = end_time - start_time
        logger.info(f"Time consumed: {consumed_time} seconds")
        return {"data": chat_img_summary_list}
    
    async def generate_image_description(self, image_chat_queues):
        chat_results = await self.proxy_agent.a_initiate_chats(image_chat_queues)
        return {'summary': chat_results.summary.replace('\n', ' ')}

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
    
    async def process_images(self, images_url, article_summary):
        image_chat_results = {}
        
        async def process_single_image(index, img_url):
            try:
                logger.info(f"Processing image: {img_url['url']}")
                url = img_url['url']

                message = self.build_image_description_instruction(index, url, article_summary)
                await self.proxy_agent.a_send(message, self.image_agent, silent=False)
                
                response = await self.image_agent.a_generate_reply(sender=self.proxy_agent)
                
                return index, response
            except Exception as e:
                logger.error(f"Error processing image {img_url['url']}: {e}", exc_info=True)
                return index, f"Unable to generate description for image {index+1}."
        
        tasks = [process_single_image(index, img_url) for index, img_url in enumerate(images_url)]
        results = await asyncio.gather(*tasks)
        
        for index, response in results:
            image_chat_results[index] = response
        
        return image_chat_results

    def validate_news_url(self, news_source):
        for domain in self.NEWS_WHITELIST:
            if domain.strip() in news_source:
                return True
        return False
    
    def build_image_description_instruction(self, index, url, article_summary):
        image_tag_prefix = '<img'
        close_tag_suffix = '>'
        message = None

        is_restricted = any(domain in url.lower() for domain in self.RESTRICTED_IMAGE_DOMAINS)
        if is_restricted:
            logger.info(f"Using ImageDownloader for restricted image: {url}")
            success, pil_image = download_image(url)
            
            if not success or pil_image is None:
                logger.error(f"Failed to download restricted image: {url}")
                return index, f"Unable to generate description for image {index+1} (download failed)."
                    
            return AIConfiguration.get_image_description_instructions(url, article_summary)
        else:
            img_tag_formatted = image_tag_prefix + ' ' + url + close_tag_suffix
            message = AIConfiguration.get_image_description_instructions(img_tag_formatted, article_summary)
        
        return message
