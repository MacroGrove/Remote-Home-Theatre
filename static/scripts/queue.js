window.addEventListener("DOMContentLoaded", function() {

    // on page load, load all current videos in queue
    loadQueue();

    // attach an event listener to the send button to post links
    const queueButton = document.getElementById("queue-button")
    queueButton.addEventListener("click", postQueueVideo)
});

// load links from database
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
            console.log("Queue Fetch Failed: ", error)
        });
}

// udpate links from database
async function updateQueue() {
    const room_id = document.getElementById("roomID").value;
    fetch(`/api/v1/queue/${room_id}`)
        .then(validateJSON)
        .then(queueData => {
            for (const video of queueData.videos) {
                if(document.getElementById(video.id) == null) {
                    insertVideo(video);
                }
            }
        })
        .catch(error => {
            console.log("Queue Fetch Failed: ", error)
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
    item.setAttribute("id", video.id)
    queue.appendChild(item);

    // Clear queue input
    let field = document.getElementById("queue-field")
    field.value = "";
}

// send queued video to database
async function postQueueVideo() {
    /* Steps
        1. get the roomID and url text from the DOM
        2. create a new url object to be posted
        3. create a new POST fetch request
        4. once POST is fulfilled, insert a url into the page
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