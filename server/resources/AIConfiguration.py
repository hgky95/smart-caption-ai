import autogen


class AIConfiguration:
    content_summarizer_system_message = """
        You are an expert at analyzing and summarizing HTML content.
                Your tasks:
                1. Extract the main textual content from HTML, ignoring navigation, headers, footers, and other boilerplate
                2. Provide a clear, concise summary of the main content
                3. Identify and preserve key information like titles, dates, and main topics
                4. Ignore HTML tags and formatting in your summary
                Please provide summaries that are coherent and well-structured."""

    config_list = autogen.config_list_from_dotenv(
        dotenv_file_path="server/.env",
        model_api_key_map={"gpt-4o-mini": "OPENAI_API_KEY"},
    )

    image_llm_config = {
        "config_list": config_list,
        "temperature": 0.5,
        "max_tokens": 500,
        "cache_seed": 42
    }

    content_summarizer_config = {
        "config_list": config_list,
        "temperature": 0,
        "max_tokens": 1000,
        "cache_seed": 42
    }

    def get_image_description_instructions(img_tag_formatted, article_summary):
        return f"""You are an Image Describer Agent creating detailed descriptions helping visually impaired users understand the image.
        
            IMAGE: {img_tag_formatted}
            ARTICLE CONTEXT: {article_summary}
            
            DESCRIBE THE IMAGE IN MAXIMUM 4 SENTENCES:
            - Overall scene description
            - Key visual details and composition
            - Specific elements and their relationships
            - Describe people, locations, or events based on the article context
            
            GUIDELINES:
            - Be precise, objective, and factual
            - Cover subject, colors, lighting, spatial relationships, and text if present
            - Describe people respectfully with relevant visual details
            - Only describe what is clearly visible
        """
