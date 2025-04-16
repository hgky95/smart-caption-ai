import requests
from io import BytesIO
from PIL import Image

def download_image(url):
    
    # simulate full browser-like headers for image requests
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/jpeg, image/png',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.cbc.ca/',
        'Origin': 'https://www.cbc.ca',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'Sec-Fetch-Dest': 'image',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-site',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
    }
    
    try:
        print(f"Downloading image from: {url}")
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '')
        print(f"Content-Type: {content_type}")
        img_data = BytesIO(response.content)
            
        print(f"Downloaded content size: {len(img_data.getvalue())} bytes")
        
        try:
            pil_image = Image.open(img_data).convert("RGB")
            return True, pil_image
        except Exception as e:
            print(f"Error opening image: {e}")
            return False, None
            
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False, None