import cv2
from ultralytics import YOLO
import numpy as np
from settings import CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT

class TrackerCamera:
    def __init__(self):
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        
        # Use YOLOv8 nano pose model for real-time performance and tracking
        print("Loading AI Model (YOLOv8 Pose)...")
        self.model = YOLO('yolov8n-pose.pt')
        self.active = self.cap.isOpened()
        
        # Mapping YOLO track IDs to Player IDs (1, 2, 3)
        self.track_to_player = {}

    def assign_players(self, track_ids, x_centers):
        """Assign player 1 (left), 2 (center), 3 (right) based on initial X position.
           Keeps memory of who is who based on Track ID.
        """
        if len(self.track_to_player) == 0:
            if len(track_ids) >= 1:
                # Sort by X center
                sorted_indices = sorted(range(len(x_centers)), key=lambda i: x_centers[i])
                # Limit to 3 players
                num_players = min(len(sorted_indices), 3)
                for i in range(num_players):
                    self.track_to_player[track_ids[sorted_indices[i]]] = i + 1 # 1: Left, 2: Center, 3: Right
        else:
            # Check if there are new track IDs we haven't mapped yet
            current_mapped_players = [self.track_to_player[tid] for tid in track_ids if tid in self.track_to_player]
            missing_players = [p for p in [1, 2, 3] if p not in current_mapped_players]
            
            unmapped_tids = [tid for tid in track_ids if tid not in self.track_to_player]
            
            # Map unmapped IDs to missing player slots based on X position to keep left-to-right logic for new entries
            if unmapped_tids and missing_players:
                # Pair unmapped TIDs with their X centers
                unmapped_x = [(tid, x_centers[track_ids.index(tid)]) for tid in unmapped_tids]
                unmapped_x.sort(key=lambda item: item[1]) # Sort left-to-right
                
                missing_players.sort() # [1, 2, 3] left-to-right preference
                
                for i in range(min(len(unmapped_x), len(missing_players))):
                    self.track_to_player[unmapped_x[i][0]] = missing_players[i]

    def update(self):
        if not self.active:
            return None, {}

        ret, frame = self.cap.read()
        if not ret:
            return None, {}

        frame = cv2.flip(frame, 1) # Mirror for AR feel
        
        # Run YOLOv8 tracking
        # persist=True keeps tracking IDs across frames. 
        # classes=[0] filters for 'person' class only.
        results = self.model.track(frame, persist=True, classes=[0], verbose=False)
        
        player_keypoints = {} # Dict of player_id -> list of (x, y) keypoints
        
        if len(results) > 0 and results[0].boxes is not None and results[0].boxes.id is not None:
            track_ids = results[0].boxes.id.int().cpu().tolist()
            boxes = results[0].boxes.xywh.cpu().numpy() # (N, 4) - x_center, y_center, w, h
            
            x_centers = [box[0] for box in boxes]
            
            # Ensure mapping is updated
            self.assign_players(track_ids, x_centers)
            
            # Extract keypoints if available
            if hasattr(results[0], 'keypoints') and results[0].keypoints is not None:
                keypoints = results[0].keypoints.xy.cpu().numpy() # (N, 17, 2)
                
                for i, tid in enumerate(track_ids):
                    if tid in self.track_to_player:
                        pid = self.track_to_player[tid]
                        # Collect valid keypoints (>0)
                        valid_kps = [ (int(kp[0]), int(kp[1])) for kp in keypoints[i] if kp[0] > 0 and kp[1] > 0 ]
                        
                        # Also add a general body bounding box center for easier catching if needed
                        center_x = int(boxes[i][0])
                        center_y = int(boxes[i][1])
                        w = int(boxes[i][2])
                        h = int(boxes[i][3])
                        
                        # Store both keypoints and bounding box for collision detection
                        player_keypoints[pid] = {
                            "keypoints": valid_kps,
                            "bbox": (center_x - w//2, center_y - h//2, w, h)
                        }
        
        # OpenCV uses BGR, Pygame uses RGB. Convert here for performance.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return rgb_frame, player_keypoints

    def release(self):
        self.cap.release()
