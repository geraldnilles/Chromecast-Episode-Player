
function bind_forward(){
    var buttons = document.querySelectorAll("button.forward");
	for (var i = 0; i < buttons.length; i++){
        var b = buttons[i];
        b.onclick = function(e){
            // Remove the on-click for now so that we cant add more buttons
            var value = e.target.closest("button").value;
            send_request("forward/"+value);
        }
    }
}

function bind_rewind(){
    var buttons = document.querySelectorAll("button.rewind");
	for (var i = 0; i < buttons.length; i++){
        var b = buttons[i];
        b.onclick = function(e){
            // Remove the on-click for now so that we cant add more buttons
            var value = e.target.closest("button").value;
            send_request("rewind/"+value);
        }
    }
}

function bind_reset(){
    var buttons = document.querySelectorAll("button.reset");
	for (var i = 0; i < buttons.length; i++){
        var b = buttons[i];
        b.onclick = function(e){
            // Remove the on-click for now so that we cant add more buttons
            var value = e.target.closest("button").value;
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
    bind_forward();
    bind_rewind();
    bind_reset();
}

bind_buttons();

