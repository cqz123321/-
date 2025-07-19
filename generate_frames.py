# generate_frames.py

frame_count = 225  # 修改这里为你想要的帧数

# 打印 frames[] 数组
print("const uint16_t* frames[] = {")
for i in range(1, frame_count + 1):
    end = ",\n" if i % 5 == 0 and i != frame_count else ", " if i != frame_count else "\n"
    print(f"  frame{i}", end=end)
print("};\n")

# 打印帧数
print(f"const int numFrames = {frame_count};")
