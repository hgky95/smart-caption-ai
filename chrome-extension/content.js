const BACKEND_HOST = "http://127.0.0.1:5000";
const API = "/ai/convert";

async function createIframeWithModifiedContent() {
    console.log("Start create iframe");
    // Add a background overlay to cover the entire page
    const overlay = document.createElement('div');
    overlay.className = 'background-overlay';
    document.body.appendChild(overlay);

    // Create an iframe element
    const iframe = document.createElement('iframe');
    iframe.className = 'iframeContainer';
    iframe.id = 'iframeContainer';
    document.body.appendChild(iframe);

    // Fetch the current page content
    try {
        // Fetch the current page content
        const response = await fetch(window.location.href);
        const html = await response.text();

        // Parse the HTML content
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // Apply Readability modifications
        const article = new Readability(doc).parse();
        const iframeContent = `
            <html>
                <head>
                    <link rel="stylesheet" type="text/css" href="${chrome.runtime.getURL('css/iframeStyle.css')}">
                </head>
                <body>
                    <div class="body-content">
                        <h1>${article.title}</h1>
                        ${article.content}
                    </div>
                </body>
            </html>
        `;

        // Write the modified content to the iframe
        iframe.contentDocument.open();
        iframe.contentDocument.write(iframeContent);
        iframe.contentDocument.close();

        return article.content;
    } catch (error) {
        console.error('Error fetching and modifying content:', error);
        return null;
    }
}

function extractImageUrls(htmlContent) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlContent, 'text/html');
    const imgTags = doc.querySelectorAll('img');
    return Array.from(imgTags).map(img => img.src);
}

function updateImageAlts(imageSummaries) {
    const iframe = document.getElementById('iframeContainer');
    console.log("Updating image alt");

    const iframeDocument = iframe.contentDocument || iframe.contentWindow.document;
    const images = iframeDocument.getElementsByTagName('img');

    for (let i = 0; i < imageSummaries.length && i < images.length; i++) {
        images[i].alt = imageSummaries[i];
        console.log('Updated alt for image ' + (i + 1));
    }
}

function convertImagesToText(htmlContent) {
    const article_url = document.location.href;
    const imgTags = extractImageUrls(htmlContent);
    const images_url = imgTags.map(url => ({url}))
    console.log("Number of images: " + images_url.length);

    const headers = new Headers();
    headers.append("Content-Type", "application/json");
    const request_body = JSON.stringify({
        "article_url": article_url,
        "images_url": images_url
    });
    console.log(request_body);
    const requestOptions = {
        method: "POST",
        headers: headers,
        body: request_body,
    };
    console.log("Calling backend to convert image to text");
    fetch(BACKEND_HOST + API, requestOptions)
        .then((response) => response.json()) // Parse the response as JSON
        .then((result) => {
            // Extract the summaries
            const imageSummaries = result.data.map(element => element.summary);
            updateImageAlts(imageSummaries)
        })
        .catch((error) => console.error(error));
}

// Listen for messages from the background script
chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
    if (message.action === "createIframe") {
        const htmlContent = await createIframeWithModifiedContent();
        convertImagesToText(htmlContent);
    }
});
