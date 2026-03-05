// ── Three.js 場景 + Orb（異常物件） ──
/* global gsap */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { getAccentHex } from '../config/theme.js';

let scene, camera, renderer, controls;
let anomalyObject;
let distortionAmount = 1.0;
let resolution = 32;
let clock = new THREE.Clock();
let isDraggingAnomaly = false;
let anomalyVelocity = new THREE.Vector2(0, 0);
let anomalyTargetPosition = new THREE.Vector3(0, 0, 0);
let anomalyOriginalPosition = new THREE.Vector3(0, 0, 0);
let defaultCameraPosition = new THREE.Vector3(0, window.innerWidth <= 768 ? 1.2 : 0, window.innerWidth <= 768 ? 14 : 10);
let zoomedCameraPosition = new THREE.Vector3(0, 0, 7);
let updateGlow = null;

// 主題顏色（動態從 CSS 變數取得）
let themeColors = {
  primary: 0xff4e42,
  secondary: 0xc2362f,
  tertiary: 0xffb3ab
};

function updateThemeColors() {
  const style = getComputedStyle(document.documentElement);
  const primary = style.getPropertyValue('--accent-primary').trim();
  const secondary = style.getPropertyValue('--accent-secondary').trim();
  const tertiary = style.getPropertyValue('--accent-tertiary').trim();
  
  // 將 HSL 轉為 hex 供 Three.js 使用
  themeColors.primary = new THREE.Color(primary).getHex();
  themeColors.secondary = new THREE.Color(secondary).getHex();
  themeColors.tertiary = new THREE.Color(tertiary).getHex();
}

// Agent 狀態驅動 Orb 視覺
let agentActivity = 0;
let agentActivitySmooth = 0;  // 平滑過渡
let agentStateStartTime = 0;  // 狀態開始時間
let streamIntensity = 0;      // 串流速度強度
let streamIntensitySmooth = 0;
let doneBloom = 0;            // 完成綻放效果

export function setAgentState(state) {
  const prev = agentActivity;
  if (state === 'thinking') agentActivity = 1;
  else if (state === 'responding') agentActivity = 2;
  else {
    // 回到 idle 時觸發綻放
    if (prev === 2) doneBloom = 1.0;
    agentActivity = 0;
  }
  if (agentActivity !== prev) agentStateStartTime = performance.now();
}

// 串流速度更新（由 chat.js 呼叫）
export function setStreamIntensity(val) {
  streamIntensity = val;
}

// 監聽 chat.js 的狀態事件（避免循環依賴）
window.addEventListener('agent-state', (e) => setAgentState(e.detail));
window.addEventListener('agent-stream', (e) => setStreamIntensity(e.detail || 0));
let updateParticles = null;

export function getScene() { return scene; }
export function getCamera() { return camera; }
export function getControls() { return controls; }
export function getAnomalyObject() { return anomalyObject; }
export function getClock() { return clock; }

// 取得 Orb 在螢幕上的 2D 投影座標
export function getOrbScreenPosition() {
  if (!anomalyObject || !camera) return { x: window.innerWidth / 2, y: window.innerHeight / 2 };
  const pos = anomalyObject.position.clone();
  pos.project(camera);
  return {
    x: (pos.x * 0.5 + 0.5) * window.innerWidth,
    y: (-pos.y * 0.5 + 0.5) * window.innerHeight,
  };
}

export function setDistortion(val) {
  distortionAmount = val;
  updateGlow = createAnomalyObject();
}

export function setResolution(val) {
  resolution = val;
  updateGlow = createAnomalyObject();
}

export function zoomCameraForAudio(zoomIn) {
  const targetPosition = zoomIn ? zoomedCameraPosition : defaultCameraPosition;
  gsap.to(camera.position, {
    x: targetPosition.x,
    y: targetPosition.y,
    z: targetPosition.z,
    duration: 1.5,
    ease: 'power2.inOut',
    onUpdate: () => camera.lookAt(0, 0, 0),
  });
}

function createBackgroundParticles() {
  const particlesGeometry = new THREE.BufferGeometry();
  const particleCount = window.innerWidth <= 768 ? 1000 : 3000;
  const positions = new Float32Array(particleCount * 3);
  const colors = new Float32Array(particleCount * 3);
  const sizes = new Float32Array(particleCount);
  const color1 = new THREE.Color(themeColors.primary);
  const color2 = new THREE.Color(themeColors.secondary);
  const color3 = new THREE.Color(themeColors.tertiary);

  for (let i = 0; i < particleCount; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 100;
    positions[i * 3 + 1] = (Math.random() - 0.5) * 100;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 100;
    let color;
    const colorChoice = Math.random();
    if (colorChoice < 0.33) color = color1;
    else if (colorChoice < 0.66) color = color2;
    else color = color3;
    colors[i * 3] = color.r;
    colors[i * 3 + 1] = color.g;
    colors[i * 3 + 2] = color.b;
    sizes[i] = 0.05;
  }

  particlesGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  particlesGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  particlesGeometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

  const particlesMaterial = new THREE.ShaderMaterial({
    uniforms: { time: { value: 0 } },
    vertexShader: `
      attribute float size;
      varying vec3 vColor;
      uniform float time;
      void main() {
        vColor = color;
        vec3 pos = position;
        pos.x += sin(time * 0.1 + position.z * 0.2) * 0.05;
        pos.y += cos(time * 0.1 + position.x * 0.2) * 0.05;
        pos.z += sin(time * 0.1 + position.y * 0.2) * 0.05;
        vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
        gl_PointSize = size * (300.0 / -mvPosition.z);
        gl_Position = projectionMatrix * mvPosition;
      }
    `,
    fragmentShader: `
      varying vec3 vColor;
      void main() {
        float r = distance(gl_PointCoord, vec2(0.5, 0.5));
        if (r > 0.5) discard;
        float glow = 1.0 - (r * 2.0);
        glow = pow(glow, 2.0);
        gl_FragColor = vec4(vColor, glow);
      }
    `,
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    vertexColors: true,
  });

  const particles = new THREE.Points(particlesGeometry, particlesMaterial);
  scene.add(particles);
  return function update(time) {
    particlesMaterial.uniforms.time.value = time;
  };
}

function createAnomalyObject() {
  if (anomalyObject) scene.remove(anomalyObject);
  anomalyObject = new THREE.Group();
  const radius = 2;

  const outerGeometry = new THREE.IcosahedronGeometry(radius, Math.max(1, Math.floor(resolution / 8)));
  const outerMaterial = new THREE.ShaderMaterial({
    uniforms: {
      time: { value: 0 },
      color: { value: new THREE.Color(themeColors.primary) },
      audioLevel: { value: 0 },
      distortion: { value: distortionAmount },
      agentActivity: { value: 0 },
    },
    vertexShader: `
      uniform float time;
      uniform float audioLevel;
      uniform float distortion;
      uniform float agentActivity;
      varying vec3 vNormal;
      varying vec3 vPosition;
      
      vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
      vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
      vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
      vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }
      
      float snoise(vec3 v) {
        const vec2 C = vec2(1.0/6.0, 1.0/3.0);
        const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
        vec3 i  = floor(v + dot(v, C.yyy));
        vec3 x0 = v - i + dot(i, C.xxx);
        vec3 g = step(x0.yzx, x0.xyz);
        vec3 l = 1.0 - g;
        vec3 i1 = min(g.xyz, l.zxy);
        vec3 i2 = max(g.xyz, l.zxy);
        vec3 x1 = x0 - i1 + C.xxx;
        vec3 x2 = x0 - i2 + C.yyy;
        vec3 x3 = x0 - D.yyy;
        i = mod289(i);
        vec4 p = permute(permute(permute(
                i.z + vec4(0.0, i1.z, i2.z, 1.0))
              + i.y + vec4(0.0, i1.y, i2.y, 1.0))
              + i.x + vec4(0.0, i1.x, i2.x, 1.0));
        float n_ = 0.142857142857;
        vec3 ns = n_ * D.wyz - D.xzx;
        vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
        vec4 x_ = floor(j * ns.z);
        vec4 y_ = floor(j - 7.0 * x_);
        vec4 x = x_ *ns.x + ns.yyyy;
        vec4 y = y_ *ns.x + ns.yyyy;
        vec4 h = 1.0 - abs(x) - abs(y);
        vec4 b0 = vec4(x.xy, y.xy);
        vec4 b1 = vec4(x.zw, y.zw);
        vec4 s0 = floor(b0)*2.0 + 1.0;
        vec4 s1 = floor(b1)*2.0 + 1.0;
        vec4 sh = -step(h, vec4(0.0));
        vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy;
        vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww;
        vec3 p0 = vec3(a0.xy, h.x);
        vec3 p1 = vec3(a0.zw, h.y);
        vec3 p2 = vec3(a1.xy, h.z);
        vec3 p3 = vec3(a1.zw, h.w);
        vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3)));
        p0 *= norm.x; p1 *= norm.y; p2 *= norm.z; p3 *= norm.w;
        vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
        m = m * m;
        return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
      }
      
      void main() {
        vNormal = normalize(normalMatrix * normal);
        float slowTime = time * 0.3;
        vec3 pos = position;
        float noise = snoise(vec3(position.x * 0.5, position.y * 0.5, position.z * 0.5 + slowTime));
        pos += normal * noise * 0.2 * distortion * (1.0 + audioLevel);
        vPosition = pos;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
      }
    `,
    fragmentShader: `
      uniform float time;
      uniform vec3 color;
      uniform float audioLevel;
      uniform float agentActivity;
      varying vec3 vNormal;
      varying vec3 vPosition;
      void main() {
        vec3 viewDirection = normalize(cameraPosition - vPosition);
        float fresnel = 1.0 - max(0.0, dot(viewDirection, vNormal));
        fresnel = pow(fresnel, 2.0 + audioLevel * 2.0);
        // thinking: 脈動加速, responding: 更亮
        float pulse = 0.8 + 0.2 * sin(time * 2.0);
        vec3 finalColor = color * fresnel * pulse * (1.0 + audioLevel * 0.8);
        float alpha = fresnel * (0.7 - audioLevel * 0.3);
        gl_FragColor = vec4(finalColor, alpha);
      }
    `,
    wireframe: true,
    transparent: true,
  });

  const outerSphere = new THREE.Mesh(outerGeometry, outerMaterial);
  anomalyObject.add(outerSphere);
  scene.add(anomalyObject);

  // Glow sphere
  const glowGeometry = new THREE.SphereGeometry(radius * 1.2, 32, 32);
  const glowMaterial = new THREE.ShaderMaterial({
    uniforms: {
      time: { value: 0 },
      color: { value: new THREE.Color(themeColors.primary) },
      audioLevel: { value: 0 },
      agentActivity: { value: 0 },
    },
    vertexShader: `
      varying vec3 vNormal;
      varying vec3 vPosition;
      uniform float audioLevel;
      uniform float agentActivity;
      void main() {
        vNormal = normalize(normalMatrix * normal);
        vPosition = position * (1.0 + audioLevel * 0.2);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(vPosition, 1.0);
      }
    `,
    fragmentShader: `
      varying vec3 vNormal;
      varying vec3 vPosition;
      uniform vec3 color;
      uniform float time;
      uniform float audioLevel;
      uniform float agentActivity;
      void main() {
        vec3 viewDirection = normalize(cameraPosition - vPosition);
        float fresnel = 1.0 - max(0.0, dot(viewDirection, vNormal));
        fresnel = pow(fresnel, 3.0 + audioLevel * 3.0);
        float pulse = 0.5 + 0.5 * sin(time * 2.0);
        float audioFactor = 1.0 + audioLevel * 3.0;
        vec3 finalColor = color * fresnel * (0.8 + 0.2 * pulse) * audioFactor;
        float alpha = fresnel * (0.3 * audioFactor) * (1.0 - audioLevel * 0.2);
        gl_FragColor = vec4(finalColor, alpha);
      }
    `,
    transparent: true,
    side: THREE.BackSide,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });

  const glowSphere = new THREE.Mesh(glowGeometry, glowMaterial);
  anomalyObject.add(glowSphere);

  return function updateAnomaly(time, audioLevel) {
    // 計算動態 agent 強度
    const elapsed = (performance.now() - agentStateStartTime) / 1000;
    let targetActivity = 0;

    if (agentActivity === 0) {
      // Idle: 跟原版一樣靜止（agentActivity = 0）
      targetActivity = 0;
    } else if (agentActivity === 1) {
      // Thinking: 漸強 + 不規則抖動（像腦袋高速運轉）
      const ramp = 0.5 + Math.min(elapsed / 10, 1) * 1.5;
      // 多層 sin 疊加 = 不規則猶豫感
      const jitter = Math.sin(elapsed * 2.3) * 0.12
                    + Math.sin(elapsed * 5.7) * 0.08
                    + Math.sin(elapsed * 11.3) * 0.04;
      targetActivity = ramp + jitter;
    } else if (agentActivity === 2) {
      // Responding: 串流速度驅動 + 呼吸底線
      streamIntensitySmooth += (streamIntensity - streamIntensitySmooth) * 0.1;
      targetActivity = 0.8 + streamIntensitySmooth * 1.5
                     + Math.sin(time * 1.2) * 0.1;
    }

    // 完成綻放：短暫爆亮後衰減
    if (doneBloom > 0.01) {
      targetActivity += doneBloom * 2.5;
      doneBloom *= 0.95;  // 指數衰減（~60 幀消失）
    } else {
      doneBloom = 0;
    }

    // 平滑過渡（idle 回復慢一點更自然）
    const smoothSpeed = agentActivity === 0 ? 0.02 : 0.06;
    agentActivitySmooth += (targetActivity - agentActivitySmooth) * smoothSpeed;

    outerMaterial.uniforms.time.value = time;
    outerMaterial.uniforms.audioLevel.value = audioLevel;
    outerMaterial.uniforms.distortion.value = distortionAmount;
    outerMaterial.uniforms.agentActivity.value = agentActivitySmooth;
    glowMaterial.uniforms.time.value = time;
    glowMaterial.uniforms.audioLevel.value = audioLevel;
    glowMaterial.uniforms.agentActivity.value = agentActivitySmooth;
  };
}

function setupAnomalyDragging() {
  const container = document.getElementById('three-container');
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  let isDragging = false;
  let dragStartPosition = new THREE.Vector2();
  anomalyOriginalPosition = new THREE.Vector3(0, 0, 0);
  anomalyTargetPosition = new THREE.Vector3(0, 0, 0);
  const maxDragDistance = 3;

  // 共用：取得 normalized 座標
  function getPointerCoords(event) {
    const x = event.touches ? event.touches[0].clientX : event.clientX;
    const y = event.touches ? event.touches[0].clientY : event.clientY;
    return {
      x: (x / window.innerWidth) * 2 - 1,
      y: -(y / window.innerHeight) * 2 + 1,
    };
  }

  function onPointerDown(event) {
    const coords = getPointerCoords(event);
    mouse.x = coords.x;
    mouse.y = coords.y;
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObject(anomalyObject, true);
    if (intersects.length > 0) {
      controls.enabled = false;
      isDragging = true;
      isDraggingAnomaly = true;
      dragStartPosition.x = mouse.x;
      dragStartPosition.y = mouse.y;
      if (event.cancelable) event.preventDefault();
    }
  }

  function onPointerMove(event) {
    if (!isDragging) return;
    if (event.cancelable) event.preventDefault();
    const coords = getPointerCoords(event);
    mouse.x = coords.x;
    mouse.y = coords.y;
    const deltaX = (mouse.x - dragStartPosition.x) * 5;
    const deltaY = (mouse.y - dragStartPosition.y) * 5;
    anomalyTargetPosition.x += deltaX;
    anomalyTargetPosition.y += deltaY;
    const distance = Math.sqrt(anomalyTargetPosition.x ** 2 + anomalyTargetPosition.y ** 2);
    if (distance > maxDragDistance) {
      const scale = maxDragDistance / distance;
      anomalyTargetPosition.x *= scale;
      anomalyTargetPosition.y *= scale;
    }
    anomalyVelocity.x = deltaX * 2;
    anomalyVelocity.y = deltaY * 2;
    dragStartPosition.x = mouse.x;
    dragStartPosition.y = mouse.y;
  }

  function onPointerUp() {
    if (isDragging) {
      controls.enabled = true;
      isDragging = false;
      isDraggingAnomaly = false;
    }
  }

  // Mouse events
  container.addEventListener('mousedown', onPointerDown);
  container.addEventListener('mousemove', onPointerMove);
  container.addEventListener('mouseup', onPointerUp);
  container.addEventListener('mouseleave', onPointerUp);

  // Touch events
  container.addEventListener('touchstart', onPointerDown, { passive: false });
  container.addEventListener('touchmove', onPointerMove, { passive: false });
  container.addEventListener('touchend', onPointerUp);
  container.addEventListener('touchcancel', onPointerUp);
}

function updateAnomalyPosition() {
  if (!isDraggingAnomaly) {
    anomalyVelocity.x *= 0.95;
    anomalyVelocity.y *= 0.95;
    anomalyTargetPosition.x += anomalyVelocity.x * 0.1;
    anomalyTargetPosition.y += anomalyVelocity.y * 0.1;
    const springStrength = 0.1;
    anomalyVelocity.x -= anomalyTargetPosition.x * springStrength;
    anomalyVelocity.y -= anomalyTargetPosition.y * springStrength;
    if (Math.abs(anomalyTargetPosition.x) < 0.05 && Math.abs(anomalyTargetPosition.y) < 0.05) {
      anomalyTargetPosition.set(0, 0, 0);
      anomalyVelocity.set(0, 0);
    }
    const bounceThreshold = 3;
    const bounceDamping = 0.8;
    if (Math.abs(anomalyTargetPosition.x) > bounceThreshold) {
      anomalyVelocity.x = -anomalyVelocity.x * bounceDamping;
      anomalyTargetPosition.x = Math.sign(anomalyTargetPosition.x) * bounceThreshold;
      if (Math.abs(anomalyVelocity.x) > 0.1) {
      }
    }
    if (Math.abs(anomalyTargetPosition.y) > bounceThreshold) {
      anomalyVelocity.y = -anomalyVelocity.y * bounceDamping;
      anomalyTargetPosition.y = Math.sign(anomalyTargetPosition.y) * bounceThreshold;
      if (Math.abs(anomalyVelocity.y) > 0.1) {
      }
    }
  }
  anomalyObject.position.x += (anomalyTargetPosition.x - anomalyObject.position.x) * 0.2;
  anomalyObject.position.y += (anomalyTargetPosition.y - anomalyObject.position.y) * 0.2;
  if (!isDraggingAnomaly) {
    anomalyObject.rotation.x += anomalyVelocity.y * 0.01;
    anomalyObject.rotation.y += anomalyVelocity.x * 0.01;
  }
}

export function resetAnomaly() {
  distortionAmount = 1.0;
  resolution = 32;
  updateGlow = createAnomalyObject();
  anomalyTargetPosition.set(0, 0, 0);
  anomalyVelocity.set(0, 0);
  anomalyObject.position.set(0, 0, 0);
}

// 動畫循環（由 main.js 傳入 audioLevel）
export function animateScene(audioLevel, rotationSpeed, audioReactivity) {
  controls.update();
  const time = clock.getElapsedTime();
  updateAnomalyPosition();
  if (updateGlow) updateGlow(time, audioLevel);
  if (updateParticles) updateParticles(time);
  if (anomalyObject) {
    const audioRotationFactor = 1 + audioLevel * audioReactivity;
    anomalyObject.rotation.y += 0.005 * rotationSpeed * audioRotationFactor;
    anomalyObject.rotation.z += 0.002 * rotationSpeed * audioRotationFactor;
  }
  renderer.render(scene, camera);
}

export function onWindowResize(resizeCanvasCallback) {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);

  // 手機 ↔ 桌面切換時更新 camera 距離
  const isMobile = window.innerWidth <= 768;
  const newZ = isMobile ? 14 : 10;
  const newY = isMobile ? 1.2 : 0;
  defaultCameraPosition.z = newZ;
  defaultCameraPosition.y = newY;
  if (!isDraggingAnomaly) {
    camera.position.z = newZ;
    camera.position.y = newY;
  }

  if (resizeCanvasCallback) resizeCanvasCallback();
}

export function initScene() {
  scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x0a0e17, 0.05);
  camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.copy(defaultCameraPosition);

  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    powerPreference: 'high-performance',
    stencil: false,
    depth: true,
  });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setClearColor(0x000000, 0);
  renderer.setPixelRatio(window.devicePixelRatio);
  document.getElementById('three-container').appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.1;
  controls.enableRotate = false;
  controls.enablePan = false;
  controls.zoomSpeed = 0.7;
  controls.minDistance = 3;
  controls.maxDistance = 30;
  controls.enableZoom = false;

  const ambientLight = new THREE.AmbientLight(0x404040, 1.5);
  scene.add(ambientLight);
  const directionalLight = new THREE.DirectionalLight(0xffffff, 1.5);
  directionalLight.position.set(1, 1, 1);
  scene.add(directionalLight);
  const pointLight1 = new THREE.PointLight(themeColors.primary, 1, 10);
  pointLight1.position.set(2, 2, 2);
  scene.add(pointLight1);
  const pointLight2 = new THREE.PointLight(themeColors.secondary, 1, 10);
  pointLight2.position.set(-2, -2, -2);
  scene.add(pointLight2);

  updateGlow = createAnomalyObject();
  updateParticles = createBackgroundParticles();
  setupAnomalyDragging();
  
  // 初始化主題顏色
  updateThemeColors();
  
  // 監聽主題變更
  window.addEventListener('theme-change', () => {
    updateThemeColors();
    // 重新建立物件以套用新顏色
    updateGlow = createAnomalyObject();
    updateParticles = createBackgroundParticles();
    // 更新 point lights
    const lights = scene.children.filter(child => child instanceof THREE.PointLight);
    if (lights[0]) lights[0].color.setHex(themeColors.primary);
    if (lights[1]) lights[1].color.setHex(themeColors.secondary);
  });
}
