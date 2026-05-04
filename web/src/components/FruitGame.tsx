'use client';

import React, { useEffect, useRef, useState } from 'react';
import styles from './FruitGame.module.css';
import Script from 'next/script';
import * as THREE from 'three';
import { FBXLoader } from 'three-stdlib';
import { OBJLoader } from 'three-stdlib';

interface Fruit3D {
  mesh: THREE.Group | THREE.Mesh;
  speedY: number;
  speedX: number;
  active: boolean;
  isBomb: boolean;
}

interface Particle3D {
  mesh: THREE.Mesh;
  velocity: THREE.Vector3;
  life: number;
}

const GAME_WIDTH = 1280;
const GAME_HEIGHT = 720;
const GAME_DURATION = 60;

export default function FruitGame() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [gameState, setGameState] = useState<'loading' | 'menu' | 'playing' | 'gameover'>('loading');
  const [score, setScore] = useState(0);
  const [timeLeft, setTimeLeft] = useState(GAME_DURATION);
  
  // Three.js Refs
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const fruitsRef = useRef<Fruit3D[]>([]);
  const particlesRef = useRef<Particle3D[]>([]);
  const swordsRef = useRef<{ 
    left: THREE.Group | null, 
    right: THREE.Group | null,
  }>({ 
    left: null, 
    right: null, 
  });
  const appleModelRef = useRef<THREE.Group | null>(null);
  
  const scoreRef = useRef(0);
  const timeLeftRef = useRef(GAME_DURATION);
  const detectorRef = useRef<any>(null);
  const animationFrameRef = useRef<number | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);

  // Sound Synthesis
  const playSlashSound = () => {
    try {
      if (!audioCtxRef.current) audioCtxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      const ctx = audioCtxRef.current;
      if (ctx.state === 'suspended') ctx.resume();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(800, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(100, ctx.currentTime + 0.1);
      gain.gain.setValueAtTime(0.05, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.1);
    } catch (e) {}
  };

  const playImpactSound = () => {
    try {
      if (!audioCtxRef.current) audioCtxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      const ctx = audioCtxRef.current;
      if (ctx.state === 'suspended') ctx.resume();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(150, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(40, ctx.currentTime + 0.2);
      gain.gain.setValueAtTime(0.2, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.2);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.2);
    } catch (e) {}
  };

  // Initialize Three.js
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, GAME_WIDTH / GAME_HEIGHT, 1, 5000);
    camera.position.set(0, 0, 1000);
    camera.lookAt(0, 0, 0);
    
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(GAME_WIDTH, GAME_HEIGHT);
    renderer.setPixelRatio(window.devicePixelRatio);
    
    if (containerRef.current) {
      containerRef.current.appendChild(renderer.domElement);
    }

    const ambientLight = new THREE.AmbientLight(0xffffff, 1.0);
    scene.add(ambientLight);
    const dirLight = new THREE.DirectionalLight(0xffffff, 1.5);
    dirLight.position.set(200, 500, 500);
    scene.add(dirLight);

    sceneRef.current = scene;
    cameraRef.current = camera;
    rendererRef.current = renderer;

    const fbxLoader = new FBXLoader();
    const objLoader = new OBJLoader();

    fbxLoader.load('/model/55-sting-sword-lowpoly.fbx/Sting-Sword lowpoly.fbx', (object) => {
      const scale = 5.0; 
      object.scale.set(scale, scale, scale);
      object.rotation.x = -Math.PI / 2;
      
      const createSwordGroup = () => {
        const group = new THREE.Group();
        const meshClone = object.clone();
        
        // Pivot adjustment: Move hilt so it's at the VERY origin of the group
        // If the hilt was inside the arm, we need to push the mesh UP (Y+) 
        // relative to the group origin which will be at the wrist.
        meshClone.position.set(0, -50, 0); 
        
        group.add(meshClone);
        return group;
      };
      
      const leftSword = createSwordGroup();
      const rightSword = createSwordGroup();
      
      scene.add(leftSword);
      scene.add(rightSword);
      
      swordsRef.current.left = leftSword;
      swordsRef.current.right = rightSword;
      
      leftSword.visible = false;
      rightSword.visible = false;
    });

    objLoader.load('/model/5kmoldfbow00-apple/apple.obj', (object) => {
      // Much smaller apples
      object.scale.set(12, 12, 12);
      object.traverse((child) => {
        if ((child as THREE.Mesh).isMesh) {
          (child as THREE.Mesh).material = new THREE.MeshStandardMaterial({ 
            color: 0xff0000, 
            roughness: 0.2, 
            metalness: 0.3 
          });
        }
      });
      appleModelRef.current = object;
    });

    return () => {
      renderer.dispose();
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
    };
  }, []);

  // AI Script Initialization
  useEffect(() => {
    const checkScripts = setInterval(() => {
      // @ts-ignore
      const tf = window.tf;
      // @ts-ignore
      const poseDetection = window.poseDetection;
      if (tf && poseDetection) {
        clearInterval(checkScripts);
        initModel(tf, poseDetection);
      }
    }, 1000);

    const initModel = async (tf: any, poseDetection: any) => {
      try {
        await tf.setBackend('webgl');
        await tf.ready();
        const detector = await poseDetection.createDetector(
          poseDetection.SupportedModels.BlazePose,
          { 
            runtime: 'mediapipe', 
            modelType: 'full',
            solutionPath: 'https://cdn.jsdelivr.net/npm/@mediapipe/pose'
          }
        );
        detectorRef.current = detector;
        setGameState('menu');
      } catch (err) {}
    };
    return () => clearInterval(checkScripts);
  }, []);

  // Camera Setup
  useEffect(() => {
    if (gameState === 'loading') return;
    const video = videoRef.current;
    if (!video) return;
    const startCamera = async () => {
      try {
        if (!video.srcObject) {
          const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: GAME_WIDTH, height: GAME_HEIGHT },
            audio: false,
          });
          video.srcObject = stream;
          video.onloadedmetadata = () => video.play();
        }
      } catch (err) {}
    };
    startCamera();
  }, [gameState]);

  // Game Loop
  useEffect(() => {
    if (gameState !== 'playing') return;

    const scene = sceneRef.current;
    const camera = cameraRef.current;
    const renderer = rendererRef.current;
    const video = videoRef.current;
    if (!scene || !camera || !renderer || !video) return;

    let lastTime = performance.now();
    let spawnTimer = 0;

    const screenToWorld = (x: number, y: number) => {
      const nx = ( (GAME_WIDTH - x) / GAME_WIDTH ) * 2 - 1;
      const ny = -( (y / GAME_HEIGHT) * 2 - 1 );
      const visibleHeight = 2 * Math.tan((camera.fov * Math.PI) / 360) * 1000;
      const visibleWidth = visibleHeight * (GAME_WIDTH / GAME_HEIGHT);
      return {
        x: nx * (visibleWidth / 2),
        y: ny * (visibleHeight / 2)
      };
    };

    const createParticles = (x: number, y: number) => {
      const particleGeo = new THREE.BoxGeometry(6, 6, 6);
      const particleMat = new THREE.MeshStandardMaterial({ color: 0xff0000 });
      for (let i = 0; i < 10; i++) {
        const p = new THREE.Mesh(particleGeo, particleMat);
        p.position.set(x, y, 0);
        scene.add(p);
        particlesRef.current.push({
          mesh: p,
          velocity: new THREE.Vector3((Math.random()-0.5)*25, (Math.random()-0.5)*25, (Math.random()-0.5)*15),
          life: 1.0
        });
      }
    };

    const gameLoop = async (timestamp: number) => {
      const deltaTime = timestamp - lastTime;
      lastTime = timestamp;

      timeLeftRef.current -= deltaTime / 1000;
      if (timeLeftRef.current <= 0) {
        setGameState('gameover');
        return;
      }
      setTimeLeft(Math.floor(timeLeftRef.current));

      // Faster spawn rate: 600ms
      spawnTimer += deltaTime;
      if (spawnTimer > 600) {
        if (appleModelRef.current) {
          const fruitMesh = appleModelRef.current.clone();
          const worldBounds = screenToWorld(0, 0);
          const startX = (Math.random() - 0.5) * (Math.abs(worldBounds.x) * 1.8);
          fruitMesh.position.set(startX, -500, 0);
          scene.add(fruitMesh);
          fruitsRef.current.push({
            mesh: fruitMesh,
            // Much higher velocity: 22-30
            speedY: 22 + Math.random() * 8,
            speedX: (Math.random() - 0.5) * 8,
            active: true,
            isBomb: false
          });
        }
        spawnTimer = 0;
      }

      // Detection
      let poses = [];
      if (detectorRef.current && video.readyState >= 2) {
        try {
          poses = await detectorRef.current.estimatePoses(video, { flipHorizontal: false });
        } catch (e) {}
      }

      // Update Swords
      if (poses.length > 0) {
        const kps = poses[0].keypoints;
        const joints = [
          { wrist: kps[15], elbow: kps[13], sword: swordsRef.current.left },
          { wrist: kps[16], elbow: kps[14], sword: swordsRef.current.right }
        ];

        joints.forEach(j => {
          if (j.wrist && j.wrist.score > 0.4 && j.sword) {
            const wristPos = screenToWorld(j.wrist.x, j.wrist.y);
            
            // Smoother and faster following
            j.sword.position.x += (wristPos.x - j.sword.position.x) * 0.8;
            j.sword.position.y += (wristPos.y - j.sword.position.y) * 0.8;
            j.sword.position.z = 20; // Slightly in front
            j.sword.visible = true;

            if (j.elbow && j.elbow.score > 0.3) {
              const dx = j.wrist.x - j.elbow.x;
              const dy = j.wrist.y - j.elbow.y;
              const angle = Math.atan2(-dy, -dx); 
              j.sword.rotation.z = angle + Math.PI / 2;
            }
          } else if (j.sword) {
            j.sword.visible = false;
          }
        });
      }

      // Physics
      fruitsRef.current.forEach((fruit) => {
        fruit.mesh.position.y += fruit.speedY;
        fruit.mesh.position.x += fruit.speedX;
        fruit.speedY -= 0.45; // Slightly stronger gravity for the fast fruit
        fruit.mesh.rotation.y += 0.07;
        fruit.mesh.rotation.x += 0.03;

        if (fruit.mesh.position.y < -600 && fruit.speedY < 0) {
          fruit.active = false;
          scene.remove(fruit.mesh);
        }

        // Collision Check
        [swordsRef.current.left, swordsRef.current.right].forEach(sword => {
          if (sword && sword.visible && fruit.active) {
            const dist = sword.position.distanceTo(fruit.mesh.position);
            // Smaller collision radius for smaller apples
            if (dist < 120) { 
              fruit.active = false;
              scene.remove(fruit.mesh);
              scoreRef.current += 1;
              setScore(scoreRef.current);
              createParticles(fruit.mesh.position.x, fruit.mesh.position.y);
              playImpactSound();
              playSlashSound();
            }
          }
        });
      });

      particlesRef.current.forEach(p => {
        p.mesh.position.add(p.velocity);
        p.velocity.y -= 0.6;
        p.life -= 0.03;
        p.mesh.scale.setScalar(p.life);
        if (p.life <= 0) scene.remove(p.mesh);
      });

      fruitsRef.current = fruitsRef.current.filter(f => f.active);
      particlesRef.current = particlesRef.current.filter(p => p.life > 0);

      renderer.render(scene, camera);
      animationFrameRef.current = requestAnimationFrame(gameLoop);
    };

    animationFrameRef.current = requestAnimationFrame(gameLoop);
    return () => { if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current); };
  }, [gameState]);

  const startGame = () => {
    scoreRef.current = 0;
    setScore(0);
    timeLeftRef.current = GAME_DURATION;
    setTimeLeft(GAME_DURATION);
    fruitsRef.current.forEach(f => sceneRef.current?.remove(f.mesh));
    fruitsRef.current = [];
    setGameState('playing');
  };

  return (
    <div className={styles.container}>
      <Script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-core" strategy="afterInteractive" />
      <Script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-converter" strategy="afterInteractive" />
      <Script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl" strategy="afterInteractive" />
      <Script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection" strategy="afterInteractive" />
      <Script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose" strategy="afterInteractive" />

      <div className={styles.gameWrapper}>
        <video ref={videoRef} className={styles.video} autoPlay playsInline muted />
        <div ref={containerRef} className={styles.canvas} style={{ width: GAME_WIDTH, height: GAME_HEIGHT }} />
        
        {gameState === 'loading' && (
          <div className={styles.loading}>
            <div className={styles.spinner} />
            <p>Readying Sting Sword 3D...</p>
          </div>
        )}

        {(gameState === 'menu' || gameState === 'gameover') && (
          <div className={styles.menuOverlay}>
            <h1 className={styles.title}>{gameState === 'menu' ? 'Sting Sword AR' : 'Great Slashing!'}</h1>
            {gameState === 'gameover' && <p className={styles.finalScore}>Final Score: {score}</p>}
            <button className={styles.startButton} onClick={startGame}>
              {gameState === 'menu' ? 'Enter Arena' : 'Slash Again'}
            </button>
          </div>
        )}

        {gameState === 'playing' && (
          <div className={styles.uiOverlay}>
            <div className={styles.stats}>
              <p className={styles.score}>{score}</p>
              <p className={styles.timer}>{timeLeft}s</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
