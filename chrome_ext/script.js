chrome.browserAction.onClicked.addListener(function () {
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    var currentUrl = tabs[0].url;

    fetch("http://localhost:8000/process_auction", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ auction_url: currentUrl }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Auction Data:", data);
        // You can add code here to display the data in the extension popup
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  });
});
