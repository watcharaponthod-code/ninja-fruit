# 🍎 Ninja Fruit - AI Pose-Based Fruit Picking Game

A real-time interactive game where players slash fruits using body movements captured by webcam, processed with **YOLOv8 Pose Detection**.

---

## 🎮 Demo Video

https://github.com/watcharaponthod-code/Ninja_fruit/raw/main/demo/demo-gameplay.mp4

---

## 🧠 ML Data Flow — AI Pipeline

> แสดงการไหลของข้อมูลตั้งแต่กล้องจนถึงการแสดงผลบนจอ

```mermaid
flowchart TD
    Webcam([📷 Webcam]):::green

    subgraph cam["📁 camera.py — TrackerCamera"]
        direction TB
        Capture[OpenCV\nVideoCapture]
        YOLO[YOLOv8 Pose Model\nyolov8n-pose.pt]
        Assign[Player Assigner\nleft / center / right]
    end

    subgraph gm["📁 game.py — GameManager"]
        direction TB
        HandHist[Hand History\nTracking × 6 frames]
        SlashDet[Slash Detection\nmovement > 15 px]
        Collision[Fruit / Bomb\nCollision Check]
        Score[Score & Combo\nSystem]
        Particles[Particle Effects]
    end

    subgraph ml["📁 main.py — Game Loop @ 30 FPS"]
        direction TB
        Timer[Game Timer\n60 seconds]
        Renderer[Pygame Renderer\nblit + draw]
    end

    Display([🖥️ Display Output]):::blue

    Webcam --> Capture
    Capture -->|BGR frame| YOLO
    YOLO -->|17 keypoints per person| Assign
    Assign -->|player_keypoints\ndict| HandHist

    HandHist --> SlashDet
    SlashDet -->|fruit.slash\np1 → p2| Collision
    Collision -->|fruit cut| Score
    Collision -->|visual| Particles

    Score --> Renderer
    Particles --> Renderer
    Timer --> Renderer
    Renderer --> Display

    classDef green fill:#6dbf67,stroke:#4a9e45,color:#fff
    classDef blue  fill:#5b7fd4,stroke:#3a5db0,color:#fff
```

### 🔍 Component Breakdown

| Component | File | Role |
|---|---|---|
| **Webcam** | — | Physical camera input |
| **OpenCV VideoCapture** | `camera.py` | Captures & mirrors each frame |
| **YOLOv8 Pose Model** | `camera.py` | Detects people → 17 COCO keypoints per person |
| **Player Assigner** | `camera.py` | Maps track IDs → Player 1/2/3 by X-position |
| **Hand History** | `game.py` | Stores last 6 wrist positions (keypoints 9 & 10) |
| **Slash Detection** | `game.py` | Triggers when hand moves > 15 px per frame |
| **Fruit/Bomb Collision** | `game.py` | Line-circle distance check between hand path & fruit |
| **Score & Combo** | `game.py` | +1 pt / fruit, combo bonus every 3 cuts, -5 for bomb |
| **Particle Effects** | `game.py` | Juice VFX on cut / explosion |
| **Game Timer** | `main.py` | 60-second countdown |
| **Pygame Renderer** | `main.py` | Composites frame + fruits + scores + timer |

---

## 🏗️ Class Architecture

```mermaid
classDiagram
    class TrackerCamera {
        +YOLO model
        +VideoCapture cap
        +dict track_to_player
        +update() rgb_frame, player_keypoints
        +assign_players(track_ids, x_centers)
        +release()
    }

    class GameManager {
        +dict scores
        +list fruits
        +list particles
        +dict hand_history
        +dict combo_count
        +spawn_fruit()
        +update(player_keypoints)
        +draw(surface, player_keypoints)
    }

    class Fruit {
        +bool is_bomb
        +float x, y
        +float speed_x, speed_y
        +bool is_cut
        +update()
        +draw(surface)
        +slash(p1, p2) bool
    }

    class Particle {
        +float x, y, vx, vy
        +int life
        +update()
        +draw(surface)
    }

    GameManager "1" --> "many" Fruit
    GameManager "1" --> "many" Particle
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Pose Detection | YOLOv8 Nano (`yolov8n-pose.pt`) |
| Computer Vision | OpenCV (`cv2`) |
| Game Engine | Pygame |
| Tracking | YOLO built-in multi-object tracking (`persist=True`) |
| Language | Python 3 |

## 📦 Installation

```bash
pip install -r requirements.txt
python main.py
```
