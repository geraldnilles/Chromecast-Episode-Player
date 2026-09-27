
// ---------------------------------------------------------------------------
// Shared command state.
//
// `in_flight` prevents double-firing a command while one is outstanding (the
// server can take several seconds to answer /show/). `status_el` is a small
// live-region element used to give the user feedback.
// ---------------------------------------------------------------------------
var in_flight = false;

function set_status(message, is_error) {
    var el = document.querySelector("#status");
    if (!el) {
        return;
    }
    el.textContent = message || "";
    el.classList.toggle("text-danger", !!is_error);
}

function send_request(url, success_message) {
    if (in_flight) {
        // Ignore clicks while a command is still running.
        return;
    }
    in_flight = true;
    set_status("Working\u2026", false);

    var request = new XMLHttpRequest();
    request.open("POST", url);
    request.timeout = 20000;

    request.onload = function () {
        in_flight = false;
        var ok = request.status >= 200 && request.status < 300;
        var payload = null;
        try {
            payload = JSON.parse(request.responseText);
        } catch (err) {
            payload = null;
        }
        if (ok && (!payload || payload.ok !== false)) {
            set_status(success_message || "Done", false);
        } else {
            var message = (payload && payload.error) || ("Command failed (HTTP " + request.status + ")");
            set_status(message, true);
        }
    };

    request.onerror = function () {
        in_flight = false;
        set_status("Network error \u2013 command not sent", true);
    };

    request.ontimeout = function () {
        in_flight = false;
        set_status("Timed out waiting for the server", true);
    };

    request.send();
}

function bind_show() {
    var buttons = document.querySelectorAll("button.show");
    for (var i = 0; i < buttons.length; i++) {
        var b = buttons[i];
        b.onclick = function (e) {
            var value = e.target.closest("button").innerText;
            var count = document.querySelector("input.episodeCount").value;
            var device = get_device_name();
            if (!device) {
                set_status("Select a device first", true);
                return;
            }
            send_request("./show/" + encodeURIComponent(value) + "/" + count + "/" + encodeURIComponent(device),
                         "Playing some episodes");
        };
    }
}

function bind_volume() {
    var buttons = document.querySelectorAll("button.volume");
    for (var i = 0; i < buttons.length; i++) {
        var b = buttons[i];
        b.onclick = function (e) {
            var value = e.target.closest("button").value;
            var device = get_device_name();
            if (!device) {
                set_status("Select a device first", true);
                return;
            }
            send_request("./volume/" + value + "/" + encodeURIComponent(device),
                         "Adjusting the volume");
        };
    }
}

function bind_stop() {
    var buttons = document.querySelectorAll("button.stop");
    for (var i = 0; i < buttons.length; i++) {
        var b = buttons[i];
        b.onclick = function (e) {
            var device = get_device_name();
            if (!device) {
                set_status("Select a device first", true);
                return;
            }
            send_request("./stop/" + encodeURIComponent(device),
                         "Stopping playback");
        };
    }
}

function bind_slider() {
    var sliders = document.querySelectorAll("input.episodeCount");
    for (var i = 0; i < sliders.length; i++) {
        var s = sliders[i];
        document.querySelector("span.episodeCount").innerText = s.value;
        s.onchange = function (e) {
            document.querySelector("span.episodeCount").innerText = e.target.value;
        };
    }
}

function get_device_name() {
    /* Returns the name of the chromecast device which is currently selected
     * by the DOM elements, or null if none is selected.
     */
    var active = document.querySelector("button.device.active");
    return active ? active.innerText : null;
}

function bind_device_toggle() {
    var buttons = document.querySelectorAll("button.device");
    if (!buttons.length) {
        return;
    }

    // Default-select exactly one device: prefer "Bedroom TV" if present,
    // otherwise fall back to the first device in the list.
    var default_button = null;
    for (var i = 0; i < buttons.length; i++) {
        if (buttons[i].innerText === "Bedroom TV") {
            default_button = buttons[i];
            break;
        }
    }
    if (!default_button) {
        default_button = buttons[0];
    }

    buttons.forEach(function (b) {
        b.classList.remove("active");
        b.onclick = function (e) {
            buttons.forEach(function (a) {
                a.classList.remove("active");
            });
            e.currentTarget.classList.add("active");
        };
    });

    default_button.classList.add("active");
}

function bind_buttons() {
    bind_show();
    bind_volume();
    bind_stop();
    bind_slider();
    bind_device_toggle();
}

// bfcache / standalone-web-app restore guard: do NOT auto-run anything when
// the page is restored from the back/forward cache. The app only ever acts on
// user clicks, and the command endpoints are POST + no-store, so a restored
// page cannot replay a stale command.
window.addEventListener("pageshow", function (e) {
    if (e.persisted) {
        in_flight = false;
        set_status("", false);
    }
});

bind_buttons();
