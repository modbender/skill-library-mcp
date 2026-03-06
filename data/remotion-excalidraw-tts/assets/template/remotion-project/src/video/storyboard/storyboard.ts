import type {Focus} from '../components/FocusOverlay';

export type Camera = {x: number; y: number; scale: number};

export type Scene = {
  name: string;
  from: number;
  to: number;
  cameraFrom: Camera;
  cameraTo: Camera;
  focus?: Focus;
  subtitle?: string;
};

const sec = (fps: number, s: number) => Math.round(fps * s);

type Args = {fps: number; width: number; height: number};

type StoryboardJson = {
  fps?: number;
  scenes: Array<{
    name: string;
    durationSec: number;
    subtitle?: string;
    cameraFrom: Camera;
    cameraTo: Camera;
    focus?: Focus;
  }>;
};

const defaultStoryboard = ({fps}: Args): Scene[] => {
  // NOTE: Excalidraw canvas coordinates depend on the drawing. We start with
  // conservative whole-canvas framing and simple focus rectangles.
  const scenes: Omit<Scene, 'from' | 'to'>[] = [
    {
      name: 'cold-open',
      cameraFrom: {x: 0, y: 0, scale: 1},
      cameraTo: {x: 0, y: 0, scale: 1},
      subtitle: '很多智能体看起来很聪明，但隔天就失忆。',
      focus: {x: 140, y: 120, width: 1640, height: 340, label: '长期记忆问题'},
    },
    {
      name: 'openclaw-positioning',
      cameraFrom: {x: 0, y: 0, scale: 1},
      cameraTo: {x: -80, y: -30, scale: 1.12},
      subtitle: 'OpenClaw 的目标：能操作设备的数字助手。',
      focus: {x: 120, y: 140, width: 1680, height: 440, label: '从聊天到“能做事”'},
    },
    {
      name: 'four-contexts',
      cameraFrom: {x: -80, y: -30, scale: 1.12},
      cameraTo: {x: -180, y: -80, scale: 1.25},
      subtitle: '上下文四来源：长期知识 / 任务记忆 / 会话历史 / 外部资源。',
      focus: {x: 120, y: 220, width: 1680, height: 520, label: '上下文供给系统'},
    },
    {
      name: 'file-based',
      cameraFrom: {x: -180, y: -80, scale: 1.25},
      cameraTo: {x: -260, y: -130, scale: 1.35},
      subtitle: '基线方案：Markdown 作为真实之源 + 后端索引检索。',
      focus: {x: 140, y: 260, width: 1640, height: 520, label: '文件型记忆（SoT）'},
    },
    {
      name: 'lancedb-plugin',
      cameraFrom: {x: -260, y: -130, scale: 1.35},
      cameraTo: {x: -340, y: -170, scale: 1.45},
      subtitle: 'memory-lancedb：对话前自动回忆，对话后自动捕获。',
      focus: {x: 160, y: 260, width: 1600, height: 560, label: '自动驾驶的长期记忆'},
    },
    {
      name: 'loop',
      cameraFrom: {x: -340, y: -170, scale: 1.45},
      cameraTo: {x: -420, y: -220, scale: 1.55},
      subtitle: '形成闭环：recall → 执行 → capture → embedding → 写入 → 下次召回。',
      focus: {x: 160, y: 300, width: 1600, height: 600, label: '记忆闭环'},
    },
    {
      name: 'outro',
      cameraFrom: {x: -420, y: -220, scale: 1.55},
      cameraTo: {x: -420, y: -220, scale: 1.55},
      subtitle: '下一步：我们进代码，验证配置、表结构和注入时序。',
      focus: {x: 120, y: 700, width: 1680, height: 260, label: '下一集预告'},
    },
  ];

  const durations = [15, 25, 30, 35, 45, 25, 10].map((s) => sec(fps, s));

  const out: Scene[] = [];
  let cursor = 0;
  scenes.forEach((scene, i) => {
    const d = durations[i] ?? sec(fps, 20);
    out.push({
      ...scene,
      from: cursor,
      to: cursor + d,
    });
    cursor += d;
  });

  return out;
};

export const storyboardFromJson = (json: StoryboardJson, fps: number): Scene[] => {
  let cursor = 0;
  return json.scenes.map((s) => {
    const d = sec(fps, s.durationSec);
    const out: Scene = {
      name: s.name,
      from: cursor,
      to: cursor + d,
      subtitle: s.subtitle,
      cameraFrom: s.cameraFrom,
      cameraTo: s.cameraTo,
      focus: s.focus,
    };
    cursor += d;
    return out;
  });
};

export const makeStoryboard = ({fps}: Args): Scene[] => {
  return defaultStoryboard({fps, width: 0, height: 0});
};
