"""
主GUI窗口类
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import os
import sys
import threading

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.paths import (
    get_home_dir, get_app_data_dir, get_storage_path,
    get_db_path, get_machine_id_path, get_workspace_storage_path
)
from utils.version_checker import check_for_updates, get_current_version, get_update_url
from augutils.json_modifier import modify_telemetry_ids
from augutils.sqlite_modifier import clean_augment_data
from augutils.workspace_cleaner import clean_workspace_storage
from augutils.backup_cleaner import find_backup_files, clean_all_backups

from .styles import COLORS, FONTS, SIZES
from .components import StatusCard, ProgressCard, LogTextBox, ActionButton, ThreadedOperation


class MainWindow(ctk.CTk):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 窗口配置
        self.title("AugmentNew")
        self.geometry(f"{SIZES['window_width']}x{SIZES['window_height']}")
        self.resizable(True, True)

        # 初始化变量
        self.current_operation = None
        self.update_available = False
        self.latest_version = None

        # 创建界面
        self.create_widgets()
        self.update_system_info()

        # 绑定窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 在界面创建完成后设置图标、最大化和检查更新
        self.after(50, self.set_window_icon)
        self.after(100, self.maximize_window)
        self.after(1000, self.check_for_updates_async)

    def set_window_icon(self):
        """设置窗口图标"""
        try:
            # 尝试多种可能的图标路径
            icon_paths = [
                "favicon.ico",  # 当前目录
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "favicon.ico"),  # 上级目录
                os.path.join(sys._MEIPASS, "favicon.ico") if hasattr(sys, '_MEIPASS') else None,  # PyInstaller打包后的路径
            ]

            for icon_path in icon_paths:
                if icon_path and os.path.exists(icon_path):
                    # 对于CustomTkinter，需要使用iconbitmap方法
                    self.iconbitmap(icon_path)

                    # 同时设置wm_iconbitmap以确保兼容性
                    self.wm_iconbitmap(icon_path)

                    # 强制刷新窗口
                    self.update_idletasks()
                    return

        except Exception:
            # 如果设置图标失败，静默处理，不影响程序运行
            pass

    def maximize_window(self):
        """最大化窗口"""
        try:
            # Windows系统
            if os.name == 'nt':
                self.state('zoomed')
            else:
                # Linux/Unix系统
                try:
                    self.attributes('-zoomed', True)
                except:
                    # 如果-zoomed不支持，尝试其他方法
                    self.geometry("1200x800")
        except Exception:
            # 如果最大化失败，至少设置一个较大的窗口尺寸
            try:
                self.geometry("1200x800")
            except:
                pass

    def create_widgets(self):
        """创建界面组件"""
        # 主容器 - 增加内边距
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # 创建左右分栏 - 直接使用主容器
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        # 左侧面板 - 调整宽度比例
        left_panel = ctk.CTkFrame(content_frame)
        left_panel.pack(side="left", fill="both", expand=False, padx=(0, 8))
        left_panel.configure(width=380)  # 固定左侧宽度

        # 右侧面板 - 占用剩余空间
        right_panel = ctk.CTkFrame(content_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=(8, 0))

        self.create_left_panel(left_panel)
        self.create_right_panel(right_panel)
    
    def create_left_panel(self, parent):
        """创建左侧面板"""
        # 系统信息卡片 - 减少高度
        self.system_info_card = StatusCard(parent, "📋 系统信息")
        self.system_info_card.pack(fill="x", pady=(0, 12))

        # 操作按钮区域
        action_frame = ctk.CTkFrame(parent)
        action_frame.pack(fill="x", pady=(0, 12))

        action_title = ctk.CTkLabel(
            action_frame,
            text="🛠 操作选项",
            font=FONTS['subtitle'],
            text_color=COLORS['text_primary']
        )
        action_title.pack(pady=(12, 8))

        # 按钮容器 - 减少内边距
        button_container = ctk.CTkFrame(action_frame, fg_color="transparent")
        button_container.pack(fill="x", padx=15, pady=(0, 12))

        # 修改ID按钮
        self.modify_ids_btn = ActionButton(
            button_container,
            text="🔄 修改Telemetry ID",
            command=self.modify_telemetry_ids,
            style="primary"
        )
        self.modify_ids_btn.pack(fill="x", pady=3)

        # 清理数据库按钮
        self.clean_db_btn = ActionButton(
            button_container,
            text="🗃 清理数据库",
            command=self.clean_database,
            style="warning"
        )
        self.clean_db_btn.pack(fill="x", pady=3)

        # 清理工作区按钮
        self.clean_workspace_btn = ActionButton(
            button_container,
            text="💾 清理工作区",
            command=self.clean_workspace,
            style="warning"
        )
        self.clean_workspace_btn.pack(fill="x", pady=3)

        # 分隔线
        separator = ctk.CTkFrame(button_container, height=2, fg_color=COLORS['secondary'])
        separator.pack(fill="x", pady=8)

        # 一键清理按钮
        self.clean_all_btn = ActionButton(
            button_container,
            text="🚀 一键清理全部",
            command=self.clean_all,
            style="success"
        )
        self.clean_all_btn.pack(fill="x", pady=3)

        # 分隔线
        separator2 = ctk.CTkFrame(button_container, height=2, fg_color=COLORS['secondary'])
        separator2.pack(fill="x", pady=8)

        # 删除备份按钮
        self.delete_backups_btn = ActionButton(
            button_container,
            text="🗑 删除所有备份",
            command=self.delete_all_backups,
            style="danger"
        )
        self.delete_backups_btn.pack(fill="x", pady=3)

        # 进度卡片 - 占用剩余空间
        self.progress_card = ProgressCard(parent, "📊 操作进度")
        self.progress_card.pack(fill="both", expand=True, pady=(0, 0))
    
    def create_right_panel(self, parent):
        """创建右侧面板"""
        # 日志区域标题
        log_title = ctk.CTkLabel(
            parent,
            text="📝 操作日志",
            font=FONTS['subtitle'],
            text_color=COLORS['text_primary']
        )
        log_title.pack(pady=(12, 8))

        # 日志文本框 - 恢复原始大小，占用大部分空间
        self.log_textbox = LogTextBox(parent)
        self.log_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 8))

        # 日志控制区域 - 包含所有按钮
        log_control_frame = ctk.CTkFrame(parent, fg_color="transparent")
        log_control_frame.pack(fill="x", padx=15, pady=(0, 12))

        # 左侧：使用说明
        info_label = ctk.CTkLabel(
            log_control_frame,
            text="💡 使用前请确保已完全退出 VS Code",
            font=FONTS['small'],
            text_color=COLORS['warning']
        )
        info_label.pack(side="left")

        # 右侧按钮组
        button_group = ctk.CTkFrame(log_control_frame, fg_color="transparent")
        button_group.pack(side="right")

        # 查看源码按钮
        source_btn = ActionButton(
            button_group,
            text="🔗 查看源码",
            command=self.open_source_code,
            style="primary"
        )
        source_btn.pack(side="right", padx=(8, 0))

        # 更新按钮 - 显示版本信息
        self.update_btn = ActionButton(
            button_group,
            text=f"🔄 v{get_current_version()}",
            command=self.check_for_updates_manual,
            style="warning"
        )
        self.update_btn.pack(side="right", padx=(8, 0))
        self.update_btn.configure(state="disabled")  # 初始状态为禁用

        # 清空日志按钮
        clear_log_btn = ActionButton(
            button_group,
            text="🗑 清空日志",
            command=self.clear_log,
            style="danger"
        )
        clear_log_btn.pack(side="right", padx=(8, 0))

        # 添加欢迎消息
        self.log_textbox.append_log("欢迎使用 AugmentNew！", "INFO")
        self.log_textbox.append_log("选择需要的操作，程序会自动创建备份文件", "INFO")



    def open_source_code(self):
        """打开源码链接"""
        import webbrowser
        try:
            webbrowser.open("https://github.com/alltobebetter/AugmentNew")
            self.log_textbox.append_log("已在浏览器中打开源码页面", "INFO")
        except Exception as e:
            self.log_textbox.append_log(f"打开源码页面失败: {str(e)}", "ERROR")

    def check_for_updates_async(self):
        """异步检查更新"""
        def check_updates():
            try:
                result = check_for_updates()
                # 在主线程中更新UI
                self.after(0, lambda: self.update_version_status(result))
            except Exception as e:
                self.after(0, lambda: self.log_textbox.append_log(f"检查更新失败: {str(e)}", "ERROR"))

        # 在后台线程中检查更新
        import threading
        thread = threading.Thread(target=check_updates, daemon=True)
        thread.start()

    def check_for_updates_manual(self):
        """手动检查更新"""
        if self.current_operation and self.current_operation.is_running():
            messagebox.showwarning("警告", "有操作正在进行中，请等待完成")
            return

        self.update_btn.set_processing(True, "检查中...")
        self.log_textbox.append_log("正在检查更新...", "INFO")

        def check_updates():
            try:
                result = check_for_updates()
                self.after(0, lambda: self.handle_manual_update_check(result))
            except Exception as e:
                self.after(0, lambda: self.handle_update_check_error(str(e)))

        import threading
        thread = threading.Thread(target=check_updates, daemon=True)
        thread.start()

    def update_version_status(self, result):
        """更新版本状态"""
        if result['error']:
            # 检查失败，保持按钮为检查更新状态
            self.update_btn.configure(
                text=f"🔄 v{get_current_version()}",
                state="normal"
            )
            return

        self.latest_version = result['latest_version']
        self.update_available = result['has_update']

        if result['has_update']:
            # 有更新可用
            self.update_btn.configure(
                text=f"🆕 v{result['latest_version']} 可用",
                state="normal",
                command=self.open_update_page
            )
            # 更新按钮样式为成功色
            self.update_btn.configure(fg_color=COLORS['success'])
        else:
            # 已是最新版本
            self.update_btn.configure(
                text=f"✅ v{get_current_version()} 最新",
                state="disabled"
            )

    def handle_manual_update_check(self, result):
        """处理手动更新检查结果"""
        self.update_btn.set_processing(False)

        if result['error']:
            self.log_textbox.append_log(f"检查更新失败: {result['error']}", "ERROR")
            messagebox.showerror("检查更新失败", result['error'])
            return

        if result['has_update']:
            self.log_textbox.append_log(f"发现新版本: v{result['latest_version']}", "SUCCESS")
            messagebox.showinfo(
                "发现新版本",
                f"发现新版本 v{result['latest_version']}！\n\n"
                f"当前版本: v{get_current_version()}\n"
                f"最新版本: v{result['latest_version']}\n\n"
                "点击更新按钮访问下载页面"
            )
        else:
            self.log_textbox.append_log("已是最新版本", "INFO")
            messagebox.showinfo("检查更新", "您使用的已是最新版本！")

        self.update_version_status(result)

    def handle_update_check_error(self, error):
        """处理更新检查错误"""
        self.update_btn.set_processing(False)
        self.log_textbox.append_log(f"检查更新失败: {error}", "ERROR")

    def open_update_page(self):
        """打开更新页面"""
        import webbrowser
        try:
            webbrowser.open(get_update_url())
            self.log_textbox.append_log("已在浏览器中打开更新页面", "INFO")
        except Exception as e:
            self.log_textbox.append_log(f"打开更新页面失败: {str(e)}", "ERROR")

    def update_system_info(self):
        """更新系统信息"""
        try:
            # 清空现有信息
            for widget in self.system_info_card.content_frame.winfo_children():
                widget.destroy()
            
            # 添加系统路径信息
            paths_info = [
                ("主目录", get_home_dir()),
                ("应用数据目录", get_app_data_dir()),
                ("存储文件", get_storage_path()),
                ("数据库文件", get_db_path()),
                ("机器ID文件", get_machine_id_path()),
                ("工作区存储", get_workspace_storage_path())
            ]
            
            for label, path in paths_info:
                exists = os.path.exists(path)
                color = COLORS['success'] if exists else COLORS['danger']
                status = "✅" if exists else "❌"
                
                self.system_info_card.add_info_row(
                    label, 
                    f"{status} {os.path.basename(path)}", 
                    color
                )
            
            self.log_textbox.append_log("系统信息已更新", "INFO")
            
        except Exception as e:
            self.log_textbox.append_log(f"更新系统信息失败: {str(e)}", "ERROR")
    
    def modify_telemetry_ids(self):
        """修改Telemetry ID"""
        if self.current_operation and self.current_operation.is_running():
            messagebox.showwarning("警告", "有操作正在进行中，请等待完成")
            return
        
        def progress_callback(value, status):
            self.progress_card.update_progress(value, status)
        
        def success_callback(result):
            self.modify_ids_btn.set_processing(False)
            self.progress_card.update_progress(1.0, "修改完成")
            
            self.log_textbox.append_log("Telemetry ID 修改成功！", "SUCCESS")
            self.log_textbox.append_log(f"存储备份: {result['storage_backup_path']}", "INFO")
            if result['machine_id_backup_path']:
                self.log_textbox.append_log(f"机器ID备份: {result['machine_id_backup_path']}", "INFO")
            
            self.log_textbox.append_log(f"旧机器ID: {result['old_machine_id'][:16]}...", "INFO")
            self.log_textbox.append_log(f"新机器ID: {result['new_machine_id'][:16]}...", "INFO")
            self.log_textbox.append_log(f"旧设备ID: {result['old_device_id']}", "INFO")
            self.log_textbox.append_log(f"新设备ID: {result['new_device_id']}", "INFO")
        
        def error_callback(error):
            self.modify_ids_btn.set_processing(False)
            self.progress_card.reset()
            self.log_textbox.append_log(f"修改Telemetry ID失败: {str(error)}", "ERROR")
            messagebox.showerror("错误", f"操作失败: {str(error)}")
        
        self.modify_ids_btn.set_processing(True, "修改中...")
        self.progress_card.reset()
        self.log_textbox.append_log("开始修改 Telemetry ID...", "INFO")
        
        self.current_operation = ThreadedOperation(
            modify_telemetry_ids,
            success_callback,
            error_callback,
            progress_callback
        )
        self.current_operation.start()

    def clean_database(self):
        """清理数据库"""
        if self.current_operation and self.current_operation.is_running():
            messagebox.showwarning("警告", "有操作正在进行中，请等待完成")
            return

        def progress_callback(value, status):
            self.progress_card.update_progress(value, status)

        def success_callback(result):
            self.clean_db_btn.set_processing(False)
            self.progress_card.update_progress(1.0, "清理完成")

            self.log_textbox.append_log("数据库清理成功！", "SUCCESS")
            self.log_textbox.append_log(f"数据库备份: {result['db_backup_path']}", "INFO")
            self.log_textbox.append_log(f"删除了 {result['deleted_rows']} 条包含'augment'的记录", "INFO")

        def error_callback(error):
            self.clean_db_btn.set_processing(False)
            self.progress_card.reset()
            self.log_textbox.append_log(f"清理数据库失败: {str(error)}", "ERROR")
            messagebox.showerror("错误", f"操作失败: {str(error)}")

        self.clean_db_btn.set_processing(True, "清理中...")
        self.progress_card.reset()
        self.log_textbox.append_log("开始清理数据库...", "INFO")

        self.current_operation = ThreadedOperation(
            clean_augment_data,
            success_callback,
            error_callback,
            progress_callback
        )
        self.current_operation.start()

    def clean_workspace(self):
        """清理工作区"""
        if self.current_operation and self.current_operation.is_running():
            messagebox.showwarning("警告", "有操作正在进行中，请等待完成")
            return

        def progress_callback(value, status):
            self.progress_card.update_progress(value, status)

        def success_callback(result):
            self.clean_workspace_btn.set_processing(False)
            self.progress_card.update_progress(1.0, "清理完成")

            self.log_textbox.append_log("工作区清理成功！", "SUCCESS")
            self.log_textbox.append_log(f"工作区备份: {result['backup_path']}", "INFO")
            self.log_textbox.append_log(f"删除了 {result['deleted_files_count']} 个文件", "INFO")

            if result.get('failed_operations'):
                self.log_textbox.append_log(f"有 {len(result['failed_operations'])} 个操作失败", "WARNING")

            if result.get('failed_compressions'):
                self.log_textbox.append_log(f"有 {len(result['failed_compressions'])} 个文件备份失败", "WARNING")

        def error_callback(error):
            self.clean_workspace_btn.set_processing(False)
            self.progress_card.reset()
            self.log_textbox.append_log(f"清理工作区失败: {str(error)}", "ERROR")
            messagebox.showerror("错误", f"操作失败: {str(error)}")

        self.clean_workspace_btn.set_processing(True, "清理中...")
        self.progress_card.reset()
        self.log_textbox.append_log("开始清理工作区...", "INFO")

        self.current_operation = ThreadedOperation(
            clean_workspace_storage,
            success_callback,
            error_callback,
            progress_callback
        )
        self.current_operation.start()

    def clean_all(self):
        """一键清理全部"""
        if self.current_operation and self.current_operation.is_running():
            messagebox.showwarning("警告", "有操作正在进行中，请等待完成")
            return

        # 确认对话框
        result = messagebox.askyesno(
            "确认操作",
            "这将执行以下操作：\n\n"
            "1. 修改 Telemetry ID\n"
            "2. 清理数据库\n"
            "3. 清理工作区存储\n\n"
            "所有操作都会自动创建备份。\n"
            "确定要继续吗？"
        )

        if not result:
            return

        def progress_callback(value, status):
            self.progress_card.update_progress(value, status)

        def run_all_operations():
            """运行所有清理操作"""
            try:
                progress_callback(0.1, "开始一键清理...")

                # 1. 修改 Telemetry ID
                progress_callback(0.2, "修改 Telemetry ID...")
                telemetry_result = modify_telemetry_ids()

                progress_callback(0.5, "清理数据库...")
                # 2. 清理数据库
                db_result = clean_augment_data()

                progress_callback(0.8, "清理工作区...")
                # 3. 清理工作区
                ws_result = clean_workspace_storage()

                progress_callback(1.0, "全部操作完成")

                return {
                    'telemetry': telemetry_result,
                    'database': db_result,
                    'workspace': ws_result
                }

            except Exception as e:
                raise e

        def success_callback(results):
            self.clean_all_btn.set_processing(False)
            self.progress_card.update_progress(1.0, "全部完成")

            self.log_textbox.append_log("🎉 一键清理全部完成！", "SUCCESS")

            # 显示详细结果
            telemetry = results['telemetry']
            database = results['database']
            workspace = results['workspace']

            self.log_textbox.append_log("=" * 50, "INFO")
            self.log_textbox.append_log("📋 操作摘要:", "INFO")
            self.log_textbox.append_log(f"✅ Telemetry ID已更新", "SUCCESS")
            self.log_textbox.append_log(f"✅ 数据库清理完成，删除 {database['deleted_rows']} 条记录", "SUCCESS")
            self.log_textbox.append_log(f"✅ 工作区清理完成，删除 {workspace['deleted_files_count']} 个文件", "SUCCESS")
            self.log_textbox.append_log("=" * 50, "INFO")

            messagebox.showinfo(
                "操作完成",
                "一键清理已完成！\n\n"
                "现在可以重新启动 VS Code 并使用新邮箱登录 AugmentCode 插件。"
            )

        def error_callback(error):
            self.clean_all_btn.set_processing(False)
            self.progress_card.reset()
            self.log_textbox.append_log(f"一键清理失败: {str(error)}", "ERROR")
            messagebox.showerror("错误", f"操作失败: {str(error)}")

        self.clean_all_btn.set_processing(True, "清理中...")
        self.progress_card.reset()
        self.log_textbox.append_log("开始一键清理全部操作...", "INFO")

        self.current_operation = ThreadedOperation(
            run_all_operations,
            success_callback,
            error_callback,
            progress_callback
        )
        self.current_operation.start()

    def delete_all_backups(self):
        """删除所有备份文件"""
        if self.current_operation and self.current_operation.is_running():
            messagebox.showwarning("警告", "有操作正在进行中，请等待完成")
            return

        # 首先查找备份文件
        try:
            backup_files = find_backup_files()
            total_files = sum(len(files) for files in backup_files.values())

            if total_files == 0:
                messagebox.showinfo("提示", "没有找到备份文件")
                self.log_textbox.append_log("没有找到备份文件", "INFO")
                return

            # 确认对话框
            result = messagebox.askyesno(
                "确认删除",
                f"找到 {total_files} 个备份文件：\n\n"
                f"• 存储配置备份: {len(backup_files['storage_backups'])} 个\n"
                f"• 数据库备份: {len(backup_files['db_backups'])} 个\n"
                f"• 机器ID备份: {len(backup_files['machine_id_backups'])} 个\n"
                f"• 工作区备份: {len(backup_files['workspace_backups'])} 个\n\n"
                "确定要删除所有备份文件吗？\n"
                "此操作不可撤销！"
            )

            if not result:
                return

        except Exception as e:
            messagebox.showerror("错误", f"查找备份文件失败: {str(e)}")
            return

        def progress_callback(value, status):
            self.progress_card.update_progress(value, status)

        def success_callback(result):
            self.delete_backups_btn.set_processing(False)
            self.progress_card.update_progress(1.0, "删除完成")

            self.log_textbox.append_log("备份文件删除成功！", "SUCCESS")
            self.log_textbox.append_log(f"删除了 {result['deleted_count']} 个文件", "INFO")
            self.log_textbox.append_log(f"释放空间: {result['total_size_freed']:.2f} MB", "INFO")

            if result['failed_files']:
                self.log_textbox.append_log(f"有 {len(result['failed_files'])} 个文件删除失败", "WARNING")
                for failed_file in result['failed_files']:
                    self.log_textbox.append_log(f"失败: {failed_file}", "WARNING")

            # 显示备份类型统计
            backup_types = result.get('backup_types', {})
            if backup_types:
                self.log_textbox.append_log("删除的备份类型:", "INFO")
                for backup_type, count in backup_types.items():
                    if count > 0:
                        type_name = {
                            'storage_backups': '存储配置备份',
                            'db_backups': '数据库备份',
                            'machine_id_backups': '机器ID备份',
                            'workspace_backups': '工作区备份'
                        }.get(backup_type, backup_type)
                        self.log_textbox.append_log(f"  • {type_name}: {count} 个", "INFO")

        def error_callback(error):
            self.delete_backups_btn.set_processing(False)
            self.progress_card.reset()
            self.log_textbox.append_log(f"删除备份文件失败: {str(error)}", "ERROR")
            messagebox.showerror("错误", f"操作失败: {str(error)}")

        self.delete_backups_btn.set_processing(True, "删除中...")
        self.progress_card.reset()
        self.log_textbox.append_log("开始删除备份文件...", "INFO")

        self.current_operation = ThreadedOperation(
            clean_all_backups,
            success_callback,
            error_callback,
            progress_callback
        )
        self.current_operation.start()

    def clear_log(self):
        """清空日志"""
        self.log_textbox.clear_log()
        self.log_textbox.append_log("日志已清空", "INFO")

    def on_closing(self):
        """窗口关闭事件"""
        if self.current_operation and self.current_operation.is_running():
            result = messagebox.askyesno(
                "确认退出",
                "有操作正在进行中，确定要退出吗？"
            )
            if not result:
                return

        self.destroy()
