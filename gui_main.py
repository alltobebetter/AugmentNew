#!/usr/bin/env python3
"""
AugmentNew GUI版本主程序入口
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """检查依赖项"""
    try:
        import customtkinter
        return True
    except ImportError:
        return False

def install_dependencies():
    """安装依赖项"""
    try:
        import subprocess
        import sys
        
        # 安装customtkinter
        subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter>=5.2.0"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow>=10.0.0"])
        
        return True
    except Exception as e:
        print(f"安装依赖失败: {e}")
        return False

def main():
    """主函数"""
    # 检查依赖项
    if not check_dependencies():
        print("检测到缺少必要的依赖项...")
        
        # 创建一个简单的tkinter窗口询问是否安装
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        result = messagebox.askyesno(
            "缺少依赖项",
            "程序需要安装以下依赖项才能运行：\n\n"
            "- customtkinter (现代化GUI库)\n"
            "- pillow (图像处理库)\n\n"
            "是否现在自动安装？\n\n"
            "注意：需要网络连接"
        )
        
        root.destroy()
        
        if result:
            print("正在安装依赖项...")
            if install_dependencies():
                print("依赖项安装成功！")
                messagebox.showinfo("安装完成", "依赖项安装成功！\n程序将重新启动。")
                
                # 重新启动程序
                import subprocess
                subprocess.Popen([sys.executable] + sys.argv)
                sys.exit(0)
            else:
                messagebox.showerror(
                    "安装失败", 
                    "依赖项安装失败！\n\n"
                    "请手动运行以下命令安装：\n"
                    "pip install customtkinter pillow"
                )
                sys.exit(1)
        else:
            print("用户取消安装，程序退出")
            sys.exit(1)
    
    try:
        # 导入GUI模块
        from gui.main_window import MainWindow
        
        # 创建并运行主窗口
        app = MainWindow()
        app.mainloop()
        
    except Exception as e:
        # 如果GUI启动失败，显示错误信息
        root = tk.Tk()
        root.withdraw()
        
        messagebox.showerror(
            "启动失败",
            f"GUI启动失败：\n\n{str(e)}\n\n"
            "请检查是否正确安装了所有依赖项。"
        )
        
        print(f"GUI启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
