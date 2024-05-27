// Function to create iframe with modified content
function createIframeWithModifiedContent() {
    // Add a gray overlay to cover the entire page
    const overlay = document.createElement('div');
    overlay.className = 'background-overlay';
    document.body.appendChild(overlay);

    // Create an iframe element
    const iframe = document.createElement('iframe');
    iframe.className = 'iframeContainer'; // Apply iframe container style from CSS
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

            // Create a styled container for the iframe content
            const iframeContent = `
                <html>
                    <head>
                        <link rel="stylesheet" type="text/css" href="${chrome.runtime.getURL('css/iframeStyle.css')}">
                    </head>
                    <body>
                        <div class="body-content">
                            ${article.content}
                        </div>
                    </body>
                </html>
            `;

            // Write the modified content to the iframe
            iframe.contentDocument.open();
            iframe.contentDocument.write(iframeContent);
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
