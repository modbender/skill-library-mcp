# ClusterPoint 点聚合

基于 Supercluster 算法的点聚合组件，根据缩放级别自动合并临近点。适用于大量 POI 点的展示。

## 基础用法

```javascript
const cluster = engine.add(new mapvthree.ClusterPoint({
    cluster: {
        radius: 80,
        maxZoom: 18,
        minZoom: 5,
    },
    icon: {
        width: 40,
        height: 40,
        mapSrc: 'assets/icons/cluster.png',
    },
    label: {
        fontSize: 14,
        fillStyle: '#ffffff',
    }
}));

cluster.dataSource = mapvthree.GeoJSONDataSource.fromGeoJSON({
    type: 'FeatureCollection',
    features: [
        {
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [116.404, 39.915] },
            properties: { name: '点位1' }
        }
    ]
});
```

## 构造参数

### 聚合配置（cluster）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `radius` | number | `50` | 聚合半径（像素） |
| `maxZoom` | number | `18` | 最大聚合级别 |
| `minZoom` | number | `5` | 最小聚合级别 |

### 图标配置（icon）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `width` | number | `30` | 宽度（像素） |
| `height` | number | `30` | 高度（像素） |
| `mapSrc` | string | - | 图标 URL |

> icon 配置会创建内置 Icon 子组件，更多参数见 Icon 组件。

### 标签配置（label）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `fillStyle` | string | `'#ccc'` | 文字颜色 |
| `fontSize` | number | `16` | 字号 |
| `flat` | boolean | `false` | 贴地显示 |

> label 配置会创建内置 TwinLabel 子组件。

## 主要属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `dataSource` | GeoJSONDataSource | 设置源数据 |
| `clusterDataSource` | GeoJSONDataSource | 聚合后数据源（只读） |
| `clusterData` | Array | 当前聚合结果（只读） |
| `minUpdateInterval` | number | 更新间隔（默认 300ms，最小 16ms） |

## 聚合数据结构

聚合后的数据自动包含 `cluster`、`cluster_id`、`point_count` 属性：

```javascript
// 聚合点
{
    properties: {
        cluster: true,
        cluster_id: 1,
        point_count: 10,
        point_count_abbreviated: '10'
    }
}

// 非聚合点（保留原始 properties）
{
    properties: { name: '点位名称' }
}
```

## 自定义聚合组件

可通过 `addComponent` 添加自定义子组件替代内置 icon/label：

```javascript
const cluster = engine.add(new mapvthree.ClusterPoint({
    cluster: { radius: 100 }
}));

// 添加自定义 Icon 子组件
const icon = new mapvthree.Icon({ vertexIcons: true, width: 40, height: 40 });
cluster.addComponent(icon);

// 通过 clusterDataSource 设置属性映射
cluster.clusterDataSource.defineAttribute('icon', (item) => {
    if (item.properties.cluster) {
        return 'assets/icons/cluster.png';
    }
    return item.properties.icon || 'assets/icons/marker.png';
});

cluster.clusterDataSource.defineAttribute('text', (item) => {
    return item.properties.cluster
        ? item.properties.point_count.toString()
        : item.properties.name || '';
});
```

## 点击展开

```javascript
cluster.addEventListener('click', (e) => {
    const item = e.entity.value;
    if (item.properties.cluster) {
        engine.flyTo({
            center: item.geometry.coordinates,
            range: 5000,
        });
    }
});
```

## 示例：设备状态聚合

```javascript
const deviceCluster = engine.add(new mapvthree.ClusterPoint({
    cluster: { radius: 100 }
}));

const icon = new mapvthree.Icon({ vertexIcons: true, width: 32, height: 32 });
deviceCluster.addComponent(icon);

deviceCluster.clusterDataSource.defineAttribute('icon', (item) => {
    if (item.properties.cluster) return 'assets/icons/device_cluster.png';
    const icons = {
        online: 'device_online.png',
        offline: 'device_offline.png',
        alarm: 'device_alarm.png'
    };
    return `assets/icons/${icons[item.properties.status] || 'device_unknown.png'}`;
});
```
