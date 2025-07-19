#ifndef FRAME_DATA_H
#define FRAME_DATA_H

#include <stdint.h>

// 假设最大帧数（依据内存和实际需求调整）
#define MAX_FRAMES 500

// 声明帧数据数组（这里每帧为12行，每行8个二进制位，存于 uint16_t 类型中）
extern const uint16_t* frames[MAX_FRAMES];
// 当前帧数（自动生成后有效）
extern const int numFrames;

// 通过指定帧数来自动生成动画帧数据
void generateFrames(uint16_t inputFrameCount);

#endif  // FRAME_DATA_H

