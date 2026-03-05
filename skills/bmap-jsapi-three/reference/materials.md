# 材质系统使用指南

## 概述

MapV Three 提供 WaterMaterial（水面材质）和 ExtendMeshStandardMaterial（扩展网格标准材质）。

## WaterMaterial - 水面材质

创建动态流动的水面效果，适用于河流、湖泊、海洋等水体可视化。

### 基础用法

```javascript
const waterMaterial = new mapvthree.WaterMaterial({
    waterColor: [0.004, 0.18, 0.47],   // RGB 归一化颜色
    foamSpeed: 0.05,
    style: 'lake'                       // 'river' | 'lake' | 'ocean'
});

// 应用到 Polygon
const polygon = engine.add(new mapvthree.Polygon({
    polygon: [[116.40, 39.90, 0], [116.41, 39.90, 0], [116.41, 39.91, 0]],
    material: waterMaterial,
    height: 100
}));
```

### WaterMaterial 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `waterColor` | Array\<number\> | `[1/255, 46/255, 120/255]` | 水体颜色（RGB 归一化数组） |
| `foamSpeed` | number | `0.10` | 泡沫流动速度 |
| `offsetScale` | number | `1` | 偏移缩放 |
| `depthSoftness` | number | `5` | 深度柔和度 |
| `foamDepthSoftness` | number | `1` | 泡沫深度柔和度 |
| `foamSoftness` | number | `3` | 泡沫柔和度 |
| `foamScale` | number | `0.1` | 泡沫贴图缩放比例 |
| `crestFoam` | number | `0.70` | 波峰泡沫强度 |
| `crestFoamColor` | Array\<number\> | `[0.3, 0.3, 0.6]` | 波峰泡沫颜色（RGB 归一化） |
| `specularStrength` | number | `1.5` | 镜面反射强度 |
| `uvScale` | number | `1.0` | UV 纹理缩放 |
| `useEnvMap` | boolean | `true` | 是否使用环境贴图 |
| `timeScaleFactor` | number | `0.001` | 时间缩放因子 |

### style 属性

`style` 属性切换不同的水体法线贴图风格：

| 值 | 说明 |
|------|------|
| `'river'` | 河流风格 |
| `'lake'` | 湖泊风格（默认） |
| `'ocean'` | 海洋风格 |

```javascript
waterMaterial.style = 'ocean';
```

### 动态修改属性

```javascript
const waterMaterial = new mapvthree.WaterMaterial();

waterMaterial.waterColor = [0.0, 0.5, 0.8];
waterMaterial.foamSpeed = 0.15;
waterMaterial.style = 'river';
waterMaterial.specularStrength = 2.0;
```

### 示例：不同水体效果

```javascript
// 河流
const riverMaterial = new mapvthree.WaterMaterial({
    waterColor: [0.0, 0.3, 0.6],
    foamSpeed: 0.15,
    style: 'river'
});

// 海洋
const oceanMaterial = new mapvthree.WaterMaterial({
    waterColor: [0.004, 0.18, 0.47],
    foamSpeed: 0.05,
    crestFoam: 0.9,
    style: 'ocean',
    depthSoftness: 8
});
```

---

## ExtendMeshStandardMaterial - 扩展网格标准材质

基于 Three.js MeshStandardMaterial 扩展，提供 PBR（物理基渲染）效果。

### 基础用法

```javascript
const material = new mapvthree.ExtendMeshStandardMaterial({
    color: 0xcccccc,
    metalness: 0.5,
    roughness: 0.5,
    map: textureMap,
    normalMap: normalMap
});

const model = engine.add(new mapvthree.SimpleModel({
    url: 'assets/building.glb',
    material: material
}));
```

### ExtendMeshStandardMaterial 参数表

#### 基础颜色

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `color` | Color/number | `0xffffff` | 基础颜色 |
| `map` | Texture | null | 颜色贴图 |
| `emissive` | Color/number | `0x000000` | 自发光颜色 |
| `emissiveMap` | Texture | null | 自发光贴图 |
| `emissiveIntensity` | number | `1.0` | 自发光强度 |

#### PBR 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `metalness` | number | `0.0` | 金属度 (0-1) |
| `roughness` | number | `1.0` | 粗糙度 (0-1) |
| `metalnessMap` | Texture | null | 金属度贴图 |
| `roughnessMap` | Texture | null | 粗糙度贴图 |

#### 法线和环境

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `normalMap` | Texture | null | 法线贴图 |
| `normalScale` | Vector2 | (1, 1) | 法线强度 |
| `bumpMap` | Texture | null | 凹凸贴图 |
| `bumpScale` | number | `1.0` | 凹凸强度 |
| `envMap` | Texture | null | 环境反射贴图 |
| `envMapIntensity` | number | `1.0` | 环境反射强度 |
| `opacity` | number | `1.0` | 透明度 (0-1) |
| `transparent` | boolean | `false` | 启用透明度 |

### 示例：不同材质效果

```javascript
// 金属建筑
const metalBuilding = new mapvthree.ExtendMeshStandardMaterial({
    color: 0x888888,
    metalness: 0.9,
    roughness: 0.1,
    emissive: 0x111111,
    emissiveIntensity: 0.2
});

// 玻璃窗
const glass = new mapvthree.ExtendMeshStandardMaterial({
    color: 0x88ccff,
    metalness: 0.0,
    roughness: 0.05,
    opacity: 0.3,
    transparent: true,
    envMapIntensity: 0.8
});
```
