window.addEventListener("DOMContentLoaded", function() {
	const messageButton = document.getElementById("message-button")
    messageButton.addEventListener("click", )
});

// load messages from database
async function loadMessages() {
    const room_id = document.getElementById("articleID").innerText;
    fetch(`/api/v1/messages/${room_id}`)
        .then(validateJSON)
        .then(messageData => {
            for (const message of messageData.messages) {
                insertMessage(message);
            }
        })
        .catch(error => {
            console.log("Message Fetch Failed: ", error)
        });
}

async function getMessages() {
    return 
}

/**
 * Asynchronously add a div with all messagse from db to the page.
 * 
 * @param {Array.<Message>} messages an array of Message objects from db
 */
async function insertMessage(message) {
    const chat = document.getElementById("message-list");
    const item = document.createElement("p");
    item.innerText = message;
    chat.appendChild(item);
}

// send message to database
async function storeMessage() {

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