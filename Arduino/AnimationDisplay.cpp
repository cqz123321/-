#include "AnimationDisplay.h"

ArduinoLEDMatrix matrix;  // 全局矩阵实例

void drawFrame(const uint16_t* frame) {
  matrix.beginDraw();
  matrix.clear();
  matrix.stroke(255);

  // 遍历行和列，注意这里采用 (y,x) 坐标，请确保它与你的硬件相匹配
  for (int y = 0; y < 12; y++) {       // 12 行
    for (int x = 0; x < 8; x++) {        // 8 列
      if (frame[y] & (1 << (7 - x))) {   // 判断当前行从左到右的位是否需要点亮
        matrix.point(y, x);              // 这里用 (y, x) 顺序，如有需要可调整成 (x, y)
      }
    }
  }

  matrix.endDraw();
}

void beginDisplay() {
  matrix.begin();
}
