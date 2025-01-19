import asyncio
import websockets
import json
from genai import generate_game_data
from collections import defaultdict

# Store players, audience, and game data
players = []
audience = []
game_data = {}
theme = ""
quit = False

# Event to signal that the theme has been selected
theme_selected_event = asyncio.Event()

# Send game data to players
async def send_to_players():
    for player in players:
        await player["websocket"].send(json.dumps({
            "type": "game_prompt",
            "prompt": game_data["prompt"],
            "twist": game_data["twist"]
        }))

# Handle player connections
async def handle_player(websocket):
    global theme, game_data
    players.append({
        "websocket": websocket,  # Store WebSocket connection
        "name": f"Player {len(players) + 1}",  # Assign a player name (you can change this logic)
        "score": 0  # Initialize score, or any other data you need
    })
    print(f"Player connected: {websocket.remote_address}")

    try:
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "theme_selection":
                # Check if the theme is already set
                if theme:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": f"Theme has already been set to '{theme}'."
                    }))
                else:
                    theme = data["theme"]
                    theme_selected_event.set()  # Signal that the theme has been selected
                    await websocket.send(json.dumps({
                        "type": "confirmation",
                        "message": f"Theme '{theme}' selected!"
                    }))
                    print(f"Theme selected: {theme}")

                    # Wait for game data to be generated before notifying players
                    await theme_selected_event.wait()  # Ensure game_data is populated
                    if game_data:  # Verify game_data exists
                        await send_to_players()

    except websockets.exceptions.ConnectionClosed:
        print(f"Player disconnected: {websocket.remote_address}")

    finally:
        removed_player = next((p for p in players if p["websocket"] == websocket), None)
        players.remove(removed_player)

# Function to get a player by name
def get_player_by_name(player_name):
    player = next((p for p in players if p["name"] == player_name), None)
    return player

# Handle audience connections
async def handle_audience(websocket):
    global quit

    audience.append(websocket)
    print(f"Audience member connected: {websocket.remote_address}")

    try:
        await websocket.send(json.dumps({
            "type": "game_status",
            "message": "Debate Round is Ongoing!"
        }))

        async for message in websocket:
            data = json.loads(message)
            if data.get("type") == "vote":

                voted_player = data.get("player")
                player = get_player_by_name(voted_player)

                if player:
                    player["score"] += 1  # Increment score of the voted player
                    print(f"Vote received for {voted_player}")
                else: 
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": f"Player {voted_player} does not exist!"
                    }))

            elif data.get("type") == "quit":
                print("Quit message received. Ending game...")
                quit = True  # Set the quit flag to True

    except websockets.exceptions.ConnectionClosed:
        print(f"Audience member disconnected: {websocket.remote_address}")

    finally:
        audience.remove(websocket)

# Timer for debate time
async def game_timer():
    global theme
    await asyncio.sleep(2)  # 2-minute debate time
    theme = ""
    print("Time's up!")
    await announce_winner()

# Announce the winner at the end of the round
async def announce_winner():
    winner = max(players, key=lambda p: p["score"], default=None)
    result = {
        "type": "winner",
        "winner": winner["name"]
    }
    for player in players:
        await player["websocket"].send(json.dumps(result))
    for audi in audience:
        await audi.send(json.dumps(result))

# Main function
async def main():
    global game_data, theme, quit

    # Start WebSocket servers
    print("Starting WebSocket servers...")
    player_server = await websockets.serve(handle_player, "localhost", 8765)
    audience_server = await websockets.serve(handle_audience, "localhost", 8766)
    print("Servers started...")

    while True:
        print("Waiting for theme selection...")
        await theme_selected_event.wait()
        theme_selected_event.clear()  # Reset the event for the next round

        # Generate the game prompt and twist
        game_data = generate_game_data("generate a prompt", theme)
        print("Game data generated:", game_data)

        # Notify players of the game start
        await send_to_players()

        # Start the game timer
        await game_timer()

        if quit:
            print("Game is ending...")
            await announce_winner()

        for player in players:#reset scores of players to 0
            player["score"] = 0

        game_data = {}#reset game_data to none
        print("THINGS ARE RESET")

    # Clean up WebSocket servers
    player_server.close()
    await player_server.wait_closed()
    audience_server.close()
    await audience_server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
