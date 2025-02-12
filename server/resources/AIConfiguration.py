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
        filter_dict={
            "model": {
                "gpt-4o-mini",
            }
        }
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

    def get_image_description_instructions(img_tag_formatted):
        return f"""
                           You are an Image Description Agent specializing in creating detailed, precise image descriptions for visually impaired users. 
                           You have the context of the image provided by the web_surfer. Your primary focus is providing rich visual details while using context to enhance accuracy.
                           INPUT:
                           Image content: {img_tag_formatted}

                           DESCRIPTION REQUIREMENTS:

                           Visual Elements (Must Cover):

                           - Subject composition and arrangement
                           - Colors, lighting, and visual tone
                           - Spatial relationships between elements
                           - Background details when relevant
                           - Text or symbols if present
                           - Facial expressions and body language for people
                           - Notable design elements or patterns

                           Detail Level:

                           - Start with overall scene/composition
                           - Progress to specific details
                           - Include relevant measurements or scale when apparent
                           - Describe textures and materials where visible
                           - Note any distinctive features or unusual elements

                           Context Integration:

                           - Use article context to identify specific people, locations, or events
                           - Clarify technical elements mentioned in the article
                           - Verify specialized terminology accuracy

                           FORMAT (maximum 4 sentences):

                           - First sentence: Overall scene description
                           - Second sentence: Key visual details and composition
                           - Third sentence: Specific elements and their relationships
                           - Final sentence: Relevant contextual connection

                           QUALITY GUIDELINES:

                           - Use precise, descriptive language
                           - Maintain objective, factual tone
                           - Order details from most to least significant
                           - Include spatial relationships clearly
                           - Use specific color terms rather than general ones
                           - Describe patterns and textures with concrete comparisons
                           - When describing people, include relevant visual details while maintaining respect

                           ACCURACY RULES:

                           - Only describe what is clearly visible in the image
                           - Use qualifying language for uncertain elements
                           - Cross-reference visual elements with article context
                           - Do not make assumptions about non-visible elements
                           - If technical details are mentioned in context, verify they match what's visible"""
