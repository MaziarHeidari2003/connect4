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