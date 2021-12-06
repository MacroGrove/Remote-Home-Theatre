window.addEventListener("DOMContentLoaded", function() {
    // on page load, load all current messages
	loadMessages();
    
    // attach an event listener to the send button to post messages
    const messageButton = document.getElementById("message-button");
    messageButton.addEventListener("click", postMessage);
});

// load messages from database
async function loadMessages() {

    /* Steps
        1. get the articleID from the DOM so correct comments can be loaded
        2. fetch the comments list from the server
        3. insert every comment from this list into the comments section
    */
    
    const roomID = document.getElementById("roomID").value;
    return fetch(`/api/v1/messages/${roomID}/`)
        .then(validateJSON)
        .then(messageData => {
            for (const message of messageData.messages) {
                insertMessage(message);
            }
        })
        .catch(error => {
            console.log("Message Fetch Failed: ", error);
        });
}

// update messages from database
async function updateMessages() {

    /* Steps
        1. get the articleID from the DOM so correct comments can be loaded
        2. fetch the comments list from the server
        3. insert every comment from this list into the comments section
    */
    
    const roomID = document.getElementById("roomID").value;

    return fetch(`/api/v1/messages/${roomID}/`)
        .then(validateJSON)
        .then(messageData => {
            for (const message of messageData.messages) {
                if(document.getElementById(message.id) == null) {
                    insertMessage(message);
                }
            }
        })
        .catch(error => {
            console.log("Message Fetch Failed: ", error);
        });
}

/**
 * Asynchronously add a div with all messagse from db to the page.
 * 
 * @param {Message} message a Message object from db
 */
async function insertMessage(message) {

    /* Steps
        1. get a reference to the messages container
        2. create a new div to hold the new comment
        3. add the 'message' class to the div for CSS
        4. add this message div to the messages container
    */
    if (message.message !="") {
        const chat = document.getElementById("message-list");
        const head = document.createElement("b");
        head.innerText = message.user.username + " " + message.timestamp;
        const body = document.createElement("p");
        body.setAttribute("id", message.id)
        body.innerText = message.message;
        chat.appendChild(head);
        chat.appendChild(body);

        // Clear message field
        let field = document.getElementById("message-field");
        field.value = "";
    }
}

// send message to database
async function postMessage() {

     /* Steps
        1. get the roomID and comment text from the DOM
        2. create a new comment object to be posted
        3. create a new POST fetch request
        4. once POST is fulfilled, insert comment into the page
    */

    const roomID = document.getElementById("roomID").value;
    const messageText = document.getElementById("message-field").value;
    const message = {
        "roomID": roomID,
        "message": messageText
    };

    return fetch(`/api/v1/messages/${roomID}/`, {
        method: "POST",
        headers: {
            "content-Type": "application/json"
        },
        body: JSON.stringify(message)
        })
        .then(validateJSON)
        .then(insertMessage)
        .catch(error => {
            console.log("Message Post Failed: ", error)
        });
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