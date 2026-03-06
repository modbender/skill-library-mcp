# 📊 Embodied AI — Taxonomy & Glossary

A unified classification system and keyword dictionary for the Embodied AI news tracking system.
Ensures consistent categorization across `search_queries.md`, `output_templates.md`, and `workflow.md`.

---

## How to Use This File

| Who | How |
|-----|-----|
| **Search** (`search_queries.md`) | Use the keyword lists to build/refine queries; use aliases to avoid missing results |
| **Classification** (`workflow.md` Step 3) | Use the category tree to assign each story to the correct bucket |
| **Output** (`output_templates.md`) | Use the metadata fields per category to fill template fields consistently |
| **Monthly Maintenance** | Add new terms, retire obsolete ones, re-classify as the field evolves |

---

## 1. News Category Taxonomy

The primary classification system for all news stories. Every story must be assigned to **exactly one** primary category and may have **0–2** secondary tags.

```
📰 Embodied AI News
│
├── 🔥 Major Announcements          ← Cross-cutting; reserved for top-impact stories
│
├── 🧠 Foundation Models & Algorithms
│   ├── Vision-Language-Action (VLA) Models
│   ├── Diffusion / Flow-based Policies
│   ├── World Models
│   ├── Reinforcement Learning
│   ├── Imitation Learning & Teleoperation
│   ├── Sim-to-Real Transfer
│   ├── Language-Conditioned Robotics
│   ├── 3D / Spatial Understanding
│   ├── Generalist / Cross-Embodiment Policies
│   └── Multimodal Perception (Vision, Tactile, Audio)
│
├── 🦾 Hardware & Platforms
│   ├── Humanoid Robots (Full-body Bipedal)
│   ├── Quadruped / Legged Robots
│   ├── Mobile Manipulators
│   ├── Dexterous Hands & Grippers
│   ├── Actuators & Transmission
│   ├── Sensors (Tactile, Force-Torque, Vision)
│   ├── Compute & Edge AI Hardware
│   └── Supply Chain & Manufacturing
│
├── 🌐 Simulation & Infrastructure
│   ├── Simulation Platforms
│   ├── Digital Twins
│   ├── Benchmarks & Evaluation
│   ├── Datasets
│   ├── Robot OS & Middleware
│   └── Cloud Robotics & Fleet Management
│
├── 🏭 Deployments & Commercial
│   ├── Factory & Warehouse
│   ├── Household & Service
│   ├── Healthcare & Medical
│   ├── Agriculture & Field
│   ├── Construction & Inspection
│   ├── Retail & Hospitality
│   └── Performance Metrics & Benchmarks
│
├── 💰 Funding, M&A & Business
│   ├── Funding Rounds
│   ├── M&A & Partnerships
│   ├── IPO & Public Markets
│   ├── Market Sizing & Forecasts
│   └── Talent & Hiring
│
├── 🌍 Policy, Safety & Ethics
│   ├── Safety Standards
│   ├── Government Regulation
│   ├── Export Controls & Geopolitics
│   ├── Ethics & Labor Impact
│   └── Industry Consortia & Standards Bodies
│
└── 🇨🇳 China Ecosystem
    ├── Company News (Unitree, AGIBOT, UBTECH, Galbot, Fourier, etc.)
    ├── Policy & Subsidies
    ├── Supply Chain & Manufacturing
    ├── Academic & Research
    └── Market & Competition
```

### Category Assignment Rules

| Rule | Description |
|------|-------------|
| **Single Primary** | Every story gets exactly one primary category |
| **Major Announcements** | Only for stories that would be "above the fold" — new paradigm, >$500M funding, first-ever deployment milestone, etc. Also assign a secondary category |
| **China Ecosystem** | Use when the story's primary significance is about the Chinese market/ecosystem. If a Chinese company publishes a technical paper, primary = 🧠, secondary = 🇨🇳 |
| **Cross-cutting stories** | A story about "Unitree raises $500M to scale humanoid production" → Primary: 💰, Secondary: 🇨🇳, 🦾 |
| **When in doubt** | Ask: "What is the reader most interested in learning from this story?" — that determines the primary category |

---

## 2. Technology Taxonomy

### 2.1 Learning Paradigms

```
Learning Paradigms
│
├── Imitation Learning (IL)
│   ├── Behavioral Cloning (BC)
│   ├── Inverse Reinforcement Learning (IRL)
│   ├── DAgger / Interactive IL
│   └── One-Shot / Few-Shot IL
│
├── Reinforcement Learning (RL)
│   ├── Model-Free RL (PPO, SAC, TD3)
│   ├── Model-Based RL
│   ├── Offline RL / Batch RL
│   ├── Sim-to-Real RL
│   ├── Reward Shaping / Reward Learning
│   └── Curriculum Learning
│
├── Foundation Model Approaches
│   ├── Vision-Language-Action (VLA)
│   ├── Vision-Language Models for Planning (VLM)
│   ├── Large Language Model Planning (LLM-as-Planner)
│   ├── World Models / Video Prediction
│   ├── Diffusion Policy
│   ├── Flow Matching Policy
│   ├── Action Chunking (ACT)
│   ├── Generalist Policy / Cross-Embodiment
│   └── Large Behavior Models (LBM)
│
├── Sim-to-Real Transfer
│   ├── Domain Randomization
│   ├── Domain Adaptation
│   ├── System Identification
│   ├── Real-to-Sim-to-Real
│   └── Digital Twin Transfer
│
└── Data Collection & Curation
    ├── Teleoperation (VR, Exoskeleton, Puppet)
    ├── Human Video Demonstration
    ├── Synthetic Data Generation
    ├── Autonomous Data Collection (AutoRT-style)
    ├── Cross-Embodiment Datasets
    └── Data Scaling Laws
```

### 2.2 Model Architecture Taxonomy

```
Model Architectures
│
├── Vision-Language-Action (VLA)
│   ├── RT-2 / RT-2-X (Google DeepMind)
│   ├── Octo (Berkeley)
│   ├── OpenVLA (Stanford/Berkeley)
│   ├── π0 / π0-FAST (Physical Intelligence)
│   ├── GR00T (NVIDIA)
│   ├── RoboVLM
│   ├── SpatialVLA
│   └── [Emerging: company-specific VLAs]
│
├── Diffusion-Based Policies
│   ├── Diffusion Policy (Chi et al.)
│   ├── 3D Diffusion Policy (DP3)
│   ├── Consistency Policy
│   └── Flow Matching Policy
│
├── Action Chunking
│   ├── ACT (Action Chunking with Transformers)
│   └── ACT variants (BiACT, etc.)
│
├── World Models
│   ├── Video Prediction Models (UniSim, Cosmos, etc.)
│   ├── Latent World Models
│   ├── Physics-Informed World Models
│   └── Action-Conditioned Video Generation
│
├── LLM / VLM Planners
│   ├── SayCan / Inner Monologue
│   ├── Code-as-Policy
│   ├── VoxPoser
│   └── Task and Motion Planning (TAMP) + LLM
│
└── Classical / Hybrid
    ├── Model Predictive Control (MPC)
    ├── Whole-Body Control (WBC)
    ├── Trajectory Optimization
    └── Hybrid Learning + Control
```

### 2.3 Perception Stack

```
Perception
│
├── Visual Perception
│   ├── RGB Camera (Monocular, Stereo)
│   ├── Depth Sensors (Structured Light, ToF, LiDAR)
│   ├── Object Detection & Segmentation
│   ├── 6D Pose Estimation
│   ├── Open-Vocabulary Detection (OWL-ViT, Grounding DINO)
│   └── Visual Foundation Models (DINOv2, SAM, etc.)
│
├── 3D / Spatial Perception
│   ├── Point Cloud Processing
│   ├── NeRF / 3D Gaussian Splatting
│   ├── Occupancy Networks
│   ├── Scene Graphs
│   └── Spatial Reasoning
│
├── Tactile Perception
│   ├── Vision-Based Tactile (GelSight, DIGIT, Taxim)
│   ├── Capacitive / Resistive Arrays
│   ├── Tactile-Visual Fusion
│   └── Slip Detection
│
├── Proprioception
│   ├── Joint Encoders
│   ├── IMU / Inertial Measurement
│   ├── Force-Torque Sensors
│   └── Current-Based Torque Estimation
│
└── Multimodal Fusion
    ├── Vision-Language Grounding
    ├── Vision-Tactile Fusion
    ├── Audio-Visual Fusion
    └── Cross-Modal Representation
```

---

## 3. Hardware Taxonomy

### 3.1 Robot Form Factors

```
Robot Form Factors
│
├── Humanoid (Bipedal, Full-Body)
│   ├── Full-Size (>150cm): Atlas, Optimus, Figure 02, Walker S
│   ├── Mid-Size (100–150cm): GR-2, H1, NEO, Phoenix
│   ├── Compact (<100cm): G1, GR-1
│   └── Upper-Body Only (Torso + Arms): ALOHA, Mobile ALOHA
│
├── Quadruped / Legged
│   ├── Spot (Boston Dynamics)
│   ├── Go2 / B2 (Unitree)
│   ├── ANYmal (ANYbotics)
│   └── Custom Research Platforms
│
├── Mobile Manipulator
│   ├── Wheeled Base + Arm(s)
│   ├── Stretch (Hello Robot)
│   ├── TIAGo (PAL Robotics)
│   └── Custom Lab Platforms
│
├── Tabletop / Fixed-Base Arm
│   ├── Franka Emika (Panda)
│   ├── Universal Robots (UR series)
│   ├── xArm / Flexiv Rizon
│   ├── ALOHA (Bimanual)
│   └── Low-Cost Arms (Koch, SO-100, Gello, etc.)
│
└── Specialized
    ├── Surgical Robots
    ├── Agricultural Robots
    ├── Underwater Robots
    └── Aerial Manipulators
```

### 3.2 Key Components

```
Key Components
│
├── Actuators & Transmission
│   ├── Harmonic Drive / Strain Wave
│   ├── Planetary Gearbox
│   ├── Quasi-Direct-Drive (QDD)
│   ├── Linear Actuators
│   ├── Series Elastic Actuators (SEA)
│   ├── Hydraulic Actuators
│   ├── Tendon-Driven Mechanisms
│   ├── BLDC Motors
│   └── Frameless Motors
│
├── Dexterous Hands
│   ├── Anthropomorphic (5-finger)
│   │   ├── Shadow Hand
│   │   ├── Ability Hand (PSYONIC)
│   │   ├── Inspire Hand
│   │   ├── Leap Hand
│   │   └── Company-specific (Figure, Tesla, AGIBOT, etc.)
│   ├── Under-Actuated Grippers
│   ├── Soft Grippers
│   └── Parallel Jaw Grippers
│
├── Sensors
│   ├── Cameras (RGB, Depth, Event)
│   ├── LiDAR
│   ├── Tactile Sensors
│   ├── Force-Torque Sensors (F/T)
│   ├── IMU
│   ├── Joint Encoders (Absolute, Incremental)
│   └── Proximity Sensors
│
├── Compute Platforms
│   ├── NVIDIA Jetson (Orin, Thor)
│   ├── Qualcomm Robotics RB series
│   ├── Intel / AMD Embedded
│   ├── Custom ASICs
│   └── Cloud Offloading
│
└── Power Systems
    ├── Battery (LiFePO4, Li-ion)
    ├── Battery Management System (BMS)
    └── Power Distribution
```

---

## 4. Company & Organization Taxonomy

### 4.1 Humanoid Robot Companies

| Company | HQ | Latest Robot | Key Tech | Aliases & Search Terms |
|---------|-----|-------------|----------|----------------------|
| **Tesla** | 🇺🇸 Austin, TX | Optimus Gen 3 | End-to-end NN, FSD transfer | `Tesla Optimus`, `Tesla Bot`, `Tesla humanoid` |
| **Figure AI** | 🇺🇸 Sunnyvale, CA | Figure 02 | VLA + LLM (OpenAI collab) | `Figure AI`, `Figure 02`, `Figure robot` |
| **Boston Dynamics** | 🇺🇸 Waltham, MA | Electric Atlas | Whole-body athletic | `Boston Dynamics`, `Atlas`, `Electric Atlas` |
| **Agility Robotics** | 🇺🇸 Corvallis, OR | Digit | Warehouse logistics | `Agility Robotics`, `Digit`, `RoboFab` |
| **1X Technologies** | 🇳🇴 Moss, Norway | NEO Gamma | Tendon-driven, embodied AI | `1X Technologies`, `NEO`, `1X robot` |
| **Apptronik** | 🇺🇸 Austin, TX | Apollo | Modular, Mercedes collab | `Apptronik`, `Apollo robot` |
| **Sanctuary AI** | 🇨🇦 Vancouver, BC | Phoenix | Carbon AI control system | `Sanctuary AI`, `Phoenix robot`, `Carbon` |
| **Physical Intelligence** | 🇺🇸 San Francisco, CA | — (software) | π0, π0-FAST | `Physical Intelligence`, `pi zero`, `π0` |
| **Skild AI** | 🇺🇸 Pittsburgh, PA | — (software) | Scalable robot foundation model | `Skild AI`, `Skild robot` |
| **Unitree** | 🇨🇳 Hangzhou | G1, H1, B2-W | Low-cost, mass production | `Unitree`, `宇树`, `Unitree G1`, `Unitree H1` |
| **AGIBOT (Zhiyuan)** | 🇨🇳 Shanghai | A2, GENIE | Full-stack, VLA model | `AGIBOT`, `智元`, `智元机器人`, `Zhiyuan` |
| **UBTECH** | 🇨🇳 Shenzhen | Walker S2 | Public company, factory deploy | `UBTECH`, `优必选`, `Walker S` |
| **Galbot** | 🇨🇳 Shanghai | Galbot G1 | Mobile manipulation | `Galbot`, `银河通用`, `银河通用机器人` |
| **Fourier Intelligence** | 🇨🇳 Shanghai | GR-2 | Rehab origin, open platform | `Fourier Intelligence`, `傅利叶`, `Fourier GR` |
| **Xiaomi** | 🇨🇳 Beijing | CyberOne 2 | Consumer electronics crossover | `Xiaomi robot`, `CyberOne`, `小米机器人` |
| **XPeng Robotics** | 🇨🇳 Guangzhou | Iron | Auto industry crossover | `XPeng robot`, `小鹏机器人`, `Iron robot` |
| **Kepler** | 🇨🇳 Shanghai | Forerunner K2 | Industrial focus | `Kepler robot`, `开普勒`, `Forerunner` |
| **Robot Era** | 🇨🇳 Beijing | STAR1 | Agile locomotion | `Robot Era`, `星动纪元`, `STAR1` |
| **Booster Robotics** | 🇨🇳 Shenzhen | Booster T1 | Lightweight bipedal | `Booster Robotics`, `加速进化` |
| **LimX Dynamics** | 🇨🇳 Shenzhen | CL-2 | Legged locomotion | `LimX Dynamics`, `逐际动力` |
| **Noetix** | 🇨🇳 Beijing | N1 | Tsinghua spin-off | `Noetix`, `星海图` |

### 4.2 Platform & Infrastructure Companies

| Company | Role | Key Products | Search Terms |
|---------|------|-------------|-------------|
| **NVIDIA** | GPU + Sim + Foundation Model | Isaac Sim/Lab, GR00T, Cosmos, Jetson | `NVIDIA Isaac`, `NVIDIA GR00T`, `NVIDIA Cosmos` |
| **Google DeepMind** | Research + Models | RT-2, AutoRT, Gemini Robotics | `DeepMind robot`, `RT-2`, `Gemini Robotics` |
| **Meta FAIR** | Research + Open Source | Habitat, embodied research | `Meta robot`, `Habitat`, `Meta embodied` |
| **Hugging Face** | Open-Source Hub | LeRobot, model hosting | `LeRobot`, `Hugging Face robot` |
| **Toyota Research (TRI)** | Research + Demos | Diffusion Policy, LBM | `TRI robot`, `Toyota Research Institute` |
| **Amazon / Lab126** | Deployment + Research | Warehouse robotics | `Amazon robot`, `Sparrow`, `Lab126` |

### 4.3 Academic Labs (Tier 1)

| Lab | Affiliation | Focus Areas | Key People |
|-----|------------|-------------|-----------|
| **IRIS Lab** | Stanford | VLA, Diffusion Policy, ALOHA | Chelsea Finn, Sergey Levine (adj.) |
| **RAIL** | UC Berkeley | Robot learning, open-source models | Sergey Levine, Pieter Abbeel |
| **Robotic Exploration Lab** | CMU | Locomotion, manipulation | Deepak Pathak |
| **CSAIL** | MIT | Manipulation, soft robotics | Pulkit Agrawal, Russ Tedrake |
| **PAIR Lab** | Tsinghua | Embodied AI, humanoid | Hao Dong (董豪) |
| **IIIS** | Tsinghua | Robot learning | Yi Wu, Huazhe Xu |
| **CFCS** | PKU | Embodied intelligence | He Wang, Hao Su |
| **CLOVER Lab** | Shanghai AI Lab | VLA, embodied foundation model | — |
| **Robotics @ DeepMind** | Google DeepMind | RT-X, AutoRT, Gemini Robotics | Kanishka Rao |
| **TRI Robotics** | Toyota | Diffusion Policy, LBM, dexterous | Russ Tedrake, Ben Burchfiel |

---

## 5. Application Domain Taxonomy

```
Application Domains
│
├── Industrial / Manufacturing
│   ├── Assembly Line (pick-and-place, screw driving, insertion)
│   ├── Quality Inspection
│   ├── Material Handling
│   ├── Packaging & Palletizing
│   └── Machine Tending
│
├── Logistics & Warehouse
│   ├── Order Picking
│   ├── Sorting
│   ├── Goods-to-Person
│   ├── Last-Mile Delivery
│   └── Inventory Management
│
├── Household & Consumer
│   ├── Tidying / Cleaning
│   ├── Kitchen / Cooking
│   ├── Laundry (Folding, Sorting)
│   ├── Elderly Care / Assistance
│   └── Entertainment / Companionship
│
├── Healthcare & Medical
│   ├── Surgical Assistance
│   ├── Rehabilitation
│   ├── Hospital Logistics
│   ├── Nursing Assistance
│   └── Lab Automation
│
├── Agriculture & Food
│   ├── Harvesting
│   ├── Weeding / Spraying
│   ├── Livestock Management
│   └── Food Processing
│
├── Construction & Infrastructure
│   ├── Bricklaying / 3D Printing
│   ├── Welding / Cutting
│   ├── Inspection (Bridge, Pipeline, Power Line)
│   └── Demolition
│
├── Retail & Hospitality
│   ├── Shelf Stocking
│   ├── Customer Service
│   ├── Food Service / Delivery
│   └── Hotel Service
│
└── Research & Education
    ├── Lab Research Platform
    ├── STEM Education
    └── Competition (RoboCup, DARPA)
```

---

## 6. Simulation & Benchmark Taxonomy

### 6.1 Simulation Platforms

| Platform | Developer | Physics Engine | Key Strengths | Search Terms |
|----------|-----------|---------------|---------------|-------------|
| **Isaac Sim / Isaac Lab** | NVIDIA | PhysX 5 | GPU-parallel, photorealistic | `Isaac Sim`, `Isaac Lab`, `Isaac Gym` |
| **MuJoCo** | Google DeepMind | MuJoCo | Fast contact, research standard | `MuJoCo` |
| **SAPIEN** | UC San Diego / Hillbot | PhysX 5 | Articulated objects, ManiSkill | `SAPIEN`, `ManiSkill` |
| **Genesis** | Genesis Team | Custom | Differentiable, fast | `Genesis simulator` |
| **PyBullet** | Erwin Coumans | Bullet | Lightweight, open-source | `PyBullet` |
| **Gazebo** | Open Robotics | ODE/Bullet/DART | ROS integration | `Gazebo` |
| **Habitat** | Meta | Custom | Navigation, embodied QA | `Habitat simulator` |
| **RoboCasa** | UT Austin | MuJoCo | Household tasks | `RoboCasa` |
| **LIBERO** | UT Austin | MuJoCo | Lifelong learning benchmark | `LIBERO benchmark` |
| **RLBench** | Stephen James | CoppeliaSim | 100 manipulation tasks | `RLBench` |
| **Calvin** | Uni Freiburg | PyBullet | Language-conditioned | `CALVIN benchmark` |

### 6.2 Datasets

| Dataset | Scale | Content | Search Terms |
|---------|-------|---------|-------------|
| **Open X-Embodiment** | 1M+ episodes, 22 robots | Cross-embodiment manipulation | `Open X-Embodiment`, `OXE` |
| **DROID** | 76K episodes | Bimanual manipulation, diverse | `DROID dataset` |
| **BridgeData V2** | 60K+ trajectories | Tabletop manipulation | `BridgeData` |
| **RH20T** | 110K+ episodes | Chinese lab, diverse tasks | `RH20T` |
| **RoboSet** | 100K+ trajectories | Multi-skill manipulation | `RoboSet` |
| **ALOHA Datasets** | Various | Bimanual fine manipulation | `ALOHA dataset` |
| **RoboMIND** | 55K+ episodes | AGIBOT, real-world | `RoboMIND` |

---

## 7. Conference & Venue Taxonomy

### 7.1 Tier 1 — Must Track

| Conference | Full Name | Typical Date | Focus |
|-----------|-----------|-------------|-------|
| **CoRL** | Conference on Robot Learning | Oct–Nov | Robot learning (core venue) |
| **ICRA** | IEEE Intl. Conf. on Robotics & Automation | May–Jun | Broad robotics |
| **RSS** | Robotics: Science and Systems | Jul | Top-tier robotics theory |
| **IROS** | IEEE/RSJ Intl. Conf. on Intelligent Robots & Systems | Oct | Broad robotics |
| **NeurIPS** | Neural Information Processing Systems | Dec | ML (robot learning track) |
| **ICML** | Intl. Conf. on Machine Learning | Jul | ML (robot learning track) |
| **ICLR** | Intl. Conf. on Learning Representations | Apr–May | ML (growing robot track) |
| **CVPR** | Computer Vision and Pattern Recognition | Jun | Vision (embodied track) |

### 7.2 Tier 2 — Important

| Conference | Focus |
|-----------|-------|
| **HRI** | Human-Robot Interaction |
| **WAFR** | Algorithmic Foundations of Robotics |
| **Humanoids** | IEEE-RAS Intl. Conf. on Humanoid Robots |
| **RoboCup** | Robot competition |
| **ACL** | NLP (language grounding for robots) |
| **ECCV / ICCV** | Vision (embodied perception) |

### 7.3 Industry Events

| Event | Typical Date | Why It Matters |
|-------|-------------|---------------|
| **CES** | Jan | Consumer robot reveals |
| **NVIDIA GTC** | Mar | Isaac / GR00T announcements |
| **Google I/O** | May | DeepMind robotics demos |
| **Automate** | May | Industrial robotics trade show |
| **WRC (World Robot Conference)** | Aug | China ecosystem showcase |
| **CIFTIS** | Sep | China service trade (robot demos) |

---

## 8. Keyword Dictionary

A comprehensive bilingual (EN/CN) keyword list for search and classification.

### 8.1 Core Concepts

| English | Chinese | Aliases / Variants |
|---------|---------|-------------------|
| Embodied AI | 具身智能 | Embodied Intelligence, Physical AI |
| Humanoid Robot | 人形机器人 | Bipedal Robot, Android |
| Foundation Model | 基础模型 / 大模型 | Base Model, Pretrained Model |
| Vision-Language-Action | 视觉-语言-动作 | VLA |
| Diffusion Policy | 扩散策略 | Action Diffusion |
| World Model | 世界模型 | Predictive Model, Video Prediction Model |
| Imitation Learning | 模仿学习 | Learning from Demonstration, LfD |
| Reinforcement Learning | 强化学习 | RL |
| Sim-to-Real | 仿真到真实 | Sim2Real, Simulation Transfer |
| Teleoperation | 遥操作 | Remote Control, Puppet Control |
| Dexterous Manipulation | 灵巧操作 | In-Hand Manipulation, Fine Manipulation |
| Locomotion | 运动控制 | Walking, Bipedal Locomotion |
| Whole-Body Control | 全身控制 | WBC |
| Grasping | 抓取 | Grasp Planning |
| Mobile Manipulation | 移动操作 | Navigate-and-Manipulate |
| Cross-Embodiment | 跨本体 | Multi-Robot, Embodiment-Agnostic |
| Generalist Policy | 通用策略 | General-Purpose Policy |
| Large Behavior Model | 大行为模型 | LBM |
| Action Chunking | 动作分块 | ACT |
| Open Vocabulary | 开放词汇 | Zero-Shot Detection |

### 8.2 Hardware Terms

| English | Chinese | Aliases / Variants |
|---------|---------|-------------------|
| Actuator | 执行器 / 驱动器 | Motor, Drive |
| Harmonic Drive | 谐波减速器 | Strain Wave Gear |
| Planetary Gearbox | 行星减速器 | Planetary Reducer |
| Quasi-Direct-Drive | 准直驱 | QDD |
| BLDC Motor | 无刷直流电机 | Brushless DC Motor |
| Dexterous Hand | 灵巧手 | Robot Hand, Anthropomorphic Hand |
| Tactile Sensor | 触觉传感器 | Tactile Array |
| Force-Torque Sensor | 力矩传感器 | F/T Sensor, 6-axis F/T |
| End Effector | 末端执行器 | Gripper, Tool |
| Degrees of Freedom | 自由度 | DoF |
| Payload | 负载 | Load Capacity |
| Battery Life | 续航 | Runtime |
| Edge Computing | 边缘计算 | Onboard Compute |

### 8.3 Deployment & Business Terms

| English | Chinese | Aliases / Variants |
|---------|---------|-------------------|
| Deployment | 部署 / 落地 | Rollout, Go-Live |
| Pilot Program | 试点项目 | PoC, Proof of Concept |
| Units Shipped | 出货量 | Shipments |
| Task Success Rate | 任务成功率 | Completion Rate |
| Mean Time Between Failures | 平均故障间隔 | MTBF |
| Total Cost of Ownership | 总拥有成本 | TCO |
| Bill of Materials | 物料清单 | BOM |
| Series A/B/C | A/B/C轮融资 | Funding Round |
| Valuation | 估值 | Pre-money, Post-money |
| Total Addressable Market | 总可寻址市场 | TAM |
| Annual Recurring Revenue | 年度经常性收入 | ARR |
| Robot-as-a-Service | 机器人即服务 | RaaS |

### 8.4 Policy & Safety Terms

| English | Chinese | Aliases / Variants |
|---------|---------|-------------------|
| ISO 10218 | — | Industrial Robot Safety |
| ISO 13482 | — | Personal Care Robot Safety |
| ISO/TS 15066 | — | Collaborative Robot Safety |
| EU AI Act | 欧盟人工智能法案 | European AI Regulation |
| CE Marking | CE认证 | European Conformity |
| Export Control | 出口管制 | Sanctions, Entity List |
| Functional Safety | 功能安全 | SIL, Safety Integrity Level |
| Risk Assessment | 风险评估 | Hazard Analysis |

---

## 9. Relationship Maps

### 9.1 Technology Stack (Bottom-Up)

```
┌─────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                     │
│  Factory │ Warehouse │ Household │ Healthcare │ Agri    │
├─────────────────────────────────────────────────────────┤
│                    INTELLIGENCE LAYER                    │
│  VLA │ Diffusion Policy │ World Model │ RL │ LLM Plan  │
├─────────────────────────────────────────────────────────┤
│                    PERCEPTION LAYER                      │
│  RGB │ Depth │ Tactile │ Proprioception │ Language      │
├─────────────────────────────────────────────────────────┤
│                    CONTROL LAYER                         │
│  Whole-Body Control │ Impedance │ MPC │ Joint PD        │
├─────────────────────────────────────────────────────────┤
│                    HARDWARE LAYER                        │
│  Actuators │ Sensors │ Compute │ Power │ Structure      │
├─────────────────────────────────────────────────────────┤
│                    INFRASTRUCTURE LAYER                  │
│  Simulation │ Datasets │ Benchmarks │ ROS │ Cloud       │
└─────────────────────────────────────────────────────────┘
```

### 9.2 Data Flywheel

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Collect Data │────▶│  Train Model │────▶│   Deploy     │
│  (Teleop/Sim) │     │  (VLA/RL/IL) │     │  (Real World)│
└──────────────┘     └──────────────┘     └──────┬───────┘
       ▲                                          │
       │              ┌──────────────┐            │
       └──────────────│  More Data   │◀───────────┘
                      │  (Auto-Collect)│
                      └──────────────┘
```

### 9.3 Company Landscape Map

```
┌─────────────────────────────────────────────────────────────────┐
│                        FULL-STACK                                │
│  (Hardware + Software + Deployment)                             │
│                                                                 │
│  Tesla Optimus │ Figure │ 1X │ Agility │ Apptronik │ Sanctuary │
│  AGIBOT │ UBTECH │ Unitree │ Fourier │ Galbot │ Kepler        │
├─────────────────────────────────────────────────────────────────┤
│                     SOFTWARE / BRAIN                             │
│  (Foundation Models & Intelligence)                             │
│                                                                 │
│  Physical Intelligence │ Skild AI │ DeepMind │ TRI │ Covariant │
│  HuggingFace (LeRobot) │ Shanghai AI Lab (CLOVER)              │
├─────────────────────────────────────────────────────────────────┤
│                     PLATFORM / INFRA                             │
│  (Simulation, Compute, Tools)                                   │
│                                                                 │
│  NVIDIA (Isaac/GR00T) │ Meta (Habitat) │ MuJoCo │ ROS/Open Rob │
├─────────────────────────────────────────────────────────────────┤
│                     COMPONENTS / SUPPLY CHAIN                    │
│  (Actuators, Sensors, Hands)                                    │
│                                                                 │
│  Harmonic Drive │ 绿的谐波 │ 双环传动 │ PSYONIC │ Inspire Hand │
│  GelSight │ Robotiq │ OnRobot                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Versioning & Maintenance

### Current Version
- **Version**: 1.0
- **Created**: February 2026
- **Last Updated**: February 2026

### Maintenance Schedule
- **Weekly**: Add new model names, company names, product names as they appear
- **Monthly**: Review category tree structure; add/merge/split categories if needed
- **Quarterly**: Full taxonomy audit; update company table; refresh conference dates

### Changelog Template
```
## Changelog

### v1.1 — [Date]
- Added: [new term/company/category]
- Changed: [reclassified X from Y to Z]
- Removed: [deprecated term]
- Notes: [reason for change]
```

### Known Gaps (To Be Filled)
- [ ] Detailed supply chain component taxonomy (bearings, encoders, cables)
- [ ] Comprehensive Chinese academic lab list
- [ ] Emerging companies tracker (pre-Series A, stealth mode)
- [ ] Detailed safety standards mapping per region (US/EU/CN/JP/KR)
- [ ] Humanoid robot spec comparison table (height, weight, DoF, payload, battery, price)

---

> **This file is the "shared language" of the entire system.**
> When in doubt about how to classify a story, consult this file first.
> When a new term appears that doesn't fit, add it here before using it elsewhere.