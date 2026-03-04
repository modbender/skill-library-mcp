# 天空和天气系统

## 概述

MapV Three 提供完整的天空和天气模拟系统，从基础静态天空到动态大气渲染效果。

## 天空类型

| 类型 | 性能 | 效果 | 适用场景 |
|------|------|------|----------|
| `EmptySky` | 最佳 | 仅光照 | 不需要天空背景 |
| `DefaultSky` | 高 | 简单渐变 | 移动端/低性能设备 |
| `StaticSky` | 中 | 静态贴图 | 预设天气效果 |
| `DynamicSky` | 低 | 动态云层 | 桌面应用 |

## 时间系统

所有天空类都支持时间控制（秒，从午夜 00:00 开始）：

```javascript
sky.time = 3600 * 6;      // 早上 6:00
sky.time = 3600 * 14.5;   // 下午 2:30
sky.time = 3600 * 18;     // 晚上 6:00
```

## 天气预设

`clear` | `partlyCloudy` | `cloudy` | `overcast` | `foggy` | `rainy` | `snowy` | `stormy` | `thunderstorm`

## EmptySky

仅提供光照系统，不包含天空背景。

```javascript
const sky = engine.add(new mapvthree.EmptySky({ time: 3600 * 10 }));
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `sunLightIntensity` | 2.2 | 太阳光强度 |
| `skyLightIntensity` | 1.2 | 环境光强度 |
| `skyLightAttenuationRatio` | 0.2 | 环境光衰减比 |
| `envLightIntensity` | 0.2 | 环境贴图强度 |

## DefaultSky

简单渐变效果：

```javascript
const sky = engine.add(new mapvthree.DefaultSky());
sky.color = new THREE.Color(0x87ceeb);
sky.highColor = new THREE.Color(0x67ceeb);
```

## StaticSky

预设天气和时间效果，自动切换预烘焙纹理：

```javascript
const sky = engine.add(new mapvthree.StaticSky());
sky.time = 3600 * 17;
sky.weather = 'cloudy';
```

时间自动分段：night (18:00-06:00)、dusk (17:00-18:00)、afternoon (15:30-17:00)、default (06:00-15:30)。

## DynamicSky

动态大气效果和云层：

```javascript
const sky = engine.add(new mapvthree.DynamicSky());
sky.affectWorld = true;
sky.enableAtmospherePass = true;
sky.enableCloudsPass = true;
sky.cloudsCoverage = 0.6;
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `affectWorld` | boolean | `true` | 影响场景环境反射 |
| `enableAtmospherePass` | boolean | `true` | 大气层后处理 |
| `enableCloudsPass` | boolean | `true` | 体积云渲染 |
| `cloudsCoverage` | number | `0.55` | 云层覆盖率 (0-1) |
| `cloudsSpeed` | number | `1.0` | 云层移动速度 |
| `cloudDensity` | number | `1.0` | 云层密度 (0-1) |
| `cloudShapeBaseScale` | number | `1.0` | 云层形状基础缩放 |
| `cloudShapeDetailScale` | number | `1.0` | 云层形状细节缩放 |
| `cloudMarchSteps` | number | `16` | 云层渲染步进数 |
| `cloudSelfShadowSteps` | number | `5` | 云层自阴影步进数 |

## DynamicWeather

配合 DynamicSky 使用，默认天气为 `partlyCloudy`，默认过渡时间 1000ms：

```javascript
const sky = engine.add(new mapvthree.DynamicSky());
const weather = engine.add(new mapvthree.DynamicWeather(sky));

weather.transitionDuration = 3000;
weather.weather = 'rainy';

weather.addWeatherChangedListener((type) => {
    console.log('天气变为:', type);
});
```

## 完整示例

```javascript
const engine = new mapvthree.Engine(container, {
    rendering: { enableAnimationLoop: true },
    map: { projection: 'ecef' }
});

const sky = engine.add(new mapvthree.DynamicSky());
sky.enableAtmospherePass = true;
sky.enableCloudsPass = true;
sky.cloudsCoverage = 0.3;

const weather = engine.add(new mapvthree.DynamicWeather(sky));
weather.weather = 'partlyCloudy';
```
