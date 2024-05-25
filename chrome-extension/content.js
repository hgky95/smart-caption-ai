// Function to create iframe with modified content
function createIframeWithModifiedContent() {
    // Create a full-page overlay
    const overlay = document.createElement('div');
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)'; // Semi-transparent black overlay
    overlay.style.zIndex = '10000';
    document.body.appendChild(overlay);

    // Create an iframe element
    const iframe = document.createElement('iframe');
    iframe.style.position = 'fixed';
    iframe.style.top = '50%';
    iframe.style.left = '50%';
    iframe.style.transform = 'translate(-50%, -50%)'; // Center the iframe
    iframe.style.zIndex = '10001'; // Place iframe above the overlay
    iframe.style.border = 'none';
    document.body.appendChild(iframe);

    // Fetch the current page content
    fetch(window.location.href)
        .then(response => response.text())
        .then(html => {
            // Parse the HTML content
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            // Apply Readability modifications
            const article = new Readability(doc).parse();
            console.log("After using Readability lib: ", article);

            // Write the modified content to the iframe
            iframe.contentDocument.open();
            iframe.contentDocument.write(article.content);
            iframe.contentDocument.close();
        })
        .catch(error => {
            console.error('Error fetching and modifying content:', error);
        });
}

// Listen for messages from the background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "createIframe") {
        createIframeWithModifiedContent();
    }
});
