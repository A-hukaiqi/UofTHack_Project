// WebSocket connection for the lobby
const socket = new WebSocket('ws://localhost:8765');

// Players and roles (simplified for now)
let players = ["Player 1", "Player 2", "Player 3", "Player 4"];
const roles = {}; // Automatically assign roles
const isHost = sessionStorage.getItem('role') === 'host';

// Handle WebSocket connection
socket.onopen = () => {
    console.log('Connected to WebSocket');
    setupPlayers(); // Set up dummy players
    makeButtonsClickable(); // Enable all buttons
};
socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "room_update") {
        updateRoomDetails(data.roomCode, data.players);
    }
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    // Handle room update
    if (data.type === "room_update") {
        updateRoomDetails(data.roomCode, data.players);
    }

    // Handle start game
    if (data.type === "start_game") {
        console.log("Start game message received!");
        sessionStorage.setItem("roles", JSON.stringify(data.roles)); // Save roles in sessionStorage
        window.location.href = "game.html"; // Redirect all players to the game page
    }
};



// On game.html load
document.addEventListener("DOMContentLoaded", () => {
    const roles = JSON.parse(sessionStorage.getItem("roles"));
    const playerRole = roles[sessionStorage.getItem("playerName")]; // Replace with actual player identifier
    if (playerRole === "debater") {
        document.getElementById("debaterView").classList.remove("hidden");
    } else if (playerRole === "audience") {
        document.getElementById("audienceView").classList.remove("hidden");
    }
});



function updateRoomDetails(roomCode, playerList) {
    document.getElementById("roomCode").textContent = roomCode;
    const playerListElement = document.getElementById("players");
    playerListElement.innerHTML = playerList
        .map(player => `<li>${player}</li>`)
        .join('');
    document.getElementById("playerCount").textContent = playerList.length;
}


// Automatically set up dummy players and roles
function setupPlayers() {
    roles[players[0]] = "debater";
    roles[players[1]] = "debater";
    for (let i = 2; i < players.length; i++) {
        roles[players[i]] = "audience";
    }
    updatePlayerList();
}

// Update player list with roles
function updatePlayerList() {
    const playerListElement = document.getElementById('players');
    const playerCountElement = document.getElementById('playerCount');
    playerListElement.innerHTML = players
        .map((player) => `
            <li>
                ${player} - ${roles[player] || "Unassigned"}
            </li>
        `)
        .join('');
    playerCountElement.textContent = players.length;
}

// Enable buttons
function makeButtonsClickable() {
    document.getElementById('assignRolesStep').onclick = assignRoles;
    document.getElementById('startGameStep').onclick = startGame;
}

// Simulate assigning roles
function assignRoles() {
    console.log("Roles have been assigned!");
    alert("Roles automatically assigned:\n- Debaters: Player 1, Player 2\n- Audience: Player 3, Player 4");
}

// Start the game
function startGame() {
    console.log("Starting the game...");
    if (isHost) {
        socket.send(
            JSON.stringify({
                type: "start_game",
                roles, // Send roles to the backend
            })
        );
    }
}

