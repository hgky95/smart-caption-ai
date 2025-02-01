// Constants
const OPTIONAL_FEEDBACK_COUNT = 2;
const REQUIRED_FEEDBACK_COUNT = 5;
const FEEDBACK_API = "http://127.0.0.1:5000/feedback";

// Initialize usage counter
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({ usageCount: 0 });
});

// Handle extension icon click
chrome.action.onClicked.addListener(async (tab) => {
  const { usageCount } = await chrome.storage.local.get("usageCount");
  const newCount = (usageCount || 0) + 1;
  await chrome.storage.local.set({ usageCount: newCount });

  chrome.tabs.sendMessage(tab.id, { action: "createIframe" });

  // Show feedback modal when needed
  if ([OPTIONAL_FEEDBACK_COUNT, REQUIRED_FEEDBACK_COUNT].includes(newCount)) {
    chrome.tabs.sendMessage(tab.id, {
      action: "showFeedback",
      isRequired: newCount === REQUIRED_FEEDBACK_COUNT,
    });
  }
});

// Handle feedback submission
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "submitFeedback") {
    fetch(FEEDBACK_API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(message.feedback),
    })
      .then(() => chrome.storage.local.set({ usageCount: 0 }))
      .catch((error) => console.error("Feedback submission failed:", error));
  }
});
