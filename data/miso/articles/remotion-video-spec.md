# Remotion動画プロジェクト：MISOプログレス可視化

## 概要
MISOの進捗バーをRemotionでアニメーション動画として実装

## コンポーネント設計

### 1. MissionCard
メインカードコンポーネント
```
interface MissionCardProps {
  phase: 'init' | 'running' | 'partial' | 'approval' | 'complete' | 'error';
  missionDescription: string;
  agents: Agent[];
  elapsedTime: string;
  cost: string;
}
```

### 2. ProgressBar
16セグメントの進捗バー
```
interface ProgressBarProps {
  progress: number; // 0-100
  agentName?: string; // エージェント名（エージェント固有の場合）
}
```

### 3. AgentRow
エージェントごとの進捗行
```
interface AgentRowProps {
  agent: {
    name: string;
    task: string;
    status: 'init' | 'running' | 'complete' | 'error';
    progress: number;
    thinking?: string;
    resultSummary?: string;
  };
}
```

### 4. ReactionBadge
リアクションバッジ（🔥👀🎉❌）
```
interface ReactionBadgeProps {
  emoji: string;
  animated: boolean;
}
```

## アニメーション仕様

### Phase Transitions
```typescript
const phaseTransition = {
  init: {
    duration: 60,
    easing: easings.outQuart,
  },
  running: {
    duration: 30,
    easing: easings.inOutCubic,
    loop: true,
  },
  partial: {
    duration: 45,
    easing: easings.inOutQuad,
  },
  approval: {
    duration: 30,
    easing: easings.outBack,
  },
  complete: {
    duration: 60,
    easing: easings.elastic(1, 0.5),
  },
  error: {
    duration: 30,
    easing: easings.outBounce,
  },
};
```

### ProgressBar Animation
21フレーム（0%-100% 5%刻み）
```typescript
<Sequence from={0} duration={21 * 30}>
  {[...Array(21).keys()].map((frame) => (
    <AbsoluteFrame
      key={`frame-${frame}`}
      frame={frame}
      style={{ opacity: 1 - Math.abs(currentFrame - frame) / 5 }}
    >
      <ProgressBar progress={frame * 5} />
    </AbsoluteFrame>
  ))}
</Sequence>
```

### Reaction Animation
リアクション切り替え時のアニメーション
```typescript
const reactionVariants = {
  fire: {
    scale: [0, 1.2, 1],
    rotate: [-15, 15, -15, 15, 0],
    opacity: [0, 1],
    transition: { duration: 0.5 },
  },
  eyes: {
    scale: [0, 1.1, 1],
    x: [-20, 20, -20, 20, 0],
    opacity: [0, 1],
    transition: { duration: 0.6 },
  },
  party: {
    scale: [0, 1.3, 1],
    rotate: [0, 360, 720, 0],
    opacity: [0, 1],
    transition: { duration: 0.8 },
  },
  error: {
    scale: [0, 1.2, 1],
    x: [-10, 10, -10, 10, 0],
    opacity: [0, 1],
    transition: { duration: 0.4 },
  },
};
```

## スタイリング

### カラーパレット
```typescript
const colors = {
  dark: {
    background: '#0a0a0a',
    card: '#1a1a1a',
    text: '#ffffff',
    accent: '#ff6b35', // オレンジ
    success: '#22c55e',
    warning: '#eab308',
    danger: '#ef4444',
  },
  light: {
    background: '#ffffff',
    card: '#f5f5f5',
    text: '#0a0a0a',
    accent: '#ff6b35',
    success: '#22c55e',
    warning: '#eab308',
    danger: '#ef4444',
  },
};
```

### Unicode Bold Font
```typescript
const unicodeBold = {
  fontFamily: 'Noto Sans JP',
  fontWeight: 700,
  // Mathematical Bold Sans-Serif characters
  // 𝗠𝗜𝗦𝗦𝗜𝗢𝗡 𝗖𝗢𝗡𝗧𝗥𝗼𝗟
};
```

## レンダリング設定

### 出力フォーマット
```json
{
  "formats": {
    "mp4": {
      "codec": "h264",
      "bitrate": "2000k",
      "audio": false,
    },
    "webm": {
      "codec": "vp9",
      "bitrate": "1800k",
      "audio": false,
    },
  },
  "resolutions": {
    "1920x1080": "YouTube",
    "1080x1920": "YouTube Shorts / TikTok",
    "1080x1080": "Instagram",
  },
}
```

### アスペクト比
- 16:9（YouTube・Instagram Reels）
- 9:16（YouTube Shorts・TikTok）
- 1:1（Instagram）

## BGM選定

候補：
1. **Lo-Fi Tech** — コーディング・開発に適した落ち着いたBGM
2. **Electronic Ambient** — スタイリッシュでモダンな雰囲気
3. **Minimal Clicks** — クリック音のみ（シンプル派向け）

## シナリオ

### シーン1: INIT
```
[0-2s] MissionCard fade in
[2-4s] AgentRow init status animation (×3)
[4-6s] 🔥 reaction badge pop in
```

### シーン2: RUNNING
```
[0-10s] ProgressBar 0% → 100% loop
[0-10s] AgentRow progress update
[0-10s] 🧠 thinking text update
```

### シーン3: PARTIAL
```
[0-3s] Agent 1 complete → ✅
[3-6s] Agent 2 complete → ✅
[6-10s] Agent 3 still running with progress
```

### シーン4: COMPLETE
```
[0-2s] 🎉 reaction badge explosion
[2-4s] All agents → ✅
[4-6s] Mission summary fade in
[6-8s] GitHub link CTA
```

## 次のステップ

- [x] コンポーネント設計
- [ ] Remotionプロジェクト初期化
- [ ] アニメーション実装
- [ ] レンダリングテスト
- [ ] YouTubeアップロード
- [ ] X/TikTok投稿
