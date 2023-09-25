// datetime.js

function getCurrentDateTime() {
    var currentDateTime = new Date();
    var dateTimeString = currentDateTime.toLocaleString();
    document.getElementById("datetime").innerHTML = dateTimeString;
}
