# Fruit Picker Web AR

This is a Next.js version of the Fruit Picking AR game.

## Features
- **AI Pose Detection**: Uses TensorFlow.js MoveNet for real-time skeleton tracking.
- **Skeleton Visuals**: Draws body connections instead of bounding boxes for a cleaner look.
- **Modern UI**: Beautifully designed with CSS Modules, gradients, and animations.
- **Gameplay**: Catch falling fruits with your hands or head to score points.

## How to Run
1. Navigate to the `web` directory:
   ```bash
   cd web
   ```
2. Install dependencies (if you haven't):
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.
5. Allow camera access and start playing!

## Technical Details
- **Framework**: Next.js 15+ (App Router)
- **Styling**: Vanilla CSS (CSS Modules)
- **AI Engine**: TensorFlow.js (MoveNet) loaded via CDN for maximum compatibility.
