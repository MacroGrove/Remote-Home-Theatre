window.addEventListener("DOMContentLoaded", function() {
	const queueButton = document.getElementById("queue-button")
    queueButton.addEventListener("click", )
});

// load messages from database
async function loadQueue() {
    const room_id = document.getElementById("articleID").innerText;
    fetch(`/api/v1/queue/${room_id}`)
        .then(validateJSON)
        .then(messageData => {
            for (const queueVideo of queueVideoData.queue) {
                insertMessage(queueVideo);
            }
        })
        .catch(error => {
            console.log("Message Fetch Failed: ", error)
        });
}

async function getQueue() {
    return 
}

/**
 * Asynchronously add a div with all messagse from db to the page.
 * 
 * @param {Array.<queueVideo>} queue an array of Message objects from db
 */
async function insertMessage(queueVideo) {
    const chat = document.getElementById("queue-list");
    const item = document.createElement("p");
    item.innerText = queueVideo;
    queue.appendChild(item);
}

// send message to database
async function storeQueueVideo() {

}

/**
 * Validate a response to ensure the HTTP status code indcates success.
 * 
 * @param {Response} response HTTP response to be checked
 * @returns {object} object encoded by JSON in the response
 */
function validateJSON(response) {
    if (response.ok) {
        return response.json();
    } else {
        return Promise.reject(response);
    }
}