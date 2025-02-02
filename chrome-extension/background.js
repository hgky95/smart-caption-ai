const OPTIONAL_FEEDBACK_COUNT = 2;
const REQUIRED_FEEDBACK_COUNT = 5;
const FEEDBACK_API = "http://127.0.0.1:5000/feedback";

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({ usageCount: 0 });
});

chrome.action.onClicked.addListener(async (tab) => {
  const { usageCount } = await chrome.storage.local.get("usageCount");
  const { feedbackSubmitted } = await chrome.storage.local.get(
    "feedbackSubmitted"
  );

  const newCount = (usageCount || 0) + 1;
  await chrome.storage.local.set({ usageCount: newCount });

  chrome.tabs.sendMessage(tab.id, { action: "createIframe" });

  if (
    !feedbackSubmitted &&
    (newCount == OPTIONAL_FEEDBACK_COUNT || newCount >= REQUIRED_FEEDBACK_COUNT)
  ) {
    chrome.tabs.sendMessage(tab.id, {
      action: "showFeedback",
      isRequired: newCount >= REQUIRED_FEEDBACK_COUNT,
    });
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "submitFeedback") {
    fetch(FEEDBACK_API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(message.feedback),
    })
      .then(() => {
        chrome.storage.local.set({
          usageCount: 0,
          feedbackSubmitted: true,
        });
        sendResponse({ success: true });
      })
      .catch((error) => {
        console.error("Feedback submission failed:", error);
        sendResponse({ success: false });
      });

    return true; // Keep message channel open for async response
  }
});
