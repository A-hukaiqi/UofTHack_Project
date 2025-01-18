import asyncio
import websockets
import json
from genai import generate_game_data

# Store players, audience, and game data
players = []
audience = []
game_data = {}

# Send game data to players
async def send_to_players():
    for player in players:
        await player.send(json.dumps({
            "type": "game_prompt",
            "prompt": game_data["prompt"],
            "twist": game_data["twist"]
        }))

# Handle player connections
async def handle_player(websocket):
    players.append(websocket)
    print(f"Player connected: {websocket.remote_address}")

    try:
        await send_to_players()
        await websocket.wait_closed()

    except websockets.exceptions.ConnectionClosed:
        print(f"Player disconnected: {websocket.remote_address}")
    finally:
        players.remove(websocket)

# Handle audience connections
async def handle_audience(websocket):
    audience.append(websocket)
    print(f"Audience member connected: {websocket.remote_address}")

    try:
        await websocket.send(json.dumps({
            "type": "game_status",
            "message": "Debate Round is Ongoing!"
        }))

        async for message in websocket:
            pass  # Add audience voting logic here if needed

    except websockets.exceptions.ConnectionClosed:
        print(f"Audience member disconnected: {websocket.remote_address}")
    finally:
        audience.remove(websocket)

# Timer for debate time
async def game_timer():
    await asyncio.sleep(120)  # 2-minute debate time
    print("Time's up!")
    await announce_winner()

# Announce the winner at the end of the round
async def announce_winner():
    winner = "Player 1"  # Placeholder logic for determining winner
    result = {
        "type": "winner",
        "winner": winner
    }

    for ws in players + audience:
        await ws.send(json.dumps(result))

# Main function
async def main():
    global game_data

    # Generate the game prompt and twist
    game_data = await generate_game_data()

    # Start the game timer
    asyncio.create_task(game_timer())

    # Start WebSocket servers
    server = await websockets.serve(handle_player, "localhost", 8765)
    audience_server = await websockets.serve(handle_audience, "localhost", 8766)

    print("Server started...")
    await server.wait_closed()
    await audience_server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
