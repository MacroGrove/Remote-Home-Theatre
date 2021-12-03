window.addEventListener("DOMContentLoaded", function() {

     // on page load, load all current videos in queue
     loadQueue();

     // attach an event listener to the send button to post messages
     const queueButton = document.getElementById("queue-button")
     queueButton.addEventListener("click", storeQueueVideo)
});

// load messages from database
async function loadQueue() {
    const room_id = document.getElementById("roomID").value;
    fetch(`/api/v1/queue/${room_id}`)
        .then(validateJSON)
        .then(queueData => {
            for (const video of queueData.videos) {
                insertVideo(video);
            }
        })
        .catch(error => {
            console.log("Message Fetch Failed: ", error)
        });
}

/**
 * Asynchronously add a div with all messagse from db to the page.
 * 
 * @param {Array.<queueVideo>} queue an array of Message objects from db
 */
async function insertVideo(video) {
    
    const queue = document.getElementById("queue-list");
    const item = document.createElement("p");
    item.innerText = video.url;
    queue.appendChild(item);
}

// send message to database
async function storeQueueVideo() {
    /* Steps
        1. get the roomID and comment text from the DOM
        2. create a new comment object to be posted
        3. create a new POST fetch request
        4. once POST is fulfilled, insert comment into the page
    */

    const roomID = document.getElementById("roomID").value;
    const url = document.getElementById("queue-field").value;
    const queueVideo = {
        "roomID": roomID,
        "url": url
    };

    return fetch(`/api/v1/queue/${roomID}/`, {
        method: "POST",
        headers: {
            "content-Type": "application/json"
        },
        body: JSON.stringify(queueVideo)
        })
        .then(validateJSON)
        .then(insertVideo)
        .catch(error => {
            console.log("Queue Post Failed: ", error)
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