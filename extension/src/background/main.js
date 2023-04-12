chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if ('message' in request) {
        console.log(request.message)
    }
})
