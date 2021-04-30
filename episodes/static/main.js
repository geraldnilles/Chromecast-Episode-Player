
function bind_show(){
    var buttons = document.querySelectorAll("button.show");
	for (var i = 0; i < buttons.length; i++){
        var b = buttons[i];
        b.onclick = function(e){
            // Remove the on-click for now so that we cant add more buttons
            var value = e.target.closest("button").innerText;
            send_request("show/"+value);
        }
    }
}

function bind_volume(){
    var buttons = document.querySelectorAll("button.volume");
	for (var i = 0; i < buttons.length; i++){
        var b = buttons[i];
        b.onclick = function(e){
            // Remove the on-click for now so that we cant add more buttons
            var value = e.target.closest("button").value;
            send_request("volume/"+value);
        }
    }
}

function bind_stop(){
    var buttons = document.querySelectorAll("button.stop");
	for (var i = 0; i < buttons.length; i++){
        var b = buttons[i];
        b.onclick = function(e){
            // Remove the on-click for now so that we cant add more buttons
            send_request("stop");
        }
    }
}

function bind_reset(){
    var buttons = document.querySelectorAll("button.reset");
	for (var i = 0; i < buttons.length; i++){
        var b = buttons[i];
        b.onclick = function(e){
            // Remove the on-click for now so that we cant add more buttons
            send_request("reset");
        }
    }
}

function send_request(url){
    var request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            // Conver the database to JSON and render
            ;
        }
    };
    request.open("GET", url);
    request.send();
    
}


function bind_buttons(){
    bind_show();
    bind_volume();
    bind_stop();
    bind_reset();
}

bind_buttons();

