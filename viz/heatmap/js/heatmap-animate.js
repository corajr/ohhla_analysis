var animating;
var animationInterval = 250;
var playPause = function () {
  if (animating) {
    clearInterval(animating);
    animating = false;
    document.getElementById("playPause").textContent = "\u25b6";
  } else {
    var searchTime = document.getElementById("searchTime"),
      now = parseInt(searchTime.value),
      min = parseInt(searchTime.min),
      max = parseInt(searchTime.max);
    if (now == max) {
      searchTime.value = min;
    }
    document.getElementById("playPause").textContent = "\u2759\u2759"; //.style("letter-spacing", "-2px")
    animating = setInterval(incrementTime, animationInterval);
  }
};

var incrementTime = function () {
  var searchTime = document.getElementById("searchTime"),
    now = parseInt(searchTime.value),
    max = parseInt(searchTime.max);
  if (now > (max - 1)) {
    playPause();
  } else {
    searchTime.value = (now + 1);
    timeAction();   
  }
};

var timeAction = function () {
  var queryTime = document.getElementById("searchTime").value;
  document.getElementById("timeDisplay").textContent = queryTime;
  endDate = parseInt(queryTime);
  updateMap(endDate);
};