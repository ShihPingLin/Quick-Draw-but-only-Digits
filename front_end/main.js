let canvas, ctx, flag = false,
    prevX = 0,
    currX = 0,
    prevY = 0,
    currY = 0,
    dot_flag = false;

let x = "black",
    y = 7;  // initial line width

/********** line width **********/
let current_width = 7;
function showVal(newVal) {
    y = newVal / 20 + 5;
    current_width = y;
    console.log(y);
}

/********** canvas part **********/
function init() {
    canvas = document.getElementById('can');
    ctx = canvas.getContext("2d");
    w = canvas.width;
    h = canvas.height;
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    canvas.addEventListener("mousemove", function (e) {
        findxy('move', e)
    }, false);
    canvas.addEventListener("mousedown", function (e) {
        findxy('down', e)
    }, false);
    canvas.addEventListener("mouseup", function (e) {
        findxy('up', e)
    }, false);
    canvas.addEventListener("mouseout", function (e) {
        findxy('out', e)
    }, false);
}

function color(obj) {
    switch (obj.id) {
        case "green":
            x = "green";
            break;
        case "blue":
            x = "blue";
            break;
        case "red":
            x = "red";
            break;
        case "yellow":
            x = "yellow";
            break;
        case "orange":
            x = "orange";
            break;
        case "black":
            x = "black";
            break;
        case "white":
            x = "white";
            break;
    }
    if (x == "white") y = 14;
    else y = current_width;
}

function draw() {
    ctx.beginPath();
    ctx.moveTo(prevX, prevY);
    ctx.lineTo(currX, currY);
    ctx.strokeStyle = x;
    ctx.lineWidth = y;
    ctx.stroke();
    ctx.closePath();
}

function erase() {
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

/*
// save image to display
function save() {
    document.getElementById("canvasimg").style.border = "2px solid";
    var dataURL = canvas.toDataURL();
    document.getElementById("canvasimg").src = dataURL;
    document.getElementById("canvasimg").style.display = "inline";

    console.log(dataURL);
}*/

function getImageData(ctx) {
    var w = canvas.width, h = canvas.height;
    var img = ctx.getImageData(0, 0, w, h).data;
    var arr = Array.from(img);
    return arr;
}

// save image and download
download_img = function (el) {
    // get image directly from context
    fetch(`${window.location.origin}/submit`, {
        body: JSON.stringify({ "features": getImageData(ctx) }),
        headers: {
            "content-type": "application/json"
        },
        method: "POST"
    })
        .then((response) => {
            if (response.status !== 200) {

            } else {
                response.json().then((data) => {
                    var pred = document.getElementById("return-number");
                    pred.innerHTML = data.prediction;
                });
            }
        });
};

const upload = () => {
    var digit = document.getElementById("digit");
    fetch(`${window.location.origin}/supervise`, {
        body: JSON.stringify({
            "features": getImageData(ctx),
            "gt": digit.value
        }),
        headers: {
            "content-type": "application/json"
        },
        method: "POST"
    });
    digit.value = "";
}

function findxy(res, e) {
    if (res == 'down') {
        prevX = currX;
        prevY = currY;
        currX = e.clientX - canvas.getBoundingClientRect().left;
        currY = e.clientY - canvas.getBoundingClientRect().top;

        flag = true;
        dot_flag = true;
        if (dot_flag) {
            ctx.beginPath();
            ctx.fillStyle = x;
            ctx.fillRect(currX, currY, 2, 2);
            ctx.closePath();
            dot_flag = false;
        }
    }
    if (res == 'up' || res == "out") {
        flag = false;
    }
    if (res == 'move') {
        if (flag) {
            prevX = currX;
            prevY = currY;

            currX = e.clientX - canvas.getBoundingClientRect().left;
            currY = e.clientY - canvas.getBoundingClientRect().top;
            draw();
        }
    }
}