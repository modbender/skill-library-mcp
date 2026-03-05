# M5Stack Arduino 编程参考

## 常用设备型号

- M5Stack Core (Basic/Gray/Fire)
- M5StickC/CPlus
- M5Stack Core2
- M5Stack CoreS3
- M5Atom (Matrix/Lite)
- M5Cardputer
- M5Dial
- M5Stamp

## 核心库依赖

```cpp
#include <M5Stack.h>          // 经典Core系列
#include <M5StickC.h>         // M5StickC
#include <M5StickCPlus.h>     // M5StickCPlus
#include <M5Core2.h>          // Core2
#include <M5CoreS3.h>         // CoreS3
#include <M5Atom.h>           // Atom系列
```

## 基础结构

```cpp
#include <M5Stack.h>

void setup() {
  M5.begin();  // 初始化M5Stack
}

void loop() {
  M5.update(); // 更新按键状态
  // 你的代码
}
```

## 常用API

### 屏幕操作
```cpp
M5.Lcd.print("Hello");
M5.Lcd.setCursor(x, y);
M5.Lcd.setTextSize(size);
M5.Lcd.setTextColor(color);
M5.Lcd.fillScreen(color);
```

### 按键操作
```cpp
M5.BtnA.wasPressed()  // A键刚按下
M5.BtnB.wasPressed()  // B键刚按下
M5.BtnC.wasPressed()  // C键刚按下
```

## 查询资源

- GitHub: https://github.com/m5stack
- 官方文档: https://docs.m5stack.com
- 示例库: File -> Examples -> M5Stack
