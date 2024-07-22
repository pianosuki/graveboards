# Graveboards Backend

## Description

Graveboards aims to provide a platform for both players and mappers to facilitate the discovery, leaderboards, and snapshot-based archival of unranked osu! beatmaps

Frontend: https://github.com/FlavioAngnes/graveboards-frontend

## Features

- **Leaderboards**
  - One-time OAuth login to automatically track your scores on Verified unranked beatmaps
- **Discovery**
  - Algorithm-based recommendation system to find beatmaps beased on your tastes **(Not implemented yet)**
- **Filtering**
  - Extensive filtering and searching capabilities including skillsets like rhythm complexity and content like jumps/streams **(Not implemented yet)**
- **Archiving**
  - Rudimentary version control system for taking snapshots of beatmaps and beatmapsets

## Installation

### Prerequisites

- Python 3.12+

### Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/pianosuki/graveboards.git
    cd graveboards
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Create the `.env` file:
    ```
    SECRET_KEY=<Some secret key>
    CLIENT_ID=<osu! API client ID>
    CLIENT_SECRET=<osu! API client secret>
    OSU_USER_ID=<Your osu! user ID>
    API_KEY=<Graveboards API key for the frontend to use>
    ```

5. Run the application:
    ```bash
    # Development mode:
    python main.py
    ```

## Documentation

The API spec can be viewed locally at: http://127.0.0.1:8000/api/v1/ui
