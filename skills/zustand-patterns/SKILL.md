---
name: zustand-patterns
version: 1.0.0
description: Zustand 状态管理实战模式。涵盖 Store 设计规范、Slice 工厂复用、persist 持久化、可恢复任务持久化、Electron IPC 联动、Store 测试和常见陷阱。适用于 React + Zustand 项目。
---

# Zustand 状态管理模式

来自 14 个模块共用 Zustand 的生产级应用的实战经验。

## 适用场景

- React + Zustand 项目的状态管理设计
- 多模块 Store 拆分与复用
- 持久化 + 应用重启后恢复
- Electron 主进程 ↔ Store 联动
- Store 测试

---

## 1. Store 设计规范

### 一个模块一个 Store

```typescript
// ✅ 每个功能模块独立 Store
src/modules/video-compressor/store/index.ts   → useVideoCompressorStore
src/modules/video-upscaler/store/index.ts     → useVideoUpscalerStore

// ❌ 不要把所有状态塞进一个全局 Store
src/store/globalStore.ts → useGlobalStore  // 千万别这样
```

### Store 命名

```typescript
// Hook 导出用 use 前缀 + 模块名 + Store
export const useVideoCompressorStore = create<VideoCompressorStore>()(...)

// 文件名：index.ts 或 {moduleName}Store.ts
```

### Store 接口先行

```typescript
// ✅ 先定义接口，再实现
interface VideoCompressorStore {
  // — 状态 —
  inputFiles: string[];
  outputDir: string;
  targetSizeMB: number;
  logs: LogEntry[];

  // — Actions —
  setInputFiles: (files: string[]) => void;
  addInputFiles: (files: string[]) => void;
  removeInputFile: (path: string) => void;
  reset: () => void;
}

export const useVideoCompressorStore = create<VideoCompressorStore>()(
  persist(
    (set) => ({
      // 实现...
    }),
    { name: 'video-compressor' }
  )
);
```

### Action 命名

```typescript
// set 前缀：简单赋值
setInputFiles: (files) => set({ inputFiles: files }),
setTargetSizeMB: (size) => set({ targetSizeMB: size }),

// add/remove 前缀：集合操作
addInputFiles: (files) => set((state) => ({
  inputFiles: [...state.inputFiles, ...files.filter(f => !state.inputFiles.includes(f))]
})),
removeInputFile: (path) => set((state) => ({
  inputFiles: state.inputFiles.filter(p => p !== path)
})),

// clear 前缀：清空
clearInputFiles: () => set({ inputFiles: [] }),
clearLogs: () => set({ logs: [] }),

// reset：恢复初始状态
reset: () => set({ inputFiles: [], outputDir: '', targetSizeMB: 50, logs: [] }),
```

---

## 2. Slice 工厂（跨 Store 复用）

多个 Store 有相同的状态片段时，用 Slice 工厂提取：

### 定义 Slice

```typescript
// store/slices/createProcessingSlice.ts

export interface ProcessingSliceState<TProgress = number> {
  isProcessing: boolean;
  progress: TProgress;
  setIsProcessing: (isProcessing: boolean) => void;
  setProgress: (progress: TProgress) => void;
  resetProcessing: () => void;
}

export function createProcessingSlice<TProgress = number>(
  set: SetState<ProcessingSliceState<TProgress>>,
  defaultProgress: TProgress = 0 as TProgress,
): ProcessingSliceState<TProgress> {
  return {
    isProcessing: false,
    progress: defaultProgress,
    setIsProcessing: (isProcessing) => set({ isProcessing } as any),
    setProgress: (progress) => set({ progress } as any),
    resetProcessing: () => set({ isProcessing: false, progress: defaultProgress } as any),
  };
}
```

### 使用 Slice

```typescript
interface MyModuleStore extends ProcessingSliceState {
  inputFiles: string[];
  // ...
}

const useMyModuleStore = create<MyModuleStore>()((set) => ({
  ...createProcessingSlice(set),  // 展开混入
  inputFiles: [],
  // ...
}));
```

### 泛型 Slice

```typescript
// progress 不一定是 number，可以是复杂对象
interface SceneAnalyzerProgress {
  phase: 'splitting' | 'analyzing' | 'done';
  current: number;
  total: number;
}

interface SceneAnalyzerStore extends ProcessingSliceState<SceneAnalyzerProgress | null> {
  // ...
}

const store = create<SceneAnalyzerStore>()((set) => ({
  ...createProcessingSlice<SceneAnalyzerProgress | null>(set, null),
  // ...
}));
```

---

## 3. 持久化

### 基本持久化

```typescript
import { persist } from 'zustand/middleware';

const useSettingsStore = create<SettingsStore>()(
  persist(
    (set) => ({ /* ... */ }),
    {
      name: 'settings-storage',           // localStorage key
      version: 1,                          // 迁移版本
      partialize: (state) => ({            // 只持久化部分字段
        outputDir: state.outputDir,
        targetSizeMB: state.targetSizeMB,
        // ❌ 不持久化 isProcessing、logs 等运行时状态
      }),
    }
  )
);
```

### 关键原则

```typescript
// ✅ 持久化：用户配置、偏好设置
partialize: (state) => ({
  outputDir: state.outputDir,
  quality: state.quality,
  encoder: state.encoder,
})

// ❌ 不持久化：运行时状态
// isProcessing, progress, logs, error — 这些重启后应该重置
```

### Electron 存储

Electron 中 `localStorage` 可用（渲染进程），但如果需要主进程访问，用 `electron-store`：

```typescript
import { persist, createJSONStorage } from 'zustand/middleware';

// 自定义 storage adapter 走 IPC
const electronStorage = createJSONStorage(() => ({
  getItem: (name) => ipcRenderer.invoke('store:get', name),
  setItem: (name, value) => ipcRenderer.invoke('store:set', name, value),
  removeItem: (name) => ipcRenderer.invoke('store:remove', name),
}));
```

---

## 4. 可恢复任务持久化（高级）

远程异步任务（如 AI 视频生成）提交后，应用重启需要恢复轮询：

```typescript
interface RecoverableTaskState {
  needsPollingRecovery: boolean;
  clearPollingRecoveryFlag: () => void;
}

function createRecoverablePersistConfig<T>({
  name,
  taskField,
  isTaskPending,
  additionalFields = [],
}: {
  name: string;
  taskField: keyof T;
  isTaskPending: (task: any) => boolean;
  additionalFields?: (keyof T)[];
}) {
  return {
    name,
    partialize: (state: T) => {
      const result: any = { [taskField]: state[taskField] };
      for (const field of additionalFields) {
        result[field] = state[field];
      }
      return result;
    },
    onRehydrate: (state: T) => {
      // 检查是否有需要恢复的 pending 任务
      const tasks = (state as any)[taskField] || [];
      if (Array.isArray(tasks) && tasks.some(isTaskPending)) {
        (state as any).needsPollingRecovery = true;
      }
    },
  };
}

// 使用
const store = create<MyState>()(
  persist(
    (set, get) => ({ /* ... */ }),
    createRecoverablePersistConfig({
      name: 'video-upscaler',
      taskField: 'tasks',
      isTaskPending: (task) => task.status === 'processing' && !!task.remoteId,
      additionalFields: ['config'],
    })
  )
);

// 组件中恢复轮询
useEffect(() => {
  if (store.needsPollingRecovery) {
    store.clearPollingRecoveryFlag();
    store.recoverPolling();
  }
}, []);
```

### 适用 vs 不适用

```
✅ 适用：远程 API 任务（视频超分、AI 生成）— 服务端继续处理
❌ 不适用：本地进程任务（FFmpeg 压缩）— 进程随应用关闭而终止
```

---

## 5. Electron IPC ↔ Store 联动

### 主进程事件 → Store 更新

```typescript
// 渲染进程：监听主进程事件更新 Store
useEffect(() => {
  const listeners = [
    window.electronAPI.on('module:progress', (progress: number) => {
      useMyStore.getState().setProgress(progress);
    }),
    window.electronAPI.on('module:complete', () => {
      useMyStore.getState().setIsProcessing(false);
      useMyStore.getState().setProgress(100);
    }),
    window.electronAPI.on('module:error', (error: string) => {
      useMyStore.getState().setIsProcessing(false);
      useMyStore.getState().setError(error);
    }),
    window.electronAPI.on('module:log', (msg: string, type: string) => {
      useMyStore.getState().addLog(msg, type);
    }),
  ];

  return () => listeners.forEach(cleanup => cleanup());
}, []);
```

### Store Action → IPC 调用

```typescript
// Store 中发起 IPC 调用
startProcessing: async () => {
  const { inputFiles, outputDir, targetSizeMB } = get();
  set({ isProcessing: true, progress: 0 });

  try {
    await window.electronAPI.invoke('module:start', {
      files: inputFiles,
      outputDir,
      targetSizeMB,
    });
  } catch (error) {
    set({ isProcessing: false, error: getErrorMessage(error) });
  }
},

stopProcessing: () => {
  window.electronAPI.invoke('module:stop');
},
```

### 关键：`getState()` 防闭包

```typescript
// ❌ 闭包陷阱：回调函数中的 state 是旧的
window.electronAPI.on('update', () => {
  const { tasks } = store; // 闭包捕获的旧值！
});

// ✅ 每次用 getState() 获取最新
window.electronAPI.on('update', () => {
  const { tasks } = useMyStore.getState(); // 始终最新
});
```

---

## 6. Store 测试

### 测试模板

```typescript
import { act } from 'react';
import { useVideoCompressorStore } from '../store';

describe('VideoCompressorStore', () => {
  beforeEach(() => {
    // 每个测试前重置 Store
    act(() => {
      useVideoCompressorStore.getState().reset();
    });
  });

  it('should add input files without duplicates', () => {
    act(() => {
      useVideoCompressorStore.getState().addInputFiles(['/a.mp4', '/b.mp4']);
      useVideoCompressorStore.getState().addInputFiles(['/b.mp4', '/c.mp4']);
    });

    const { inputFiles } = useVideoCompressorStore.getState();
    expect(inputFiles).toEqual(['/a.mp4', '/b.mp4', '/c.mp4']);
  });

  it('should reset to initial state', () => {
    act(() => {
      useVideoCompressorStore.getState().setInputFiles(['/a.mp4']);
      useVideoCompressorStore.getState().setIsProcessing(true);
      useVideoCompressorStore.getState().reset();
    });

    const state = useVideoCompressorStore.getState();
    expect(state.inputFiles).toEqual([]);
    expect(state.isProcessing).toBe(false);
  });
});
```

### 测试 Persist

```typescript
// 测试持久化时 mock localStorage
beforeEach(() => {
  localStorage.clear();
});

it('should persist and rehydrate config', () => {
  act(() => {
    useSettingsStore.getState().setTargetSizeMB(100);
  });

  // 模拟刷新：重新创建 store
  // zustand persist 会从 localStorage 读取
  const persisted = JSON.parse(localStorage.getItem('settings-storage') || '{}');
  expect(persisted.state.targetSizeMB).toBe(100);
});
```

---

## 7. 常见陷阱

### 闭包过期

```typescript
// ❌ useEffect 中直接用解构的值
const { tasks } = useMyStore();
useEffect(() => {
  const interval = setInterval(() => {
    console.log(tasks); // 永远是初始值！
  }, 1000);
  return () => clearInterval(interval);
}, []); // deps 为空

// ✅ 用 getState()
useEffect(() => {
  const interval = setInterval(() => {
    console.log(useMyStore.getState().tasks); // 最新值
  }, 1000);
  return () => clearInterval(interval);
}, []);
```

### 过度订阅

```typescript
// ❌ 订阅整个 Store（任何字段变化都重渲染）
const store = useMyStore();

// ✅ 只订阅需要的字段
const isProcessing = useMyStore((s) => s.isProcessing);
const progress = useMyStore((s) => s.progress);

// ✅ 多字段用 shallow 比较
import { useShallow } from 'zustand/react/shallow';
const { files, dir } = useMyStore(
  useShallow((s) => ({ files: s.inputFiles, dir: s.outputDir }))
);
```

### 循环更新

```typescript
// ❌ useEffect 中 set 触发重渲染 → 再触发 useEffect
useEffect(() => {
  useMyStore.getState().setProgress(calculateProgress());
}, [someValue]); // someValue 也来自同一个 Store → 死循环

// ✅ 用 subscribe 或在 action 内部处理
useMyStore.subscribe(
  (state) => state.tasks,
  (tasks) => { /* 根据 tasks 更新 progress */ },
  { equalityFn: shallow }
);
```

---

## 8. Checklist

### 新建 Store
- [ ] 接口先行（先写 interface 再实现）
- [ ] 一模块一 Store，用 `use` 前缀命名
- [ ] 复用 Slice 工厂（ProcessingSlice 等）
- [ ] `partialize` 只持久化配置，不持久化运行时状态
- [ ] Action 命名：set / add / remove / clear / reset

### 使用 Store
- [ ] 组件中用选择器订阅，不订阅整个 Store
- [ ] 回调/定时器中用 `getState()` 防闭包
- [ ] IPC 事件监听在 useEffect 中注册和清理

### 测试
- [ ] `beforeEach` 中 `reset()` Store
- [ ] 测试 action 用 `act()` 包裹
- [ ] 持久化测试 mock `localStorage`
