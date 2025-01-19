const socket = new WebSocket("ws://localhost:8765");

document.addEventListener("DOMContentLoaded", () => {
    const roomCode = sessionStorage.getItem("roomCode") || "ROOM123";
    document.getElementById("roomCode").textContent = roomCode;
});

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "vote_update") {
        updateVoteCounts(data.votes);
    }
};

function updateVoteCounts(voteData) {
    document.getElementById("debater1Votes").textContent = `Debater 1: ${voteData["Debater 1"] || 0} votes`;
    document.getElementById("debater2Votes").textContent = `Debater 2: ${voteData["Debater 2"] || 0} votes`;
}

function vote(debater) {
    socket.send(
        JSON.stringify({
            type: "vote",
            player: debater,
        })
    );
    alert(`Voted for ${debater}`);
}
