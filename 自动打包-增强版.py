import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import subprocess
import sys
import threading
import tempfile
import shutil


class AutoPackager:
    def __init__(self, root):
        self.root = root
        self.root.title("Python程序自动打包工具 - 增强版")
        self.root.geometry("600x450")

        self.setup_ui()

    def setup_ui(self):
        # 选择文件区域
        tk.Label(self.root, text="选择要打包的Python文件:", font=("Arial", 12)).pack(pady=10)

        frame1 = tk.Frame(self.root)
        frame1.pack(pady=5, fill=tk.X, padx=20)

        self.file_path = tk.StringVar()
        tk.Entry(frame1, textvariable=self.file_path, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(frame1, text="浏览", command=self.browse_file).pack(side=tk.LEFT, padx=5)

        # 选项区域
        options_frame = tk.LabelFrame(self.root, text="打包选项", padx=10, pady=10)
        options_frame.pack(pady=10, fill=tk.X, padx=20)

        self.onefile = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="打包成单个文件", variable=self.onefile).grid(row=0, column=0, sticky=tk.W,
                                                                                         padx=5)

        self.windowed = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="隐藏控制台窗口", variable=self.windowed).grid(row=0, column=1, sticky=tk.W,
                                                                                          padx=5)

        self.clean = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="清理临时文件", variable=self.clean).grid(row=1, column=0, sticky=tk.W,
                                                                                     padx=5)

        self.include_mediapipe = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="包含MediaPipe支持", variable=self.include_mediapipe).grid(row=1, column=1,
                                                                                                      sticky=tk.W,
                                                                                                      padx=5)

        # 高级选项
        advanced_frame = tk.LabelFrame(self.root, text="高级选项", padx=10, pady=10)
        advanced_frame.pack(pady=10, fill=tk.X, padx=20)

        tk.Label(advanced_frame, text="额外隐藏导入:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.hidden_imports = tk.StringVar(value="cv2, mediapipe, numpy, logging")
        tk.Entry(advanced_frame, textvariable=self.hidden_imports, width=50).grid(row=0, column=1, padx=5,
                                                                                  sticky=tk.W + tk.E)

        tk.Label(advanced_frame, text="额外参数:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.extra_args = tk.StringVar(value="--collect-all mediapipe")
        tk.Entry(advanced_frame, textvariable=self.extra_args, width=50).grid(row=1, column=1, padx=5,
                                                                              sticky=tk.W + tk.E)

        advanced_frame.columnconfigure(1, weight=1)

        # 进度条
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=20, pady=10)

        # 打包按钮
        tk.Button(self.root, text="开始打包", command=self.start_packaging,
                  bg="green", fg="white", font=("Arial", 12), height=2).pack(pady=20)

        # 状态显示
        self.status = tk.StringVar(value="准备就绪")
        status_label = tk.Label(self.root, textvariable=self.status, fg="blue", wraplength=550)
        status_label.pack()

        # 日志区域
        log_frame = tk.LabelFrame(self.root, text="打包日志", padx=10, pady=10)
        log_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)

        self.log_text = tk.Text(log_frame, height=8, width=70)
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="选择Python文件",
            filetypes=[("Python文件", "*.py"), ("所有文件", "*.*")]
        )
        if filename:
            self.file_path.set(filename)

    def log_message(self, message):
        """添加日志消息"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def packaging_thread(self):
        try:
            self.log_message("=== 开始打包过程 ===")

            # 检查并安装pyinstaller
            self.status.set("正在检查PyInstaller...")
            self.log_message("检查PyInstaller安装...")
            try:
                import pyinstaller
                self.log_message("PyInstaller已安装")
            except ImportError:
                self.status.set("正在安装PyInstaller...")
                self.log_message("正在安装PyInstaller...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.log_message("PyInstaller安装完成")

            file_path = self.file_path.get()
            if not os.path.exists(file_path):
                messagebox.showerror("错误", "文件不存在！")
                return

            # 获取文件所在目录
            file_dir = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            exe_name = file_name.replace('.py', '.exe')

            # 创建临时工作目录
            temp_dir = tempfile.mkdtemp()
            self.log_message(f"创建临时目录: {temp_dir}")

            # 构建打包命令
            cmd = ["pyinstaller"]

            if self.onefile.get():
                cmd.append("--onefile")
                self.log_message("启用单文件模式")

            if self.windowed.get():
                cmd.append("--windowed")
                self.log_message("启用无控制台窗口模式")
            else:
                cmd.append("--console")
                self.log_message("启用控制台窗口模式（推荐用于调试）")

            if self.clean.get():
                cmd.append("--clean")
                self.log_message("启用清理模式")

            # 添加隐藏导入
            hidden_imports = self.hidden_imports.get().split(',')
            for imp in hidden_imports:
                imp = imp.strip()
                if imp:
                    cmd.extend(["--hidden-import", imp])
                    self.log_message(f"添加隐藏导入: {imp}")

            # 添加mediapipe特殊处理
            if self.include_mediapipe.get():
                cmd.append("--collect-all")
                cmd.append("mediapipe")
                self.log_message("添加MediaPipe完整支持")

            # 添加额外参数
            extra_args = self.extra_args.get().strip()
            if extra_args:
                cmd.extend(extra_args.split())
                self.log_message(f"添加额外参数: {extra_args}")

            # 添加工作目录和spec文件路径
            cmd.extend(["--workpath", os.path.join(temp_dir, "build")])
            cmd.extend(["--specpath", temp_dir])
            cmd.extend(["--distpath", os.path.join(file_dir, "dist")])

            cmd.append(file_path)

            self.log_message(f"完整打包命令: {' '.join(cmd)}")
            self.status.set("正在打包，请稍候...")

            # 执行打包
            self.log_message("开始执行打包命令...")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=file_dir)

            # 输出详细信息
            if result.stdout:
                self.log_message("标准输出:")
                self.log_message(result.stdout)

            if result.stderr:
                self.log_message("错误输出:")
                self.log_message(result.stderr)

            exe_path = os.path.join(file_dir, "dist", exe_name)

            if result.returncode == 0 and os.path.exists(exe_path):
                self.status.set("✅ 打包完成！")
                self.log_message(f"✅ 打包成功！EXE文件位置: {exe_path}")
                self.log_message(f"EXE文件大小: {os.path.getsize(exe_path) / (1024 * 1024):.2f} MB")

                # 询问是否打开输出目录
                if messagebox.askyesno("成功", f"打包完成！\nEXE文件位置: {exe_path}\n\n是否打开输出目录？"):
                    os.startfile(os.path.join(file_dir, "dist"))
            else:
                self.status.set("❌ 打包失败")
                self.log_message("❌ 打包失败")
                if not os.path.exists(exe_path):
                    self.log_message("错误: 目标EXE文件未生成")
                messagebox.showerror("错误", f"打包失败，请查看日志了解详细信息")

            # 清理临时文件
            if self.clean.get() and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                self.log_message("已清理临时文件")

        except Exception as e:
            self.status.set("❌ 发生错误")
            self.log_message(f"❌ 发生错误: {str(e)}")
            import traceback
            self.log_message(traceback.format_exc())
            messagebox.showerror("错误", f"发生错误:\n{str(e)}\n\n请查看日志了解详细信息")
        finally:
            self.progress.stop()
            self.root.config(cursor="")
            self.log_message("=== 打包过程结束 ===")

    def start_packaging(self):
        if not self.file_path.get():
            messagebox.showwarning("警告", "请先选择要打包的Python文件！")
            return

        # 清空日志
        self.log_text.delete(1.0, tk.END)

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