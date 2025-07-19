````markdown
# PixelEditor — “坤哥”特别版

> “蔡徐坤剪影！无敌就完了”

---

## 🎉 项目简介

- **PixelEditor**：一款基于 Tkinter + PIL 的简易像素编辑器，专门用来把图像／GIF 压缩成黑白像素矩阵。
- **牛逼之处**：要把“坤哥”的剪影投射到 Arduino 驱动的 LED 灯泡上闪烁！
---

## ⚙️ 环境与依赖

1. **Python 3.6+**  
2. **Tkinter**（Python 自带，一般无需额外安装）  
3. **Pillow**  
   ```bash
   pip install pillow
````

4. **Arduino IDE**
5. **硬件**

   * Arduino 开发板（Uno、Nano 均可）
   * LED 矩阵 / LED 灯泡模块（一行 8～12 像素最佳）

---

## 🚀 快速上手

1. **启动像素编辑器**

   ```bash
   python pixel_editor.py
   ```

2. **载入蔡徐坤剪影**

   * 点击 “Load Image/GIF”，选中你下载好的“蔡徐坤剪影.gif”
   * 程序会把它拆成多帧灰度图，并自动调整到当前网格尺寸（默认 8×12）

3. **调整网格与阈值**

   * **Width / Height**：改成你灯泡实际 LED 数量（如 8×12、16×16 都行）
   * **Threshold 滑块**：左右拖动，直到预览中“蔡徐坤”的轮廓最清晰

4. **生成像素矩阵**

   * 单帧导出：点击 **Generate Matrix**，会在下方文本框输出 C 风格数组
   * 多帧导出：点击 **Export All Frames**，把所有动图帧都导出来，方便做动画！
  
4. **复制矩阵**
   *  打开 `FrameData.cpp` 并复制第四步 生成的frame data 复制进去

---

## 🐍 generate\_frames.py 脚本说明

为了方便在 Arduino 端一次性管理所有帧，我们提供了一个小脚本 `generate_frames.py`，它会根据你导出的各帧数组，生成：

1. **帧指针数组**

   ```cpp
   const uint16_t* frames[] = {
     frame1, frame2, frame3, /* … */, frameN
   };
   ```
2. **帧总数常量**

   ```cpp
   const int numFrames = N;
   ```

### 使用方法

1. 修改脚本开头的 `frame_count`，设为你的总帧数（比如 225）：

   ```python
   frame_count = 225  # 修改这里为你想要的帧数
   ```

2. 打开生成的 `FrameData.cpp`，会看到类似：

   ```cpp
   // 将所有帧的首地址放进数组中
   const uint16_t* frames[] = {
     frame1,   frame2,   …,   frame225
   };

   const int numFrames = 225;
   ```
3. 烧录进arduino 即可直接循环播放。

---



## 😆 致谢与彩蛋

谢谢chatgpt


