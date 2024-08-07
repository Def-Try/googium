function padNumber(k) {
    /* Add padding if less than 0 */
    if (k < 10)
        return "0" + k;
    else
        return k;
}

function updateTime() {
    var date = new Date();
    var hour = date.getHours();
    var min = date.getMinutes();
    var sec = date.getSeconds();
    hour = padNumber(hour);
    min  = padNumber(min);
    sec  = padNumber(sec);

    document.getElementById("clock").innerText = hour + ":" + min + ":" + sec;
}

updateTime();
setInterval(updateTime, 1000);