import asyncio
import websockets
import json
import random

#stores players n audience (maube set player array max)
players = []
audience = []
game_data = {}

#send game data to players
async def send_to_players():
    for player in players:
        await player.send(json.dumps({
            "type": "game_prompt",
            "prompt": game_data["prompt"],
            "twist": game_data["twist"]
        }))

#handle player connections
async def handle_player(websocket, path):
    # Register the player
    players.append(websocket)
    print(f"Player connected: {websocket.remote_address}")

    try:
        #game prompt and twist to players
        await send_to_players()

       

    except websockets.exceptions.ConnectionClosed:
        print(f"Player disconnected: {websocket.remote_address}")
    finally:
        #remove the player from the list
        players.remove(websocket)

#handle audience connections
async def handle_audience(websocket, path):
    # Register the audience
    audience.append(websocket)
    print(f"Audience member connected: {websocket.remote_address}")

    try:
        # Send initial game data to audience
        await websocket.send(json.dumps({
            "type": "game_status",
            "message": "Debate Round is Ongoing!"
        }))

        # Listen for audience votes (this can be expanded with voting logic i didn't do it)
        async for message in websocket:
            #voting counter thing here
            pass

    except websockets.exceptions.ConnectionClosed:
        print(f"Audience member disconnected: {websocket.remote_address}")
    finally:
        #remove the audience from the list
        audience.remove(websocket)

#function to generate random game data (e.g prompts, twists)
def generate_game_data():
    prompts = ["Is AI a threat?", "Should we colonize Mars?", "Is climate change reversible?"]
    twists = ["Debate as medieval peasants", "Debate as ancient philosophers", "Debate as pirates"]
    game_data["prompt"] = random.choice(prompts)
    game_data["twist"] = random.choice(twists)

#whats up there is example qs i forced gpt to make lol. ideally we replace this with api calls from gemini or whatever

# timer for debate time?? set to 2 min can be reset
async def game_timer():
    await asyncio.sleep(120)  # 2-minute debate time
    print("Time's up!")
    
    # need to collect audience votes and calculate the winner
    # This can be implemented with vote counting logic
    await announce_winner()

# Function to announce the winner at the end of the round
async def announce_winner():
    winner = "Player 1"  #replace this with the actual winner based on votes need to do that logic
    result = {
        "type": "winner",
        "winner": winner
    }

    #send winner result to all players and audience
    for ws in players + audience:
        await ws.send(json.dumps(result))

# start overall
async def main():
    generate_game_data()  # Generate the game prompt and twist
    # Start the game timer
    asyncio.create_task(game_timer())

    # start websocket server for aud
    server = await websockets.serve(handle_player, "localhost", 8765)
    audience_server = await websockets.serve(handle_audience, "localhost", 8766)
    
    print("Server started...")

    
    await server.wait_closed()
    await audience_server.wait_closed()


asyncio.run(main())