#ifndef ANIMATION_DISPLAY_H
#define ANIMATION_DISPLAY_H

#include "ArduinoGraphics.h"
#include "Arduino_LED_Matrix.h"

// 声明一个全局矩阵对象（或根据项目需要采用其他组织方式）
extern ArduinoLEDMatrix matrix;

// 声明显示函数
void drawFrame(const uint16_t* frame);
void beginDisplay();

#endif  // ANIMATION_DISPLAY_H
