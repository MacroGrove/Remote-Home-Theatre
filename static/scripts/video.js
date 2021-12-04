
window.addEventListener("DOMContentLoaded", function() {
  //Load the IFrame Player API code asynchronously.
  var tag = document.createElement('script');

  tag.src = "https://www.youtube.com/iframe_api";
  var firstScriptTag = document.getElementsByTagName('script')[0];
  firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
  

  //onYouTubeIframeAPIReady()


});

setInterval(function() {
  onYouTubeIframeAPIReady()
}, 3000);



async function onYouTubeIframeAPIReady()  {

  let url

  const roomID = document.getElementById("roomID").value;
  var player = document.getElementById('player');
  console.log('cycle');
  fetch(`/api/v1/video/${roomID}/`)
        .then(validateJSON)
        .then(videoData => {
            url = videoData.url
        })
        .then(function () {
          const id = url.substring(32, 43);
          player = new YT.Player('player', {
            height: '480',
            width: '854',
            videoId: id,
            playerVars: {
              'playsinline': 1
            },
            events: {
              'onReady': onPlayerReady,
            //  'onStateChange': onPlayerStateChange
            }
           });
        })
        .then(function (){
        })
        .catch(error => {
            console.log("Message Fetch Failed: ", error);
        });
      


  //Create an <iframe> (and YouTube player) after the API code downloads.

  
    
}


//API calls this function when the video player is ready.
function onPlayerReady(event) {
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