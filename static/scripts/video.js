
window.addEventListener("DOMContentLoaded", function() {
  //Load the IFrame Player API code asynchronously.
  var tag = document.createElement('script');

  tag.src = "https://www.youtube.com/iframe_api";
  var firstScriptTag = document.getElementsByTagName('script')[0];
  firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
  
  // getYouTubeVideo()
  const videoButton = document.getElementById("video-button");
  videoButton.addEventListener("click", patchYouTubeVideo)
});

setInterval(function() {
  getYouTubeVideo()
  updateMessages()
  updateQueue()
}, 3000);

async function getYouTubeVideo()  {
  let url
  const roomID = document.getElementById("roomID").value;

  // console.log('cycle');
  fetch(`/api/v1/video/${roomID}/`)
        .then(validateJSON)
        .then(videoData => {
            url = videoData.url
        })
        .then(function () {
          insertYouTubeVideo(url)
        })
        .catch(error => {
            console.log("Message Fetch Failed: ", error);
        });  //Create an <iframe> (and YouTube player) after the API code downloads.
}

// async function insertYouTubeVideo(url) {
//   let player = document.getElementById('player');
//   const id = url.substring(32, 43);
//   player = new YT.Player('player', {
//     height: '480',
//     width: '854',
//     videoId: id,
//     playerVars: {
//       'playsinline': 1
//     },
//     events: {
//       'onReady': onPlayerReady,
//     //  'onStateChange': onPlayerStateChange
//     }
//   });
// }
async function insertYouTubeVideo(url) {
  let tru_url = url;
  if(url.includes("youtube")){
    tru_url = url.replace("watch?v=","embed/");
  }
  const player = document.getElementById("player");

  if(player.firstChild){
    const currVid = player.firstChild
    if (currVid.src != tru_url){
      currVid.src = tru_url;
    }
  }
  else {
    const video = document.createElement("iframe");
    video.src = tru_url;
    video.width = "854";
    video.height = "480";
    player.appendChild(video);
  }


}

async function patchYouTubeVideo() {
  const roomID = document.getElementById("roomID").value;
  const url = document.getElementById("video-field").value;
  const video = {
    "roomID": roomID,
    "url": url
  };

  return fetch(`/api/v1/video/${roomID}/`, {
    method: "PATCH",
    headers: {
      "content-Type": "application/json"
    },
    body: JSON(stringify(video))
  })
  .then(validateJSON)
  .then(function () {
    insertYouTubeVideo(url)
  })
  .catch(error => {
    console.log("Video Patch Failed: ", error)
  });
}

//API calls this function when the video player is ready.
async function onPlayerReady(event) {
  event.target.playVideo();
}

//The API calls this function when the player's state changes.
//    The function indicates that when playing a video (state=1),
//    the player should play for six seconds and then stop.
//var done = false;
//function onPlayerStateChange(event) {
//  if (event.data == YT.PlayerState.PLAYING && !done) {
//    setTimeout(stopVideo, 6000);
//    done = true;
//  }
//}

async function playVideo() {
  player.playVideo();
}

async function stopVideo() {
  player.stopVideo();
}

async function validateJSON(response) {
    if (response.ok) {
        return response.json();
    } else {
        return Promise.reject(response);
    }
}