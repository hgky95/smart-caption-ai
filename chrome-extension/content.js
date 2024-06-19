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
                    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.11.3/font/bootstrap-icons.min.css" />
                </head>
                <body>
                    <div class="body-content">
                        <h1>${article.title}</h1>
                        ${article.content}
                    </div>
                    
                    <button id="tts" class="bi bi-volume-up-fill" style="position: absolute; top: 10px; right: 10px;"></button>
                    <div id="tts-controls" class="tts-controls" style="position: absolute; display: none;">
                        <i id="play-pause" class="bi-pause-circle-fill"></i>
                        <div class="speed-controls">
                            <button id="speed-075" class="speed-button" value="0.75">0.75x</button>
                            <button id="speed-1" class="speed-button selected" value="1">1x</button>
                            <button id="speed-125" class="speed-button" value="1.25">1.25x</button>
                            <button id="speed-15" class="speed-button" value="1.5">1.5x</button>
                            <button id="speed-2" class="speed-button" value="2">2x</button>
                        </div>
                    </div>
                </body>
            </html>
        `;

        // Write the modified content to the iframe
        iframe.contentDocument.open();
        iframe.contentDocument.write(iframeContent);
        iframe.contentDocument.close();

        // Wait for the iframe content to be fully loaded
        iframe.onload = () => {
            const speakButton = iframe.contentDocument.getElementById('tts');
            // disable speak button by default until the image summarization returning
            speakButton.disabled = true;
            speakButton.addEventListener('click', () => {
                textToSpeech();
                const ttsControls = iframe.contentDocument.getElementById('tts-controls');
                ttsControls.style.display = 'block';
            });
        };

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

        // Create a new <p> element for the summarization
        const summaryParagraph = iframeDocument.createElement('p');
        summaryParagraph.innerHTML = `Starting image description: <br> ${imageSummaries[i]} <br> Ending image description.`;

        // Insert the <p> element next to the image
        images[i].parentNode.insertBefore(summaryParagraph, images[i].nextSibling);
        console.log('Updated summarization for image ' + (i + 1));
    }
    const speakButton = iframe.contentDocument.getElementById('tts');
    speakButton.disabled = false;
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

let currentUtterance;
let synth = window.speechSynthesis;

let isPaused = false;

function textToSpeech() {
    const iframe = document.getElementById('iframeContainer');
    const iframeDocument = iframe.contentDocument || iframe.contentWindow.document;
    const textContent = iframeDocument.querySelector('.body-content').textContent;

    if (synth.speaking) {
        console.error('SpeechSynthesisUtterance is already speaking.');
        return;
    }

    currentUtterance = new SpeechSynthesisUtterance(textContent);
    const playPauseButton = iframeDocument.getElementById('play-pause');
    const speedButtons = iframeDocument.querySelectorAll('.speed-button');

    playPauseButton.addEventListener('click', () => {
        if (synth.speaking) {
            if (isPaused) {
                synth.resume();
                playPauseButton.className = "bi bi-pause-circle-fill";
                isPaused = false;
            } else {
                synth.pause();
                playPauseButton.className = "bi bi-play-circle-fill";
                isPaused = true;
            }
        } else {
            synth.speak(currentUtterance);
            playPauseButton.className = "bi bi-play-circle-fill";
        }
    });

    speedButtons.forEach(button => {
        button.addEventListener('click', () => {
            speedButtons.forEach(btn => btn.classList.remove('selected'));
            button.classList.add('selected');
            if (synth.speaking) {
                synth.cancel();
                currentUtterance.rate = parseFloat(button.value);
                synth.speak(currentUtterance);
            }
        });
    });

    // Set initial rate
    currentUtterance.rate = parseFloat(iframeDocument.querySelector('.speed-button.selected').value);
    synth.speak(currentUtterance);
}

// Listen for messages from the background script
chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
    if (message.action === "createIframe") {
        const htmlContent = await createIframeWithModifiedContent();
        convertImagesToText(htmlContent);
    }
});