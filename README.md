# 🍎 Ninja Fruit - AI Pose-Based Fruit Picking Game

A real-time interactive game where players "pick" or "slash" fruits using their body movements, captured via webcam and processed using **YOLOv8 Pose Detection**.

## 🎮 Demo Video

<video src="demo/demo-gameplay.mp4" controls width="100%">
  <p>Your browser doesn't support HTML video. <a href="demo/demo-gameplay.mp4">Download the video</a></p>
</video>

---

## 🚀 Overview

This project combines Computer Vision and Web Technologies to create an immersive gaming experience. It uses a Python backend for pose estimation and a Next.js frontend for the game interface (or integrated Python-based game logic).

---

## 🧠 ML Data Flow Architecture

The diagram below shows how data flows through the AI pipeline — from the **Kafka** message stream, through processing buffers and ML components, to final detection outputs.

```mermaid
flowchart TD
    kafka([kafka]):::green

    input_buffer([input_buffer]):::yellow
    rule_buffer([rule_buffer]):::yellow
    rule_processor([rule_processor]):::yellow
    forecaster_buffer([forecaster_buffer]):::yellow
    forecaster([forecaster]):::yellow
    estimator([estimator]):::yellow

    publisher_pred([publisher_pred]):::blue
    publisher_mse([publisher_mse]):::blue
    forecaster_detector([forecaster_detector]):::blue
    limit_detector([limit_detector]):::blue
    rule_detector([rule_detector]):::blue

    kafka --> input_buffer
    input_buffer --> rule_buffer
    rule_buffer --> rule_processor
    rule_processor --> forecaster_buffer
    forecaster_buffer --> forecaster
    forecaster --> estimator

    estimator --> publisher_pred
    estimator --> publisher_mse
    forecaster --> forecaster_detector
    rule_processor --> limit_detector
    rule_buffer --> rule_detector

    classDef green  fill:#6dbf67,stroke:#4a9e45,color:#fff
    classDef yellow fill:#f5c842,stroke:#d4a820,color:#333
    classDef blue   fill:#5b7fd4,stroke:#3a5db0,color:#fff
```

### 🔄 Data Flow Explanation

| Component | Type | Role |
|---|---|---|
| **kafka** | Source (🟢) | Real-time data stream input from sensors/events |
| **input_buffer** | Buffer (🟡) | Receives raw Kafka events and queues them |
| **rule_buffer** | Buffer (🟡) | Buffers data for rule-based evaluation |
| **rule_processor** | Processor (🟡) | Applies business rules and filters to data |
| **forecaster_buffer** | Buffer (🟡) | Prepares time-series window for forecasting |
| **forecaster** | ML Model (🟡) | Predicts future values using trained model |
| **estimator** | ML Model (🟡) | Estimates state / refines predictions |
| **publisher_pred** | Output (🔵) | Publishes model predictions downstream |
| **publisher_mse** | Output (🔵) | Publishes Mean Squared Error metrics |
| **forecaster_detector** | Detector (🔵) | Detects anomalies in forecasted data |
| **limit_detector** | Detector (🔵) | Triggers alerts when values exceed limits |
| **rule_detector** | Detector (🔵) | Fires when rule conditions are violated |

---

## 🏗️ System Architecture

```mermaid
flowchart LR
    subgraph Frontend["🌐 Frontend (Next.js)"]
        UI[Game UI]
        Canvas[Canvas Renderer]
    end

    subgraph Backend["⚙️ Backend (Python)"]
        Webcam[Webcam Capture]
        YOLO[YOLOv8 Pose]
        Logic[Game Logic]
    end

    subgraph AI["🤖 AI Pipeline"]
        Pose[Pose Keypoints]
        Gesture[Gesture Classifier]
    end

    Webcam --> YOLO --> Pose --> Gesture --> Logic
    Logic --> UI
    Logic --> Canvas
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Pose Detection | YOLOv8 Pose (`yolov8n-pose.pt`) |
| Backend | Python (`game.py`, `camera.py`, `main.py`) |
| Web Frontend | Next.js (`/web`) |
| Configuration | `settings.py` |

## 📦 Installation

```bash
pip install -r requirements.txt
python main.py
```
