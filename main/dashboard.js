const socket = new WebSocket("ws://localhost:8765");
let players = [];
let roles = {};

socket.onopen = () => {
    console.log("Connected to WebSocket");
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "room_update") {
        updateRoomDetails(data.roomCode, data.players);
    } else if (data.type === "start_game") {
        sessionStorage.setItem("roles", JSON.stringify(data.roles)); // Save roles for the game
        window.location.href = "game.html";
    }
};

function updateRoomDetails(roomCode, playerList) {
    document.getElementById("roomCode").textContent = roomCode;
    players = playerList;
    document.getElementById("playerCount").textContent = players.length;

    const playerListElement = document.getElementById("players");
    playerListElement.innerHTML = players
        .map((player) => `<li>${player} - ${roles[player] || "Unassigned"}</li>`)
        .join("");
}

document.getElementById("assignRolesBtn").onclick = () => {
    roles = {}; // Reset roles
    players.forEach((player, index) => {
        if (index < 2) roles[player] = "Debater";
        else roles[player] = "Audience";
    });

    alert(`Roles assigned:\nDebaters: ${players.slice(0, 2).join(", ")}\nAudience: ${players.slice(2).join(", ")}`);
    document.getElementById("startGameBtn").disabled = false; // Enable Start Game button
    updateRoomDetails(document.getElementById("roomCode").textContent, players); // Refresh player list
};

document.getElementById("startGameBtn").onclick = () => {
    socket.send(
        JSON.stringify({
            type: "start_game",
            roles,
        })
    );
};
