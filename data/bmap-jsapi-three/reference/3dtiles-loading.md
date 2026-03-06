# 3D Tiles 加载指南

## 概述

3D Tiles 是用于流式传输大规模 3D 地理空间数据的开放规范。MapV-Three 提供多个 3D Tiles 类：

- `Default3DTiles` — 通用 3D Tiles 加载器，支持 URL 和 Cesium Ion 加载
- `Default3DTilesGroup` — 多 URL 批量加载，统一管理多个 Default3DTiles 实例
- `HDMap3DTiles` — 高精地图专用，继承 Default3DTiles，内置 HD 地图材质、元素编辑、可见性控制和车道网格功能
- `TrafficMap3DTiles` — 实时路况专用，继承 Default3DTiles，自动轮询交通状态并着色

## Default3DTiles

### 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `url` | string | - | 3D Tiles URL（tileset.json） |
| `assetId` | number | - | Cesium Ion asset ID（与 url 二选一） |
| `errorTarget` | number | `64` | 屏幕空间误差目标值，越小越精细 |
| `forceUnlit` | boolean | `false` | 强制无光照模式 |
| `cullWithChildrenBounds` | boolean | `true` | 使用子节点边界剔除 |
| `cullRequestsWhileMoving` | boolean | `true` | 移动时剔除请求 |
| `cullRequestsWhileMovingMultiplier` | number | `60` | 移动时剔除请求乘数 |
| `dynamicScreenSpaceError` | boolean | `true` | 动态屏幕空间误差 |
| `dynamicScreenSpaceErrorHeightFalloff` | number | `0.25` | 动态误差高度衰减 |
| `dynamicScreenSpaceErrorDensity` | number | `0.00278` | 动态误差密度 |
| `foveatedScreenSpaceError` | boolean | `false` | 注视点屏幕空间误差 |
| `foveatedConeSize` | number | `0.3` | 注视点锥体大小 (0-1) |
| `foveatedMinimumScreenSpaceErrorRelaxation` | number | `0.8` | 注视点最小误差松弛值 |
| `progressiveResolutionHeightFraction` | number | `0.5` | 渐进式分辨率高度分数 |
| `cacheBytes` | number | - | 缓存字节数 |

### 可读写属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `errorTarget` | number | 屏幕空间误差目标值 |
| `showDebug` | boolean | 显示调试信息（包括 BoundingBox / Sphere / Region） |
| `cullWithChildrenBounds` | boolean | 子节点边界剔除 |
| `cullRequestsWhileMoving` | boolean | 移动时剔除请求 |
| `foveatedConeSize` | number | 注视点锥体大小 |
| `loadSiblings` | boolean | 加载兄弟节点 |
| `materialManager` | Default3DTilesMaterialManager | 材质管理器（见下方"材质管理器"章节） |
| `castShadow` | boolean | 投射阴影 |
| `receiveShadow` | boolean | 接收阴影 |
| `forceUnlit` | boolean | 强制无光照模式 |
| `freezeUpdate` | boolean | 冻结瓦片更新（暂停遍历和加载） |

### 只读属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `instancedElementManager` | TileInstancedElementManager | 实例化元素管理器 |
| `editableElementManager` | EditableElementManager | 可编辑元素管理器 |
| `elementsManager` | ElementsManager | 元素管理器 |

### 方法

| 方法 | 说明 |
|------|------|
| `lockCameraViewport()` | 锁定 3D Tiles 内部虚拟相机视角 |
| `releaseCameraViewport()` | 释放相机视角锁定 |
| `getBounds()` | 获取 3D Tiles 包围盒（返回 `Box3` 或 `null`） |
| `forEachLoadedModel(callback)` | 遍历所有已加载的瓦片，回调参数为 `(scene, tile)` |
| `Default3DTiles.fromAssetId(assetId, options)` | 静态方法，从 Cesium Ion 创建实例（返回 Promise） |

### 示例：从 URL 加载

```javascript
const tileset = engine.add(new mapvthree.Default3DTiles({
    url: 'https://example.com/tileset.json',
    errorTarget: 16,
}));

tileset.addEventListener('loadComplete', () => {
    console.log('3D Tiles 加载完成');
});
```

### 示例：从 Cesium Ion 加载

```javascript
mapvthree.Default3DTiles.fromAssetId(8564, {
    errorTarget: 32,
    dynamicScreenSpaceError: true,
}).then(tileset => engine.add(tileset));
```

### 示例：动态调整精度

```javascript
const tileset = engine.add(new mapvthree.Default3DTiles({
    url: 'path/to/tileset.json',
    errorTarget: 32,
}));

// 低质量浏览
tileset.errorTarget = 64;

// 高质量检查
tileset.errorTarget = 8;
```

## Default3DTilesGroup

用于同时加载多个 3D Tiles URL，统一管理属性（errorTarget、materialManager 等属性会自动同步到所有子实例）。

### 构造参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `url` | string[] | **必填**，3D Tiles URL 数组 |
| 其余参数 | - | 同 Default3DTiles 构造参数，会透传给每个子实例 |

### 示例

```javascript
const group = engine.add(new mapvthree.Default3DTilesGroup({
    url: [
        'https://example.com/part1/tileset.json',
        'https://example.com/part2/tileset.json',
    ],
    errorTarget: 32,
}));

// 属性修改会同步到所有子实例
group.errorTarget = 16;
```

## HDMap3DTiles

高精地图 3D Tiles 加载器，继承自 `Default3DTiles`。内置高精地图材质管理、护栏/隧道灯/桥墩等实例化模型、元素编辑和可见性控制功能。

### 构造参数

同 `Default3DTiles`。

### 独有属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `isHDMap3DTiles` | boolean | 固定为 `true`，用于类型标识 |
| `edit` | HDMapEdit | 高精地图元素编辑器（懒加载，首次访问时创建） |
| `turn` | HDMapTurnEdit | 转向等待区编辑器（懒加载） |
| `visibility` | HDMapVisibility | 元素可见性控制器（懒加载） |
| `grid` | HDMapGrid | 车道级网格线控制器（懒加载） |

### 独有方法

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `setGroupMaterial(groupName, properties)` | this | 设置材质分组的效果，支持 opacity、visible、color 等 |
| `resetGroupMaterial(groupName)` | this | 重置材质分组效果到默认状态 |
| `getMaterialGroups()` | string[] | 获取所有可用的材质分组名称 |
| `isEntityVisible(entity)` | boolean | 判断实体是否可见（综合 visibility 和 editableElementManager） |

### HDMapVisibility（通过 `hdmap.visibility` 访问）

控制高精地图元素按 ID 或图层类型（dataType）的显隐。

| 方法 | 说明 |
|------|------|
| `addHiddenId(id)` / `addHiddenIds(ids)` | 按 ID 隐藏元素 |
| `removeHiddenId(id)` / `removeHiddenIds(ids)` | 移除 ID 隐藏 |
| `clearHiddenIds()` | 清空所有 ID 隐藏 |
| `isEntityHidden(id)` | 判断 ID 是否被隐藏 |
| `addHiddenLayer(id)` / `addHiddenLayers(ids)` | 按 dataType 隐藏整个图层 |
| `removeHiddenLayer(id)` / `removeHiddenLayers(ids)` | 移除图层隐藏 |
| `clearHiddenLayers()` | 清空所有图层隐藏 |
| `isLayerHidden(id)` | 判断图层是否被隐藏 |

### HDMapGrid（通过 `hdmap.grid` 访问）

车道级网格线功能，支持点击查询。

| 属性/方法 | 类型 | 说明 |
|-----------|------|------|
| `enabled` | boolean | 是否启用车道级网格线 |
| `apiHost` | string | 车道网格查询接口地址 |
| `selectMesh` | Polygon | 点击高亮的网格体对象（只读） |
| 事件 `click` | - | 点击网格时触发，`event.value` 为 GeoJSON Feature |

### HDMapEdit（通过 `hdmap.edit` 访问）

高精地图元素编辑功能（需与后端服务配合使用）。

| 属性 | 类型 | 说明 |
|------|------|------|
| `enabled` | boolean | 是否启用编辑模式 |
| `apiHost` | string | 编辑服务接口地址 |
| `author` | string | 编辑操作的作者标识 |

| 方法 | 说明 |
|------|------|
| `selectElementById(id)` | 选中元素 |
| `deselect()` | 取消选中 |
| `attachElementTransformById(id)` | 给元素附加变换控件（平移/旋转/缩放） |
| `detachElementTransform()` | 取消变换控件 |
| `addElement(point, properties)` | 添加新元素 |
| `deleteElementById(id)` | 删除元素 |
| `updateElementById(id, point, properties)` | 更新元素属性 |
| `findElementById(id)` | 按 ID 查询元素信息 |

HDMapEdit 事件：`add`（添加元素时触发）、`change`（变换元素时触发）。

### 示例：HDMap3DTiles 基本用法

```javascript
const hdmap = engine.add(new mapvthree.HDMap3DTiles({
    url: 'https://example.com/hdmap/tileset.json',
    errorTarget: 16,
}));

// 设置高精地图专用材质管理器
hdmap.materialManager = new mapvthree.HDMap3DTilesMaterialManager();
```

### 示例：隧道半透明效果

```javascript
hdmap.setGroupMaterial('tunnel', {
    transparent: true,
    opacity: 0.3,
    depthWrite: false,
});

// 重置隧道材质
hdmap.resetGroupMaterial('tunnel');
```

### 示例：可见性控制

```javascript
// 隐藏特定元素
hdmap.visibility.addHiddenId('element-001');

// 隐藏整个图层类型（如网格线）
hdmap.visibility.addHiddenLayer(101); // LANEGRID

// 恢复显示
hdmap.visibility.removeHiddenId('element-001');
```

### 示例：车道级网格线

```javascript
hdmap.grid.enabled = true;
hdmap.grid.apiHost = 'https://your-api-host';

hdmap.grid.addEventListener('click', (e) => {
    console.log('点击网格:', e.value); // GeoJSON Feature
});
```

### 示例：元素编辑

```javascript
hdmap.edit.enabled = true;
hdmap.edit.apiHost = 'https://your-api-host';

// 选中元素
const element = await hdmap.edit.selectElementById('element-001');

// 附加变换控件
await hdmap.edit.attachElementTransformById('element-001');

// 完成编辑
hdmap.edit.detachElementTransform();
```

## TrafficMap3DTiles

实时路况 3D Tiles 加载器，继承自 `Default3DTiles`。每 60 秒自动轮询交通状态数据，基于 batchTable 中的 link ID 查询路况并通过 `TrafficStatusMaterial` 进行着色。

### 构造参数

同 `Default3DTiles`。

### 独有属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `isTrafficMap3DTiles` | boolean | 固定为 `true`，用于类型标识 |
| `apiHost` | string | 路况数据接口地址（修改后立即触发刷新） |

### 示例

```javascript
const traffic = engine.add(new mapvthree.TrafficMap3DTiles({
    url: 'https://example.com/traffic/tileset.json',
    errorTarget: 32,
}));

// 切换路况数据源
traffic.apiHost = 'https://your-traffic-api';
```

## 材质管理器（materialManager）

所有 3D Tiles 类都支持通过 `materialManager` 属性替换材质。设置后会自动刷新所有已加载的瓦片。材质管理器根据 mesh 的原始 `material.name` 匹配材质 key，找不到时尝试匹配 `'*'` 通配符。

### 公共导出的材质管理器

| 类名 | 说明 |
|------|------|
| `Default3DTilesMaterialManager` | 基类，提供材质增删改查和分组管理 |
| `Realistic3DTilesMaterialManager` | 写实风格，内置道路/隔离带/绿化/建筑/水体材质，支持天气和昼夜光照自动切换 |
| `Building3DTilesMaterialManager` | 建筑专用，按纹理 key 自动加载建筑贴图，支持昼夜光照 |
| `Custom3DTilesMaterialManager` | 自定义风格，内置道路/绿化/建筑/水体材质 |
| `Wireframe3DTilesMaterialManager` | 线框模式，所有 mesh 渲染为蓝色线框 |
| `RandomColor3DTilesMaterialManager` | 随机颜色模式，每种材质 key 随机分配颜色 |
| `Identity3DTilesMaterialManager` | 标识材质，用于元素拾取（type=1 按 ID 着色，type=2 按 dataType 着色） |
| `HDMap3DTilesMaterialManager` | 高精地图 V1 材质，使用 RoadMarkingMaterial 通过 styleJSON 颜色精灵图着色 |
| `HDMap3DTilesMaterialManagerV2` | 高精地图 V2 材质，内置路面/绿化/墙体/隧道/建筑/水体等 PBR 材质 |
| `HDRoad3DTilesMaterialManager` | 高清路网材质，内置道路/绿化/车道线材质 |
| `Terrain3DTilesMaterialManager` | 地形分类材质，支持地形分类纹理和水体 |

### Default3DTilesMaterialManager 基类方法

| 方法 | 说明 |
|------|------|
| `getMaterialByKey(key)` | 根据 key 获取材质（找不到时返回 `'*'` 通配材质） |
| `addMaterialByKey(key, material, group)` | 添加材质，可选指定分组 |
| `removeMaterialByKey(key)` | 删除材质 |
| `getMaterialKeysByGroup(groupName)` | 获取分组下所有材质 key |
| `getMaterialsByGroup(groupName)` | 获取分组下所有材质对象 |
| `getGroupNames()` | 获取所有分组名称 |
| `applyGroupMaterial(groupName, properties)` | 批量设置分组内材质属性 |
| `resetGroupMaterial(groupName)` | 重置分组材质到默认状态 |
| `createPbrMaterial(textureName, channels, repeat, params)` | 创建 PBR 材质的便捷方法 |
| `dispose()` | 销毁所有材质和纹理 |

### 示例：使用写实材质管理器

```javascript
const tileset = engine.add(new mapvthree.Default3DTiles({
    url: 'path/to/tileset.json',
}));

tileset.materialManager = new mapvthree.Realistic3DTilesMaterialManager();
```

### 示例：线框模式

```javascript
tileset.materialManager = new mapvthree.Wireframe3DTilesMaterialManager();
```

### 示例：切换回原始材质

```javascript
// 设置 materialManager 为 null 会恢复所有 mesh 的原始材质
tileset.materialManager = null;
```

### 示例：自定义材质管理器

```javascript
import {Default3DTilesMaterialManager} from 'mapvthree';
import {MeshStandardMaterial} from 'three';

class MyMaterialManager extends Default3DTilesMaterialManager {
    onInit() {
        // 按 key 替换特定材质
        this.addMaterialByKey('road', new MeshStandardMaterial({
            color: 0x333333,
            roughness: 0.8,
        }));
        // 使用 '*' 通配符匹配所有未指定的材质
        this.addMaterialByKey('*', new MeshStandardMaterial({
            color: 0x888888,
        }));
    }
}

tileset.materialManager = new MyMaterialManager();
```
