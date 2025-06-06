"""
GUI组件和工具类
"""

import tkinter as tk
import customtkinter as ctk
from typing import Callable, Optional
from .styles import COLORS, FONTS, BUTTON_STYLES
import threading
import time


class StatusCard(ctk.CTkFrame):
    """状态卡片组件"""

    def __init__(self, parent, title: str, **kwargs):
        super().__init__(parent, **kwargs)

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=FONTS['subtitle'],
            text_color=COLORS['text_primary']
        )
        self.title_label.pack(pady=(8, 4), padx=15, anchor="w")

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 8))
    
    def add_info_row(self, label: str, value: str, value_color: str = None):
        """添加信息行"""
        row_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)
        
        label_widget = ctk.CTkLabel(
            row_frame, 
            text=f"{label}:", 
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        label_widget.pack(side="left")
        
        value_widget = ctk.CTkLabel(
            row_frame, 
            text=value, 
            font=FONTS['code'],
            text_color=value_color or COLORS['text_primary']
        )
        value_widget.pack(side="right")
        
        return value_widget


class ProgressCard(ctk.CTkFrame):
    """进度卡片组件"""

    def __init__(self, parent, title: str, **kwargs):
        super().__init__(parent, **kwargs)

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=FONTS['subtitle'],
            text_color=COLORS['text_primary']
        )
        self.title_label.pack(pady=(12, 8), padx=15)

        self.progress_bar = ctk.CTkProgressBar(self, width=280)
        self.progress_bar.pack(pady=8, padx=15)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            self,
            text="准备就绪",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        self.status_label.pack(pady=(0, 12), padx=15)
    
    def update_progress(self, value: float, status: str = None):
        """更新进度"""
        self.progress_bar.set(value)
        if status:
            self.status_label.configure(text=status)
    
    def reset(self):
        """重置进度"""
        self.progress_bar.set(0)
        self.status_label.configure(text="准备就绪")


class LogTextBox(ctk.CTkTextbox):
    """日志文本框组件"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(
            font=FONTS['code'],
            wrap="word",
            state="disabled"
        )
    
    def append_log(self, message: str, level: str = "INFO"):
        """添加日志消息"""
        self.configure(state="normal")
        
        # 添加时间戳
        timestamp = time.strftime("%H:%M:%S")
        
        # 根据日志级别设置颜色
        color_map = {
            "INFO": COLORS['text_primary'],
            "SUCCESS": "#4CAF50",
            "WARNING": "#FF9800",
            "ERROR": "#F44336"
        }
        
        # 插入日志消息
        log_line = f"[{timestamp}] [{level}] {message}\n"
        self.insert("end", log_line)
        
        # 自动滚动到底部
        self.see("end")
        
        self.configure(state="disabled")
    
    def clear_log(self):
        """清空日志"""
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")


class ActionButton(ctk.CTkButton):
    """操作按钮组件"""

    def __init__(self, parent, text: str, command: Callable, style: str = "primary", **kwargs):
        button_config = BUTTON_STYLES.get(style, BUTTON_STYLES['primary']).copy()
        button_config.update(kwargs)

        super().__init__(parent, text=text, command=command, **button_config)

        self.original_command = command
        self.original_text = text  # 保存原始文本
        self.is_processing = False

    def set_processing(self, processing: bool, text: str = None):
        """设置处理状态"""
        self.is_processing = processing
        if processing:
            self.configure(state="disabled", text=text or "处理中...")
        else:
            # 恢复到原始状态
            self.configure(state="normal", text=self.original_text)


class ThreadedOperation:
    """线程化操作类"""
    
    def __init__(self, target_func: Callable, success_callback: Callable = None, 
                 error_callback: Callable = None, progress_callback: Callable = None):
        self.target_func = target_func
        self.success_callback = success_callback
        self.error_callback = error_callback
        self.progress_callback = progress_callback
        self.thread = None
    
    def start(self, *args, **kwargs):
        """启动线程操作"""
        if self.thread and self.thread.is_alive():
            return False
        
        self.thread = threading.Thread(
            target=self._run_operation, 
            args=args, 
            kwargs=kwargs,
            daemon=True
        )
        self.thread.start()
        return True
    
    def _run_operation(self, *args, **kwargs):
        """运行操作"""
        try:
            if self.progress_callback:
                self.progress_callback(0.1, "开始操作...")
            
            result = self.target_func(*args, **kwargs)
            
            if self.progress_callback:
                self.progress_callback(1.0, "操作完成")
            
            if self.success_callback:
                self.success_callback(result)
                
        except Exception as e:
            if self.error_callback:
                self.error_callback(e)
    
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self.thread and self.thread.is_alive()
