import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageSequence, ImageTk

class PixelEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Pixel Editor (修复版)")

        # 基础参数
        self.pixel_size = 20
        self.grid_width = 8
        self.grid_height = 12
        self.last_valid_width = self.grid_width
        self.last_valid_height = self.grid_height

        # 数据结构
        self.pixels = []              # Tk 网格 rectangle id
        self.frames = []              # 已 resize 的 PIL 灰度帧 (mode 'L')
        self.original_frames = []     # 原始尺寸（可选保留，用于重新 resize）
        self.frame_index = 0
        self.threshold = 128

        # 动画控制
        self.is_playing = False
        self.play_interval = 80  # 毫秒，可自行调节
        self.animation_job = None

        # --- 主画布 ---
        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=4)

        # --- 阈值后预览 ---
        self.preview_label = tk.Label(root, bg="white")
        self.preview_label.grid(row=0, column=4, rowspan=6, sticky="nw", padx=10)
        self.preview_image_tk = None

        # --- 原图预览 ---
        self.original_preview_label = tk.Label(root, bg="white")
        self.original_preview_label.grid(row=0, column=5, rowspan=6, sticky="nw", padx=10)
        self.original_preview_image_tk = None

        # --- 尺寸输入 ---
        tk.Label(root, text="Width:").grid(row=1, column=0)
        self.width_entry = tk.Entry(root, width=5)
        self.width_entry.insert(0, str(self.grid_width))
        self.width_entry.grid(row=1, column=1)

        tk.Label(root, text="Height:").grid(row=1, column=2)
        self.height_entry = tk.Entry(root, width=5)
        self.height_entry.insert(0, str(self.grid_height))
        self.height_entry.grid(row=1, column=3)

        # --- 按钮: 载入 / 生成网格 ---
        tk.Button(root, text="Load Image/GIF", command=self.load_image).grid(row=2, column=0, columnspan=2, sticky='ew')
        tk.Button(root, text="Generate Grid", command=self.on_generate_grid_clicked).grid(row=2, column=2, columnspan=2, sticky='ew')

        # --- 生成矩阵 & 阈值 ---
        tk.Button(root, text="Generate Matrix", command=self.export_matrix).grid(row=3, column=0, columnspan=2, sticky='ew')
        self.threshold_slider = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL,
                                         label="Threshold", command=self.update_threshold)
        self.threshold_slider.set(self.threshold)
        self.threshold_slider.grid(row=3, column=2, columnspan=2, sticky='ew')

        # --- 帧滑块 ---
        self.frame_slider = tk.Scale(root, from_=0, to=0, orient=tk.HORIZONTAL,
                                     label="Frame", command=self.set_frame)
        self.frame_slider.grid(row=4, column=0, columnspan=4, sticky="ew")

        # --- 输出框 ---
        self.output = tk.Text(root, height=12, width=70)
        self.output.grid(row=5, column=0, columnspan=6, pady=10)

        # --- 动画控制按钮 ---
        tk.Button(root, text="Play Preview", command=self.start_animation).grid(row=6, column=0, columnspan=2, sticky='ew')
        tk.Button(root, text="Stop Preview", command=self.stop_animation).grid(row=6, column=2, columnspan=2, sticky='ew')
        tk.Button(root, text="Export All Frames", command=self.export_all_frames).grid(row=6, column=4, columnspan=2, sticky='ew')

        # 初始化网格
        self.generate_grid()

    # ------------------ 尺寸与网格 ------------------
    def validate_dimensions(self):
        """读取输入框，如果非法则恢复上一次有效值。"""
        w_text = self.width_entry.get().strip()
        h_text = self.height_entry.get().strip()
        if not w_text or not h_text or not w_text.isdigit() or not h_text.isdigit():
            # 还原显示
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(self.last_valid_width))
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(self.last_valid_height))
            return self.last_valid_width, self.last_valid_height
        w = int(w_text)
        h = int(h_text)
        if w <= 0 or h <= 0:
            messagebox.showerror("Error", "Width/Height must be > 0")
            return self.last_valid_width, self.last_valid_height
        self.last_valid_width, self.last_valid_height = w, h
        return w, h

    def generate_grid(self):
        self.grid_width, self.grid_height = self.validate_dimensions()
        canvas_width = self.grid_width * self.pixel_size
        canvas_height = self.grid_height * self.pixel_size
        self.canvas.config(width=canvas_width, height=canvas_height)

        self.canvas.delete('all')
        self.pixels = []
        for y in range(self.grid_height):
            row = []
            for x in range(self.grid_width):
                x1 = x * self.pixel_size
                y1 = y * self.pixel_size
                rect = self.canvas.create_rectangle(
                    x1, y1, x1 + self.pixel_size, y1 + self.pixel_size,
                    fill='white', outline='gray'
                )
                self.canvas.tag_bind(rect, '<Button-1>', lambda e, r=rect: self.toggle_pixel(r))
                row.append(rect)
            self.pixels.append(row)

    def on_generate_grid_clicked(self):
        # 改变尺寸后重新生成网格，并（如果有帧）对所有帧重新 resize
        old_size = (self.grid_width, self.grid_height)
        self.generate_grid()
        new_size = (self.grid_width, self.grid_height)
        if self.frames and new_size != old_size:
            self.frames = [f.resize(new_size, Image.NEAREST) for f in self.frames]
            # 如果保留原始帧，可从 original_frames 再次 resize
        self.apply_frame()  # 重新渲染（如果有帧）

    def toggle_pixel(self, rect):
        color = self.canvas.itemcget(rect, 'fill')
        self.canvas.itemconfig(rect, fill='black' if color == 'white' else 'white')

    # ------------------ 图像载入与处理 ------------------
    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if not path:
            return
        try:
            img = Image.open(path)
        except Exception as e:
            messagebox.showerror("Error", f"无法打开图片: {e}")
            return

        # 提取所有帧 (对静态图也会产生单帧)
        frames_raw = [frame.copy() for frame in ImageSequence.Iterator(img)]
        if not frames_raw:
            frames_raw = [img]

        # 转成灰度并 resize 到当前网格尺寸
        target_size = (self.grid_width, self.grid_height)
        self.original_frames = [fr.convert('RGBA') for fr in frames_raw]  # 可保留
        self.frames = [fr.convert('L').resize(target_size, Image.NEAREST) for fr in self.original_frames]

        self.frame_index = 0
        self.frame_slider.config(to=len(self.frames) - 1)

        self.apply_frame()

    def update_threshold(self, val):
        self.threshold = int(val)
        self.apply_frame()

    def set_frame(self, val):
        if not self.frames:
            return
        self.frame_index = int(val)
        self.apply_frame()

    # ------------------ 渲染与预览 ------------------
    def apply_frame(self):
        if not self.frames:
            return
        frame = self.frames[self.frame_index]
        fw, fh = frame.size
        # 防御：如果尺寸不一致（极少数情况），临时 resize
        if (fw, fh) != (self.grid_width, self.grid_height):
            frame = frame.resize((self.grid_width, self.grid_height), Image.NEAREST)

        pixels = frame.load()
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                self.canvas.itemconfig(
                    self.pixels[y][x],
                    fill='black' if pixels[x, y] < self.threshold else 'white'
                )
        # 预览
        threshold_img = self.create_threshold_preview(frame)
        self.show_preview_frame(threshold_img)
        self.show_original_frame(frame)

    def create_threshold_preview(self, frame_img):
        # 生成黑白阈值图 (RGB)
        bw = Image.new('RGB', frame_img.size, (255, 255, 255))
        px_src = frame_img.load()
        px_bw = bw.load()
        w, h = frame_img.size
        th = self.threshold
        for y in range(h):
            for x in range(w):
                px_bw[x, y] = (0, 0, 0) if px_src[x, y] < th else (255, 255, 255)
        return bw

    def show_preview_frame(self, pil_image):
        # 放大预览，可调尺寸
        preview = pil_image.resize((160, 160), Image.NEAREST)
        self.preview_image_tk = ImageTk.PhotoImage(preview)
        self.preview_label.config(image=self.preview_image_tk)

    def show_original_frame(self, pil_image):
        original_preview = pil_image.resize((160, 160), Image.NEAREST)
        self.original_preview_image_tk = ImageTk.PhotoImage(original_preview)
        self.original_preview_label.config(image=self.original_preview_image_tk)

    # ------------------ 导出功能 ------------------
    def choose_ctype(self):
        w = self.grid_width
        if w <= 8:
            return 'uint8_t'
        elif w <= 16:
            return 'uint16_t'
        elif w <= 32:
            return 'uint32_t'
        elif w <= 64:
            return 'uint64_t'
        else:
            # 超过64可以分段，暂时直接返回数组 of uint64_t 警告
            return 'uint64_t'

    def export_matrix(self):
        self.output.delete('1.0', tk.END)
        ctype = self.choose_ctype()
        lines = []
        for y in range(self.grid_height):
            bits = ''.join('1' if self.canvas.itemcget(self.pixels[y][x], 'fill') == 'black' else '0'
                           for x in range(self.grid_width))
            lines.append(f"0b{bits}")
        arr = "const {ctype} frame[{self.grid_height}] = {{\n  " + ",\n  ".join(lines) + "\n};"  # noqa
        self.output.insert(tk.END, arr)

    def export_all_frames(self):
        if not self.frames:
            self.output.delete('1.0', tk.END)
            self.output.insert(tk.END, '// No frames loaded')
            return
        self.output.delete('1.0', tk.END)
        ctype = self.choose_ctype()
        blocks = []
        th = self.threshold
        for idx, frm in enumerate(self.frames):
            px = frm.load()
            w, h = frm.size
            lines = []
            for y in range(h):
                bits = ''.join('1' if px[x, y] < th else '0' for x in range(w))
                lines.append(f"0b{bits}")
            block = f"const {ctype} frame{idx}[] = {{\n  " + ",\n  ".join(lines) + "\n};"  # noqa
            blocks.append(block)
        blocks.append(f"// total frames: {len(self.frames)}  width: {self.grid_width}  height: {self.grid_height}\n")
        self.output.insert(tk.END, "\n\n".join(blocks))

    # ------------------ 动画 ------------------
    def animate_next_frame(self):
        if not self.frames or not self.is_playing:
            return
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        # 设置 slider 会自动调用 set_frame -> apply_frame
        self.frame_slider.set(self.frame_index)
        self.animation_job = self.root.after(self.play_interval, self.animate_next_frame)

    def start_animation(self):
        if not self.frames:
            return
        if not self.is_playing:
            self.is_playing = True
            self.animate_next_frame()

    def stop_animation(self):
        if self.is_playing:
            self.is_playing = False
            if self.animation_job:
                self.root.after_cancel(self.animation_job)
                self.animation_job = None

    # ------------------ 退出清理 ------------------
    def cleanup(self):
        self.stop_animation()


if __name__ == '__main__':
    root = tk.Tk()
    app = PixelEditor(root)
    def on_close():
        app.cleanup()
        root.destroy()
    root.protocol('WM_DELETE_WINDOW', on_close)
    root.mainloop()
