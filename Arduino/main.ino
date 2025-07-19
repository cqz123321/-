#include "AnimationDisplay.h"
#include "FrameData.h"

void setup() {
  beginDisplay();           // 初始化 LED 矩阵
}

void loop() {
  // 遍历所有帧进行播放
  for (int i = 0; i < numFrames; i++) {
    drawFrame(frames[i]);   // 绘制当前帧
    delay(65);              // 帧间延时，可根据需求调整
  }
}
