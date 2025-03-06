# Smart Caption AI
This project is an implementation of a research paper in which I work with Dr. Randy Lin (Algoma University) to leverage LLMs to generate accurate and relevant image captions. Besides, this research paper has been accepted by the [IEEE/ICCA'24 (Sixth Edition, BUE)](https://icca-conf.info/international-conference-1) conference.

You can install it from [Chrome Extension](https://chromewebstore.google.com/detail/locgcdpdjddfjjjdbjklenbcbmgakfcg?utm_source=item-share-cb)

## Introduction
Blind individuals and those with severe vision impairments face significant challenges in navigating web content, especially with understanding images. Since images frequently provide essential information or context, they become inaccessible without accompanying text alternatives.

Smart Caption AI is a Chrome extension that generates image captions using Large Language Models (LLMs). Its unique approach involves first summarizing the webpage content or article and then using it as context for generating image captions. This method allows the LLM to "understand" more details and relevant context for the images, resulting in more accurate and relevant image descriptions.
The tool employs a multi-agent system:
- Proxy Agent: Controls the conversation among other agents
- WebSurfer Agent: Surfs and summarizes webpage content
- Image Agent: Converts images to text
This innovative approach enables Smart Caption AI to provide more contextually appropriate and accurate image captions by leveraging the surrounding content of the webpage.
Besides generating image captioning, the tool also simplify the webpage (removing ads, unnecessary information, etc) and providing Text-to-speech feature.

Below is the workflow of the tool:

![read-simplify-flow](https://github.com/user-attachments/assets/273595df-2b8a-4d97-9248-120d39830ec1)

## Requirements

- Python 3.11
- OpenAI Key or your open source LLM host
- Framework and libraries: Flask-RESTful, Pyautogen, Readability.js, etc.

## Installation
1) Clone the repository
2) Go to smart-caption-ai folder
3) Install Python: https://www.python.org/downloads/
4) Setup Python virtual environment: `python -m venv .venv`
5) Activate virtual environment:

    On Windows: `.venv\Scripts\activate`

    On Unix or MacOS: `source .venv/bin/activate`
6) Install library dependencies: `pip install -r requirements.txt`

## Backend Setup

### If you plan to use OpenAI
1. Open .env file in server folder, and declare your `OPENAI_API_KEY`
2. Run the app by: `python -m server.main`

### If you plan to use Open source LLM: llama, phi3, llava, etc
1. Open .env file in server folder, and declare your server url which host the LLM: `BASE_URL`
2. Run the app by: `python -m server.main`

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
2. Enable 'Developer Mode' on the top-right corner
3. Click on 'Load unpacked' on the top-left corner
4. Select the 'chrome-extension' folder that you cloned from previous step. Then the extension will be listed as below:
   
![image](https://github.com/user-attachments/assets/da3a8044-1d96-4111-8356-df6149ae4986)

6. Open Extension and 'pin' it for easy to use.
7. Now, you can open an article (eg. [GitHub Pages](https://pages.github.com/)), then click on the icon of this tool.
Result as below:

![record-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/4ca7937d-abad-4fe8-a566-22e8298284e7)

## Future Works
1. Fix issues with displaying images on some websites 
    - This tool is not compatible with all websites. Some websites are built with different iframe structures that lead to the tool being unable to display all of the images.

2. Optimize processing time by sending the article content directly instead of the URL to reduce 'surfing' time of the agent.
