let song_or_playlist = "song";

function toggleSong(showFormId, hideFormId) {
    song_or_playlist = "song";
    document.getElementById(showFormId).style.display = 'flex';
    document.getElementById(hideFormId).style.display = 'none';
    document.getElementById("song_button").style.backgroundColor = '#BDD5E7';
    document.getElementById("playlist_button").style.backgroundColor = '#FFB480';
    document.getElementById("song_button").style.fontWeight = 'bold';
    document.getElementById("playlist_button").style.backgroundColor = '#FFB480';
    document.getElementById("playlist_button").style.fontWeight = 'normal';
    document.getElementById("song_button").onmouseenter = function()
                    {
                        this.style.backgroundColor = "#BDD5E7";
                    }
    document.getElementById("song_button").onmouseleave = function()
                    {
                        this.style.backgroundColor = "#BDD5E7";
                    }
    document.getElementById("playlist_button").onmouseenter = function()
                    {
                        this.style.backgroundColor = "#FEC98F";
                    }
    document.getElementById("playlist_button").onmouseleave = function()
                    {
                        this.style.backgroundColor = "#FFB480";
                    }
}
function togglePlaylist(showFormId, hideFormId) {
    song_or_playlist = "playlist";
    document.getElementById(showFormId).style.display = 'flex';
    document.getElementById(hideFormId).style.display = 'none';
    document.getElementById("song_button").style.backgroundColor = '#9ABDDC';
    document.getElementById("song_button").style.fontWeight = 'normal';
    document.getElementById("playlist_button").style.backgroundColor = '#FEC98F';
    document.getElementById("playlist_button").style.fontWeight = 'bold';
    document.getElementById("song_button").onmouseenter = function()
                    {
                        this.style.backgroundColor = "#BDD5E7";
                    }
    document.getElementById("song_button").onmouseleave = function()
                    {
                        this.style.backgroundColor = "#9ABDDC";
                    }
    document.getElementById("playlist_button").onmouseenter = function()
                    {
                        this.style.backgroundColor = "#FEC98F";
                    }
    document.getElementById("playlist_button").onmouseleave = function()
                    {
                        this.style.backgroundColor = "#FEC98F";
                    }
}

var ws = new WebSocket(("ws://localhost:8000/download"));
// gets back information from the server and displays it to the client
ws.onmessage = function(event) {
    var json_data = JSON.parse(event.data);
    var state = json_data.state;
    if (state === "error_666") {
        var message = json_data.message;
        document.getElementById("error_666_display").style.display = "flex";
        document.getElementById("error_666_display").textContent = message;
    } else if (state === "starting") {
        var song_name = json_data.song_name;
        document.getElementById("down_state_starting").style.display = "flex";
        document.getElementById("down_state_starting").textContent = `Starting download ${song_name}`;
    } else if (state === "downloading") {
        var perc = json_data.perc;
        document.getElementById("down_state_starting").style.display = "None";
        document.getElementById("down_state_progress").style.display = "flex";
        document.getElementById("down_state_progress").textContent = `Download progress is ${perc}`;
    } else if (state === "finished") {
        var link = json_data.link;
        document.getElementById("down_state_progress").style.display = "None";
        document.getElementById("down-state-finished").style.display = "flex";
        var downloadLink = document.createElement('a');
        downloadLink.href = link;
        downloadLink.id = "downloadAnchor";
        document.body.appendChild(downloadLink);
    }
}

function start_download(event) {
    if (song_or_playlist === "song")
        download_song(event);
}

function download_song(event) {
    var song_id = document.getElementById("song_id").value;
    var file_type = document.getElementById("file_type").value;
    var input = JSON.stringify({song_id, file_type});
    ws.send(input);
    document.getElementById("container").style.display = "None";
    document.getElementById("down-progression-container").style.display = "flex";
    input.value = '';
    event.preventDefault();
}

function download_ready(){
    var downloadLink = document.getElementById("downloadLink");
    downloadLink.click();
    document.body.removeChild(downloadLink);
}