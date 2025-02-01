const BACKEND_HOST = "http://127.0.0.1:5000";
const API = "/ai/convert";

function cleanArticleContent(article) {
  const tempDiv = document.createElement("div");
  tempDiv.innerHTML = article.content;

  const selectorsToRemove = [
    "script",
    "style",
    "iframe",
    "nav",
    "header",
    "footer",
    "noscript",
    '[class*="ad"]',
    '[class*="social"]',
    '[id*="sidebar"]',
    "meta",
    "link",
  ];

  selectorsToRemove.forEach((selector) => {
    tempDiv.querySelectorAll(selector).forEach((el) => el.remove());
  });

  // Clean attributes from remaining elements except for essential ones
  const elementsToClean = tempDiv.getElementsByTagName("*");
  for (let el of elementsToClean) {
    const attributesToKeep = ["src", "href", "alt"];
    const attributes = el.attributes;
    for (let i = attributes.length - 1; i >= 0; i--) {
      const attrName = attributes[i].name;
      if (!attributesToKeep.includes(attrName)) {
        el.removeAttribute(attrName);
      }
    }
  }

  return {
    title: article.title,
    content: tempDiv.innerHTML,
    textContent: tempDiv.textContent.trim(),
  };
}

async function createIframeWithModifiedContent() {
  console.log("Start create iframe");
  // Add a background overlay to cover the entire page
  const overlay = document.createElement("div");
  overlay.className = "background-overlay";
  document.body.appendChild(overlay);

  // Create an iframe element
  const iframe = document.createElement("iframe");
  iframe.className = "iframeContainer";
  iframe.id = "iframeContainer";
  document.body.appendChild(iframe);

  // Fetch the current page content
  try {
    const response = await fetch(window.location.href);
    const html = await response.text();

    // Parse the HTML content
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, "text/html");

    // Apply Readability modifications
    const article = new Readability(doc).parse();
    const cleanedArticle = cleanArticleContent(article);

    const iframeContent = `
            <html>
                <head>
                    <link rel="stylesheet" type="text/css" href="${chrome.runtime.getURL(
                      "css/iframeStyle.css"
                    )}">
                    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.11.3/font/bootstrap-icons.min.css" />
                </head>
                <body>
                    <div class="body-content">
                        <h1>${cleanedArticle.title}</h1>
                        ${cleanedArticle.content}
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

    // Wait for iframe to load
    await new Promise((resolve) => {
      iframe.onload = () => {
        console.log("Iframe fully loaded");
        resolve();
      };
    });

    const speakButton = iframe.contentDocument.getElementById("tts");
    // disable speak button by default until the image summarization returning
    speakButton.disabled = true;
    speakButton.addEventListener("click", () => {
      textToSpeech();
      const ttsControls = iframe.contentDocument.getElementById("tts-controls");
      ttsControls.style.display = "block";
    });

    return cleanedArticle.content;
  } catch (error) {
    console.error("Error fetching and modifying content:", error);
    return null;
  }
}

function isRelevantImage(img) {
  // Skip common ad/icon/logo patterns and placeholders
  const skipPatterns = [
    /logo/i,
    /icon/i,
    /banner/i,
    /ad-/i,
    /advertisement/i,
    /button/i,
    /badge/i,
    /sprite/i,
    /tracking/i,
    /placeholder/i, // More general pattern to catch any placeholder
    /grey-placeholder/i, // Specific to BBC
  ];

  // Check if URL is empty or invalid
  if (!img.src || img.src === "" || img.src === "about:blank") {
    return false;
  }

  const url = new URL(img.src);
  const pathname = url.pathname;

  // Check src, alt, class, id, and pathname
  const attributes = [img.src, img.alt, img.className, img.id, pathname]
    .join(" ")
    .toLowerCase();

  if (skipPatterns.some((pattern) => pattern.test(attributes))) {
    return false;
  }

  return true;
}

function extractImageUrls(htmlContent) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(htmlContent, "text/html");
  const imgTags = doc.querySelectorAll("img");

  // Filter and map relevant images
  return Array.from(imgTags)
    .filter((img) => isRelevantImage(img))
    .map((img) => img.src);
}

function updateImageAlts(imageSummaries) {
  const iframe = document.getElementById("iframeContainer");
  console.log("Updating image alt");

  const iframeDocument =
    iframe.contentDocument || iframe.contentWindow.document;
  const images = iframeDocument.getElementsByTagName("img");

  for (let i = 0; i < imageSummaries.length && i < images.length; i++) {
    images[i].alt = imageSummaries[i];

    const summaryParagraph = iframeDocument.createElement("p");
    summaryParagraph.innerHTML = `The following image's summarization is generated by AI. Starting image description: <br> ${imageSummaries[i]} <br> Ending image description.`;

    // Insert the <p> element next to the image
    images[i].parentNode.insertBefore(summaryParagraph, images[i].nextSibling);
    console.log("Updated summarization for image " + (i + 1));
  }
  const speakButton = iframe.contentDocument.getElementById("tts");
  speakButton.disabled = false;
}

function convertImagesToText(htmlContent) {
  const imgUrls = extractImageUrls(htmlContent);
  const images_url = imgUrls.map((url) => ({ url }));

  console.log(`Found ${imgUrls.length} relevant images out of total images`);

  const headers = new Headers();
  headers.append("Content-Type", "application/json");
  const request_body = JSON.stringify({
    article_content: htmlContent,
    images_url: images_url,
  });
  const requestOptions = {
    method: "POST",
    headers: headers,
    body: request_body,
  };

  console.log(request_body.length);
  console.log("Calling backend to convert image to text");

  // fetch(BACKEND_HOST + API, requestOptions)
  //   .then((response) => response.json())
  //   .then((result) => {
  //     const imageSummaries = result.data.map((element) => element.summary);
  //     updateImageAlts(imageSummaries);
  //   })
  //   .catch((error) => console.error("Error processing images:", error));
  const imageSummaries = ["test", "test", "test", "test"];
  updateImageAlts(imageSummaries);
}

let currentUtterance;
let synth = window.speechSynthesis;

let isPaused = false;

function textToSpeech() {
  const iframe = document.getElementById("iframeContainer");
  const iframeDocument =
    iframe.contentDocument || iframe.contentWindow.document;
  const textContent = iframeDocument.querySelector(".body-content").textContent;

  if (synth.speaking) {
    console.error("SpeechSynthesisUtterance is already speaking.");
    return;
  }

  currentUtterance = new SpeechSynthesisUtterance(textContent);
  const playPauseButton = iframeDocument.getElementById("play-pause");
  const speedButtons = iframeDocument.querySelectorAll(".speed-button");

  playPauseButton.addEventListener("click", () => {
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

  speedButtons.forEach((button) => {
    button.addEventListener("click", () => {
      speedButtons.forEach((btn) => btn.classList.remove("selected"));
      button.classList.add("selected");
      if (synth.speaking) {
        synth.cancel();
        currentUtterance.rate = parseFloat(button.value);
        synth.speak(currentUtterance);
      }
    });
  });

  // Set initial rate
  currentUtterance.rate = parseFloat(
    iframeDocument.querySelector(".speed-button.selected").value
  );
  synth.speak(currentUtterance);
}

function handleFeedbackSubmission(form, modal, isRequired) {
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    e.stopPropagation();

    const feedback = {
      satisfaction: form.querySelector("#satisfaction").value,
      improvements: form.querySelector("#improvements").value,
      issues: form.querySelector("#issues").value,
      timestamp: new Date().toISOString(),
    };

    // Send feedback to background script
    chrome.runtime.sendMessage(
      { action: "submitFeedback", feedback },
      (response) => {
        if (chrome.runtime.lastError) {
          console.error("Feedback error:", chrome.runtime.lastError);
          return;
        }
        modal.remove();
      }
    );
  });

  // For required feedback, prevent closing until submitted
  if (isRequired) {
    const closeButtons = modal.querySelectorAll(".close-modal");
    closeButtons.forEach((btn) => (btn.style.display = "none"));
  }
}

function createFeedbackModal(isRequired) {
  const iframe = document.getElementById("iframeContainer");
  if (!iframe) {
    console.error("Iframe not found");
    return;
  }
  const iframeDocument =
    iframe.contentDocument || iframe.contentWindow.document;

  if (!iframeDocument || !iframeDocument.body) {
    console.error("Iframe document not ready");
    return;
  }
  console.log("Creating modal in iframe");

  const modal = iframeDocument.createElement("div");
  modal.className = "feedback-container";
  modal.innerHTML = `
    <div class="feedback-overlay">
      <div class="feedback-modal">
        <div class="modal-header">
          <h2>We Value Your Feedback! ${isRequired ? "(Required)" : ""}</h2>
          ${!isRequired ? '<span class="close-modal">&times;</span>' : ""}
        </div>
        <form class="feedback-form">
          <div class="form-group">
            <label>How satisfied are you with our tool?</label>
            <textarea id="satisfaction" required></textarea>
          </div>
          <div class="form-group">
            <label>What improvements would you suggest?</label>
            <textarea id="improvements" required></textarea>
          </div>
          <div class="form-group">
            <label>Any technical issues encountered?</label>
            <textarea id="issues" required></textarea>
          </div>
          <button type="submit">Submit Feedback</button>
        </form>
      </div>
    </div>
  `;

  // Handle form submission
  const form = modal.querySelector("form");
  handleFeedbackSubmission(form, modal, isRequired);

  // Add close handler for optional feedback
  if (!isRequired) {
    modal.querySelector(".close-modal").addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      modal.remove();
    });
  }

  // Prevent clicks on overlay from bubbling
  modal.querySelector(".feedback-overlay").addEventListener("click", (e) => {
    if (e.target === modal.querySelector(".feedback-overlay")) {
      e.preventDefault();
      e.stopPropagation();
      if (!isRequired) {
        modal.remove();
      }
    }
  });

  // Add modal to iframe
  const container = iframeDocument.documentElement; // Append to root element

  if (container) {
    container.appendChild(modal);
    console.log("Modal added to container");
  } else {
    console.error("Could not find container");
  }
}

// Listen for messages from the background script
chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
  if (message.action === "createIframe") {
    const htmlContent = await createIframeWithModifiedContent();
    convertImagesToText(htmlContent);
    // Store the feedback request if it came before iframe was ready
    if (window.pendingFeedbackRequest) {
      createFeedbackModal(window.pendingFeedbackRequest.isRequired);
      window.pendingFeedbackRequest = null;
    }
  } else if (message.action === "showFeedback") {
    console.log("Received showFeedback message");
    const iframe = document.getElementById("iframeContainer");
    if (iframe && iframe.contentDocument.readyState === "complete") {
      createFeedbackModal(message.isRequired);
    } else {
      // Store the request for later
      window.pendingFeedbackRequest = message;
      console.log("Iframe not ready, storing feedback request");
    }
  }
});
