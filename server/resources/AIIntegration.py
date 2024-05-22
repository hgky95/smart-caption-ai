import autogen
from flask import request
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
from autogen.agentchat.contrib.web_surfer import WebSurferAgent

from flask_restful import Resource

from server.resources.AIConfiguration import AIConfiguration
from server.resources.Chat import Chat


class AIIntegration(Resource):

    def post(self):
        data = request.get_json()
        article_url = data['article_url']
        images_url = data['images_url']

        # Start logging
        logging_session_id = autogen.runtime_logging.start(config={"dbname": "logs.db"})
        print("Logging session ID: " + str(logging_session_id))

        # Create agents
        web_surfer = self.create_web_surfer_agent()
        image_agent = self.create_image_agent()
        user_proxy = self.create_user_proxy_agent()

        # Create chat queues
        chat_queues = []
        summary_chat = Chat(web_surfer, f"Summarize the content of this website {article_url}", False).toDict()
        chat_queues.append(summary_chat)
        self.add_image_chat_to_queues(chat_queues, image_agent, images_url)
        chat_results = user_proxy.initiate_chats(chat_queues)

        autogen.runtime_logging.stop()

        # Only get the images summary
        chat_img_results = chat_results[1:]
        # Format response
        chat_img_summary_list = [{'summary': chat_img_result.summary.replace('\n', ' ')} for chat_img_result in chat_img_results]
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

    def create_web_surfer_agent(self):
        web_surfer = WebSurferAgent(
            "web_surfer",
            llm_config=AIConfiguration.web_surfer_llm_config,
            summarizer_llm_config=AIConfiguration.summarizer_llm_config,
        )
        return web_surfer

    def add_image_chat_to_queues(self, chat_queues, image_agent, images_url):
        image_tag_prefix = '<img'
        close_tag_suffix = '>'
        for img_url in images_url:
            img_tag_formatted = image_tag_prefix + ' ' + img_url['url'] + close_tag_suffix
            message = f"""
                           You have the context of the image from web_surfer.
                           Now, you need to answer: what is this picture of and describe everything in it based on the given context? {img_tag_formatted}>
                       """
            chat_queues.append(Chat(image_agent, message, False).toDict())
