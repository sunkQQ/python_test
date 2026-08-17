#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DocumentEditor - 功能完善的文档编辑器

@author sunk
@since 2026-06-10
"""

import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from tkinter.scrolledtext import ScrolledText
from datetime import datetime


class DocumentEditor:
    """文档编辑器主类"""

    def __init__(self, root):
        self.root = root
        self.root.title("文档编辑器")
        self.root.geometry("900x600")

        # 当前打开的文件路径
        self.current_file = None
        # 文件是否已修改
        self.modified = False
        # 查找对话框引用
        self.find_dialog = None

        # 创建菜单栏
        self.create_menu()

        # 创建工具栏
        self.create_toolbar()

        # 创建编辑区域
        self.create_editor()

        # 创建状态栏
        self.create_status_bar()

        # 绑定事件
        self.bind_events()

        # 更新标题
        self.update_title()

    def create_menu(self):
        """创建菜单栏"""
        self.menu_bar = tk.Menu(self.root)

        # 文件菜单
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="新建", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(
            label="打开", command=self.open_file, accelerator="Ctrl+O"
        )
        file_menu.add_command(
            label="保存", command=self.save_file, accelerator="Ctrl+S"
        )
        file_menu.add_command(
            label="另存为", command=self.save_as_file, accelerator="Ctrl+Shift+S"
        )
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.exit_app, accelerator="Ctrl+Q")
        self.menu_bar.add_cascade(label="文件", menu=file_menu)

        # 编辑菜单
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="撤销", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="重做", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="剪切", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="复制", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="粘贴", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(
            label="查找", command=self.show_find_dialog, accelerator="Ctrl+F"
        )
        edit_menu.add_command(
            label="替换", command=self.show_replace_dialog, accelerator="Ctrl+H"
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="全选", command=self.select_all, accelerator="Ctrl+A"
        )
        self.menu_bar.add_cascade(label="编辑", menu=edit_menu)

        # 格式菜单
        format_menu = tk.Menu(self.menu_bar, tearoff=0)
        format_menu.add_command(
            label="加粗", command=self.toggle_bold, accelerator="Ctrl+B"
        )
        format_menu.add_command(
            label="斜体", command=self.toggle_italic, accelerator="Ctrl+I"
        )
        format_menu.add_command(
            label="下划线", command=self.toggle_underline, accelerator="Ctrl+U"
        )
        format_menu.add_separator()
        format_menu.add_command(label="字体颜色", command=self.change_font_color)
        format_menu.add_command(label="背景颜色", command=self.change_bg_color)
        self.menu_bar.add_cascade(label="格式", menu=format_menu)

        # 帮助菜单
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        self.menu_bar.add_cascade(label="帮助", menu=help_menu)

        self.root.config(menu=self.menu_bar)

    def create_toolbar(self):
        """创建工具栏"""
        self.toolbar = ttk.Frame(self.root, padding=2)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # 字体选择
        self.font_var = tk.StringVar(value="微软雅黑")
        self.font_combo = ttk.Combobox(
            self.toolbar,
            textvariable=self.font_var,
            width=12,
            values=["微软雅黑", "宋体", "黑体", "楷体", "Arial", "Times New Roman"],
        )
        self.font_combo.grid(row=0, column=0, padx=2)
        self.font_combo.bind("<<ComboboxSelected>>", self.change_font)

        # 字号选择
        self.size_var = tk.IntVar(value=12)
        self.size_combo = ttk.Combobox(
            self.toolbar,
            textvariable=self.size_var,
            width=5,
            values=[8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32],
        )
        self.size_combo.grid(row=0, column=1, padx=2)
        self.size_combo.bind("<<ComboboxSelected>>", self.change_font_size)

        # 分隔线
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).grid(
            row=0, column=2, padx=5, sticky="ns"
        )

        # 格式化按钮
        self.bold_btn = ttk.Button(
            self.toolbar, text="B", command=self.toggle_bold, width=3
        )
        self.bold_btn.grid(row=0, column=3, padx=1)

        self.italic_btn = ttk.Button(
            self.toolbar, text="I", command=self.toggle_italic, width=3
        )
        self.italic_btn.grid(row=0, column=4, padx=1)

        self.underline_btn = ttk.Button(
            self.toolbar, text="U", command=self.toggle_underline, width=3
        )
        self.underline_btn.grid(row=0, column=5, padx=1)

        # 分隔线
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).grid(
            row=0, column=6, padx=5, sticky="ns"
        )

        # 颜色按钮
        self.font_color_btn = ttk.Button(
            self.toolbar, text="A", command=self.change_font_color, width=3
        )
        self.font_color_btn.grid(row=0, column=7, padx=1)

        self.bg_color_btn = ttk.Button(
            self.toolbar, text="Bg", command=self.change_bg_color, width=4
        )
        self.bg_color_btn.grid(row=0, column=8, padx=1)

        # 分隔线
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).grid(
            row=0, column=9, padx=5, sticky="ns"
        )

        # 对齐按钮
        self.align_left_btn = ttk.Button(
            self.toolbar, text="左", command=lambda: self.set_alignment("left"), width=3
        )
        self.align_left_btn.grid(row=0, column=10, padx=1)

        self.align_center_btn = ttk.Button(
            self.toolbar,
            text="中",
            command=lambda: self.set_alignment("center"),
            width=3,
        )
        self.align_center_btn.grid(row=0, column=11, padx=1)

        self.align_right_btn = ttk.Button(
            self.toolbar,
            text="右",
            command=lambda: self.set_alignment("right"),
            width=3,
        )
        self.align_right_btn.grid(row=0, column=12, padx=1)

    def create_editor(self):
        """创建编辑区域"""
        self.editor = ScrolledText(
            self.root, wrap=tk.WORD, undo=True, font=("微软雅黑", 12)
        )
        self.editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Frame(self.root, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 字数统计
        self.word_count_label = ttk.Label(self.status_bar, text="字数: 0 | 字符数: 0")
        self.word_count_label.pack(side=tk.LEFT, padx=5)

        # 当前时间
        self.time_label = ttk.Label(self.status_bar, text="")
        self.time_label.pack(side=tk.RIGHT, padx=5)
        self.update_time()

        # 文件路径
        self.path_label = ttk.Label(self.status_bar, text="未命名")
        self.path_label.pack(side=tk.LEFT, padx=5)

    def bind_events(self):
        """绑定事件"""
        # 键盘快捷键
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-Shift-S>", lambda e: self.save_as_file())
        self.root.bind("<Control-q>", lambda e: self.exit_app())
        self.root.bind("<Control-f>", lambda e: self.show_find_dialog())
        self.root.bind("<Control-h>", lambda e: self.show_replace_dialog())
        self.root.bind("<Control-a>", lambda e: self.select_all())
        self.root.bind("<Control-b>", lambda e: self.toggle_bold())
        self.root.bind("<Control-i>", lambda e: self.toggle_italic())
        self.root.bind("<Control-u>", lambda e: self.toggle_underline())

        # 文本修改事件
        self.editor.bind("<<Modified>>", self.on_modified)

        # 关闭窗口事件
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def update_title(self):
        """更新窗口标题"""
        title = "文档编辑器"
        if self.current_file:
            title = f"{os.path.basename(self.current_file)} - 文档编辑器"
        if self.modified:
            title = "*" + title
        self.root.title(title)

    def update_status(self):
        """更新状态栏"""
        text = self.editor.get("1.0", tk.END)

        # 统计字数（中文按字，英文按单词）
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
        english_words = len(re.findall(r"[a-zA-Z]+", text))
        word_count = chinese_chars + english_words

        # 字符数（不含换行符）
        char_count = len(text.replace("\n", "").replace("\r", ""))

        self.word_count_label.config(text=f"字数: {word_count} | 字符数: {char_count}")

        if self.current_file:
            self.path_label.config(text=self.current_file)
        else:
            self.path_label.config(text="未命名")

    def update_time(self):
        """更新时间显示"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=now)
        self.root.after(1000, self.update_time)

    def on_modified(self, event=None):
        """文本修改事件处理"""
        if self.editor.edit_modified():
            self.modified = True
            self.update_title()
            self.update_status()
            self.editor.edit_modified(False)

    # === 文件操作 ===

    def new_file(self):
        """新建文档"""
        if self.check_save():
            self.editor.delete("1.0", tk.END)
            self.current_file = None
            self.modified = False
            self.update_title()
            self.update_status()

    def open_file(self):
        """打开文档"""
        if self.check_save():
            file_path = filedialog.askopenfilename(
                defaultextension=".txt",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("Markdown文件", "*.md"),
                    ("所有文件", "*.*"),
                ],
            )
            if file_path:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    self.editor.delete("1.0", tk.END)
                    self.editor.insert("1.0", content)
                    self.current_file = file_path
                    self.modified = False
                    self.update_title()
                    self.update_status()
                except Exception as e:
                    messagebox.showerror("错误", f"无法打开文件: {str(e)}")

    def save_file(self):
        """保存文档"""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_as_file()

    def save_as_file(self):
        """另存为"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("文本文件", "*.txt"),
                ("Markdown文件", "*.md"),
                ("所有文件", "*.*"),
            ],
        )
        if file_path:
            self.save_to_file(file_path)

    def save_to_file(self, file_path):
        """保存到指定文件"""
        try:
            content = self.editor.get("1.0", tk.END)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.current_file = file_path
            self.modified = False
            self.update_title()
            self.update_status()
            messagebox.showinfo("成功", "文件保存成功")
        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败: {str(e)}")

    def check_save(self):
        """检查是否需要保存"""
        if self.modified:
            result = messagebox.askyesnocancel("提示", "文档已修改，是否保存？")
            if result is True:
                self.save_file()
                return True
            elif result is False:
                return True
            else:
                return False
        return True

    def exit_app(self):
        """退出应用"""
        if self.check_save():
            self.root.destroy()

    # === 编辑操作 ===

    def undo(self):
        """撤销"""
        try:
            self.editor.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        """重做"""
        try:
            self.editor.edit_redo()
        except tk.TclError:
            pass

    def cut(self):
        """剪切"""
        self.editor.event_generate("<<Cut>>")

    def copy(self):
        """复制"""
        self.editor.event_generate("<<Copy>>")

    def paste(self):
        """粘贴"""
        self.editor.event_generate("<<Paste>>")

    def select_all(self):
        """全选"""
        self.editor.tag_add(tk.SEL, "1.0", tk.END)
        self.editor.mark_set(tk.INSERT, "1.0")
        self.editor.see(tk.INSERT)

    # === 格式操作 ===

    def toggle_bold(self):
        """切换加粗"""
        self.editor.tag_add("bold", tk.SEL_FIRST, tk.SEL_LAST)
        self.editor.tag_config("bold", font=("微软雅黑", 12, "bold"))

    def toggle_italic(self):
        """切换斜体"""
        self.editor.tag_add("italic", tk.SEL_FIRST, tk.SEL_LAST)
        self.editor.tag_config("italic", font=("微软雅黑", 12, "italic"))

    def toggle_underline(self):
        """切换下划线"""
        self.editor.tag_add("underline", tk.SEL_FIRST, tk.SEL_LAST)
        self.editor.tag_config("underline", underline=True)

    def change_font(self, event=None):
        """改变字体"""
        font = self.font_var.get()
        size = self.size_var.get()
        self.editor.tag_add("font", tk.SEL_FIRST, tk.SEL_LAST)
        self.editor.tag_config("font", font=(font, size))

    def change_font_size(self, event=None):
        """改变字号"""
        font = self.font_var.get()
        size = self.size_var.get()
        self.editor.tag_add("font_size", tk.SEL_FIRST, tk.SEL_LAST)
        self.editor.tag_config("font_size", font=(font, size))

    def change_font_color(self):
        """改变字体颜色"""
        color = colorchooser.askcolor()[1]
        if color:
            self.editor.tag_add("font_color", tk.SEL_FIRST, tk.SEL_LAST)
            self.editor.tag_config("font_color", foreground=color)

    def change_bg_color(self):
        """改变背景颜色"""
        color = colorchooser.askcolor()[1]
        if color:
            self.editor.tag_add("bg_color", tk.SEL_FIRST, tk.SEL_LAST)
            self.editor.tag_config("bg_color", background=color)

    def set_alignment(self, align):
        """设置对齐方式"""
        self.editor.tag_add(f"align_{align}", tk.SEL_FIRST, tk.SEL_LAST)
        self.editor.tag_config(f"align_{align}", justify=align)

    # === 查找替换 ===

    def show_find_dialog(self):
        """显示查找对话框"""
        if self.find_dialog:
            self.find_dialog.destroy()

        self.find_dialog = tk.Toplevel(self.root)
        self.find_dialog.title("查找")
        self.find_dialog.geometry("350x100")
        self.find_dialog.transient(self.root)
        self.find_dialog.grab_set()

        ttk.Label(self.find_dialog, text="查找内容:").grid(
            row=0, column=0, padx=5, pady=5
        )
        self.find_entry = ttk.Entry(self.find_dialog, width=30)
        self.find_entry.grid(row=0, column=1, padx=5, pady=5)
        self.find_entry.focus()

        ttk.Button(self.find_dialog, text="查找下一个", command=self.find_next).grid(
            row=1, column=0, padx=5, pady=5
        )
        ttk.Button(
            self.find_dialog, text="取消", command=self.find_dialog.destroy
        ).grid(row=1, column=1, padx=5, pady=5)

        self.find_entry.bind("<Return>", lambda e: self.find_next())

    def find_next(self):
        """查找下一个"""
        search_text = self.find_entry.get()
        if not search_text:
            return

        # 从当前光标位置开始查找
        start_pos = self.editor.search(search_text, tk.INSERT, tk.END)

        if not start_pos:
            # 如果没找到，从文档开头查找
            start_pos = self.editor.search(search_text, "1.0", tk.END)

        if start_pos:
            end_pos = f"{start_pos}+{len(search_text)}c"
            self.editor.tag_remove(tk.SEL, "1.0", tk.END)
            self.editor.tag_add(tk.SEL, start_pos, end_pos)
            self.editor.mark_set(tk.INSERT, end_pos)
            self.editor.see(tk.INSERT)
        else:
            messagebox.showinfo("提示", "未找到匹配内容")

    def show_replace_dialog(self):
        """显示替换对话框"""
        if self.find_dialog:
            self.find_dialog.destroy()

        self.find_dialog = tk.Toplevel(self.root)
        self.find_dialog.title("替换")
        self.find_dialog.geometry("350x150")
        self.find_dialog.transient(self.root)
        self.find_dialog.grab_set()

        ttk.Label(self.find_dialog, text="查找内容:").grid(
            row=0, column=0, padx=5, pady=5
        )
        self.find_entry = ttk.Entry(self.find_dialog, width=30)
        self.find_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.find_dialog, text="替换为:").grid(
            row=1, column=0, padx=5, pady=5
        )
        self.replace_entry = ttk.Entry(self.find_dialog, width=30)
        self.replace_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.find_dialog, text="查找下一个", command=self.find_next).grid(
            row=2, column=0, padx=5, pady=5
        )
        ttk.Button(self.find_dialog, text="替换", command=self.replace_current).grid(
            row=2, column=1, padx=5, pady=5
        )
        ttk.Button(self.find_dialog, text="全部替换", command=self.replace_all).grid(
            row=3, column=0, padx=5, pady=5
        )
        ttk.Button(
            self.find_dialog, text="取消", command=self.find_dialog.destroy
        ).grid(row=3, column=1, padx=5, pady=5)

        self.find_entry.focus()

    def replace_current(self):
        """替换当前匹配项"""
        search_text = self.find_entry.get()
        replace_text = self.replace_entry.get()

        if not search_text:
            return

        # 检查当前选中的文本是否匹配
        try:
            selected_text = self.editor.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text == search_text:
                self.editor.delete(tk.SEL_FIRST, tk.SEL_LAST)
                self.editor.insert(tk.SEL_FIRST, replace_text)
                self.find_next()
            else:
                self.find_next()
        except tk.TclError:
            self.find_next()

    def replace_all(self):
        """替换所有匹配项"""
        search_text = self.find_entry.get()
        replace_text = self.replace_entry.get()

        if not search_text:
            return

        count = 0
        start_pos = "1.0"

        while True:
            start_pos = self.editor.search(search_text, start_pos, tk.END)
            if not start_pos:
                break

            end_pos = f"{start_pos}+{len(search_text)}c"
            self.editor.delete(start_pos, end_pos)
            self.editor.insert(start_pos, replace_text)
            start_pos = f"{start_pos}+{len(replace_text)}c"
            count += 1

        messagebox.showinfo("提示", f"已替换 {count} 处")

    def show_about(self):
        """显示关于对话框"""
        messagebox.showinfo(
            "关于文档编辑器",
            "文档编辑器 v1.0\n\n一个功能完善的文档编辑工具，支持\n文本编辑、格式化、查找替换等功能。\n\n作者: sunk\n日期: 2026-06-10",
        )


def main():
    """主函数"""
    root = tk.Tk()
    app = DocumentEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
