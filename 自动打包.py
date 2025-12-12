import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import subprocess
import sys
import threading


class AutoPackager:
    def __init__(self, root):
        self.root = root
        self.root.title("Python程序自动打包工具")
        self.root.geometry("500x300")

        self.setup_ui()

    def setup_ui(self):
        # 选择文件区域
        tk.Label(self.root, text="选择要打包的Python文件:", font=("Arial", 12)).pack(pady=10)

        frame1 = tk.Frame(self.root)
        frame1.pack(pady=5)

        self.file_path = tk.StringVar()
        tk.Entry(frame1, textvariable=self.file_path, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(frame1, text="浏览", command=self.browse_file).pack(side=tk.LEFT, padx=5)

        # 选项区域
        frame2 = tk.Frame(self.root)
        frame2.pack(pady=10)

        self.onefile = tk.BooleanVar(value=True)
        tk.Checkbutton(frame2, text="打包成单个文件", variable=self.onefile).pack(side=tk.LEFT, padx=10)

        self.windowed = tk.BooleanVar(value=False)
        tk.Checkbutton(frame2, text="隐藏控制台窗口", variable=self.windowed).pack(side=tk.LEFT, padx=10)

        # 进度条
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=20, pady=10)

        # 打包按钮
        tk.Button(self.root, text="开始打包", command=self.start_packaging,
                  bg="green", fg="white", font=("Arial", 12), height=2).pack(pady=20)

        # 状态显示
        self.status = tk.StringVar(value="准备就绪")
        tk.Label(self.root, textvariable=self.status, fg="blue").pack()

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="选择Python文件",
            filetypes=[("Python文件", "*.py"), ("所有文件", "*.*")]
        )
        if filename:
            self.file_path.set(filename)

    def packaging_thread(self):
        try:
            self.status.set("正在检查PyInstaller...")
            # 检查并安装pyinstaller
            try:
                import pyinstaller
            except ImportError:
                self.status.set("正在安装PyInstaller...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            file_path = self.file_path.get()
            if not os.path.exists(file_path):
                messagebox.showerror("错误", "文件不存在！")
                return

            # 构建打包命令
            cmd = "pyinstaller"
            if self.onefile.get():
                cmd += " --onefile"
            if self.windowed.get():
                cmd += " --windowed"
            cmd += " --clean"
            cmd += f' "{file_path}"'

            self.status.set("正在打包，请稍候...")

            # 执行打包
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                self.status.set("✅ 打包完成！")
                messagebox.showinfo("成功",
                                    f"打包完成！\nEXE文件位置: {os.path.join('../24节课学完python/dist', os.path.basename(file_path).replace('.py', '.exe'))}")
            else:
                self.status.set("❌ 打包失败")
                messagebox.showerror("错误", f"打包失败:\n{result.stderr}")

        except Exception as e:
            self.status.set("❌ 发生错误")
            messagebox.showerror("错误", f"发生错误:\n{str(e)}")
        finally:
            self.progress.stop()
            self.root.config(cursor="")

    def start_packaging(self):
        if not self.file_path.get():
            messagebox.showwarning("警告", "请先选择要打包的Python文件！")
            return

        self.progress.start(10)
        self.root.config(cursor="watch")
        self.status.set("开始打包...")

        # 在新线程中执行打包，避免界面卡死
        thread = threading.Thread(target=self.packaging_thread)
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoPackager(root)
    root.mainloop()