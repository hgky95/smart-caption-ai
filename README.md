# Smart Caption AI

This project is an implementation of a research paper in which I work with Dr. Randy Lin (Algoma University) to leverage LLMs to generate accurate and relevant image captions. Besides, this research paper has been published on [IEEE](https://ieeexplore.ieee.org/document/10928130) at the ICCA conference.

You can install it from [Chrome Extension](https://chromewebstore.google.com/detail/locgcdpdjddfjjjdbjklenbcbmgakfcg?utm_source=item-share-cb)

## Introduction

Blind individuals and those with severe vision impairments face significant challenges in navigating web content, especially with understanding images. Since images frequently provide essential information or context, they become inaccessible without accompanying text alternatives.

Smart Caption AI is a Chrome extension that generates image captions using Large Language Models (LLMs). Its unique approach involves first summarizing the webpage content or article and then using it as context for generating image captions. This method allows the LLM to "understand" more details and relevant context for the images, resulting in more accurate and relevant image descriptions.
The tool employs a multi-agent system:

- Proxy Agent: Controls the conversation among other agents
- Summarizer Agent: Summarizes webpage content
- Image Agent: Converts images to text

  This innovative approach enables Smart Caption AI to provide more contextually appropriate and accurate image captions by leveraging the surrounding content of the webpage.
  Besides generating image captioning, the tool also simplify the webpage (removing ads, unnecessary information, etc) and providing Text-to-speech feature.

Below is the workflow of the tool:

![smartcaption-workflow drawio](https://github.com/user-attachments/assets/926be720-2fd7-4981-859b-53e2a21be346)

## Requirements

- Python 3.11
- OpenAI Key or your open source LLM host
- Framework and libraries: Flask-RESTful, Pyautogen, Readability.js, etc.

## Installation

1. Clone the repository
2. Go to smart-caption-ai folder
3. Install Python: https://www.python.org/downloads/
4. Setup Python virtual environment: `python -m venv .venv`
5. Activate virtual environment:

   On Windows: `.venv\Scripts\activate`

   On Unix or MacOS: `source .venv/bin/activate`

6. Install library dependencies: `pip install -r requirements.txt`

## Backend Setup

1. Open .env file in server folder, and declare below variables

```
OPENAI_API_KEY=
DB_HOST=localhost
DB_PORT=3306
DB_NAME=smart-caption-ai
DB_USER=
DB_PASSWORD=
NEWS_WHITELIST=globalnews.ca, thehub.ca, nationalpost.com, bbc.com, foxnews.com, ctvnews.ca, cbc.ca
RESTRICTED_IMAGE_DOMAINS=cbc.ca
IMAGE_STORAGE_PATH=/path-to-store-images
```

2. Run the app by: `python -m server.main`

To verify the backend running, you can query by:

`curl --location 'http://127.0.0.1:5000/ai/convert' \
--header 'Content-Type: application/json' \
--data '{
    "article_content": "$provided_content",
    "images_url": [
        {
            "url": "$image_url"
        }
    ]
}'`
article_content: the webpage content
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
