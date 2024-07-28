# Smart Caption AI
Blind individuals and those with severe vision impairments face significant challenges in navigating web content, especially with understanding images. Since images frequently provide essential information or context, they become inaccessible without accompanying text alternatives.

Smart Caption AI is a Chrome extension that generates image captions using Large Language Models (LLMs). Its unique approach involves first summarizing the webpage content or article and then using it as context for generating image captions. This method allows the LLM to "understand" more details and relevant context for the images, resulting in more accurate and relevant image descriptions.
The tool employs a multi-agent system:
- Proxy Agent: Controls the conversation among other agents
- WebSurfer Agent: Surfs and summarizes webpage content
- Image Agent: Converts images to text
This innovative approach enables Smart Caption AI to provide more contextually appropriate and accurate image captions by leveraging the surrounding content of the webpage.
Besides generating image captioning, the tool also simplify the webpage (removing ads, unnecessary information, etc) and providing Text-to-speech feature.

## Requirements

- Python 3.11
- OpenAI Key or your open source LLM host
- Framework and libraries: Flask-RESTful, Pyautogen, Readability.js, etc.

## Installation
1) Clone the repository
2) Install Python: https://www.python.org/downloads/
3) Setup Python virtual environment: `python -m venv .venv`
4) Activate virtual environment:

    On Windows: `.venv\Scripts\activate`

    On Unix or MacOS: `source .venv/bin/activate`
5) Install library dependencies: `pip install -r requirement.txt`

## Backend Setup

### If you plan to use OpenAI
1. Go to smart-caption-ai/server folder
2. Open .env file, and declare your `OPENAI_API_KEY`
3. Run the app by: `python main.py`
4. Open Chrome browser with Developer mode and load the 

### If you plan to use Open source LLM: llama, phi3, llava, etc
1. Go to smart-caption-ai/server folder
2. Open .env file, and declare your server url which host the LLM: `BASE_URL`
3. Run the app by: `python main.py`

To verify the backend running, you can query by:

`curl --location 'http://127.0.0.1:5000/ai/convert' \
--header 'Content-Type: application/json' \
--data '{
    "article_url": "https://www.aljazeera.com/gallery/2021/3/18/families-forced-into-a-deadly-spiral-in-central-african-republic",
    "images_url": [
        {
            "url": "https://www.aljazeera.com/wp-content/uploads/2021/03/3-3.jpg?fit=1170%2C746&quality=80 "
        }
    ]
}'`
article_url: the webpage content url
images_url: list of images url in the article

## Frontend Setup (chrome extension)
1. Open Chrome browser / Settings / Extensions / Manage Extensions
2. Click on 'Load unpacked' on the top-left corner
3. Select the 'chrome-extension' folder that you cloned from previous step. Then the extension will be listed as below:
![image](https://github.com/user-attachments/assets/da3a8044-1d96-4111-8356-df6149ae4986)
4. Open Extension and 'pin' it for easy to use.
5. Now, you can open an article (eg. cbc.ca), then click on the icon of this tool.

