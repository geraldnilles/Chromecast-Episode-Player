
function bind_show(){
    var buttons = document.querySelectorAll("button.show");
	for (var i = 0; i < buttons.length; i++){
        var b = buttons[i];
        b.onclick = function(e){
            // Remove the on-click for now so that we cant add more buttons
            var value = e.target.closest("button").innerText;
            var count = document.querySelector("input.episodeCount").value;
            send_request("show/"+value+"/"+count+"/"+get_device_name());
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
            send_request("volume/"+value+"/"+get_device_name());
        }
    }
}

function bind_stop(){
    var buttons = document.querySelectorAll("button.stop");
	for (var i = 0; i < buttons.length; i++){
        var b = buttons[i];
        b.onclick = function(e){
            // Remove the on-click for now so that we cant add more buttons
            send_request("stop"+"/"+get_device_name());
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

function bind_slider(){
    var sliders = document.querySelectorAll("input.episodeCount");
	for (var i = 0; i < sliders.length; i++){
        var s = sliders[i];
        // s.value = 5;
        document.querySelector("span.episodeCount").innerText = s.value;
        s.onchange = function(e){
            // alert("Slider Moved "+e.target.value);
            document.querySelector("span.episodeCount").innerText = e.target.value;
        }
    }
}

function get_device_name(){
    /* Returns the name of the chromecast device which is currently selected
     * by the DOM elements
     */
    return document.querySelector("button.device.active").innerText;
}

function bind_device_toggle(){
    var buttons = document.querySelectorAll("button.device");
    // By default, activate the first device in the list
    buttons[0].classList.add("active");
    buttons.forEach(function(b){
    	if ( b.innerText == "Bedroom TV" ){
		b.classList.add("active");
	}

        b.onclick = function(e){
            buttons.forEach(function(a){
                a.classList.remove("active"); 
            });
            e.target.classList.add("active");
        }
    });
}


function bind_buttons(){
    bind_show();
    bind_volume();
    bind_stop();
    bind_slider();
    bind_device_toggle();
}

bind_buttons();

