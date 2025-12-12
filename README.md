# 🎮 Connect 4 – Real-Time Multiplayer Game
FastAPI backend + WebSockets + PostgreSQL + Redis + Appscheduler + Poetry + a lightweight HTML/JS frontend.

A complete real-time Connect 4 implementation with matchmaking, move validation, auto turn timeout, JWT authentication, and live board updates.

---

## 🚀 Features

### 🔐 Authentication
- Register / Login (JWT-based)
- Player profiles
- Token refresh support

### 🎮 Gameplay
- Create new games
- Join existing games
- Two-player turn-based logic
- Automatic winner detection
- Prevent illegal moves

### 🔄 Real-Time Updates
- WebSocket communication
- Redis Pub/Sub used as the real-time event bus
- Sync board state updates instantly between players
- Highlight winner’s chips

### 🕓 Game Review Mode
Replay any finished game with:
- Step forward / backward
- Jump to any move
- Full board evolution preview

### 📜 API Documentation
Interactive Swagger UI is available
---

## 🛠 Installation (Backend)

### Clone the project
```bash
git clone https://github.com/YOUR_REPO/connect4.git
cd connect4
```

###  Install the package manager
```bash
poetry install
eval $(poetry env activate)

```

###  Create .env 
Used the env.example to fill the env


### Apply migrations

```bash

alembic upgrade head
```

### Run the project 

```bash
uvicorn app.main:app --reload --port 8000
```
Make sure to give the right permissions to your redis while starting the project cause of th redis pub/sub


### Run the front code 
```bash
cd front_code_dir
python3 -m http.server 8080 

```
**And then visit http://localhost:8080/index.html**

Make sure to fix the front code urls , I mean the front code is not clean at all! So check it and change everywhere the code is sending requests to the backend. 
And add the localhost:8080 to the allowed origins


## How to run bot vs bot game? 

Open the the bot_vs_bot script, wherever you see #TODO that's the part you should change. You should change the players emails to your email and your opponent email. Right now the make_move method is just a random method which produces an int between 0 and 6 and puts in the col variable. 
You should replace it with your own algorithm code. When you run the last block you should visit the web-page and login with one of the current players emails to be able to see the the game. Rember you have just 20 sec to do it! 

## How to run human vs bot game?

Just like running bot vs bot game but this time you just have to have one make_move method which blongs to the bot. When you run the last block of the script you should go visit the web-page and go the watch-your-code-game . Remeber to be logged in with the right email. You are the human-player you should't login with the bot-related-email