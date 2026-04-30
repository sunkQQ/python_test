import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import time

# 主窗口
root = tk.Tk()
root.title("Python记事本")
root.geometry("500x400")

# 笔记列表
notes = []

# 读取文件
try:
    with open("notes.txt", "r", encoding="utf-8") as f:
        notes = f.read().splitlines()
except:
    notes = []


# 保存文件
def save_notes():
    with open("notes.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(notes))


# 添加笔记
def add_note():
    content = simpledialog.askstring("添加笔记", "请输入内容：")
    if content:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        notes.append(f"[{now}] {content}")
        save_notes()
        show_all()
        messagebox.showinfo("成功", "笔记已保存！")


# 显示所有
def show_all():
    text_box.delete(1.0, tk.END)
    if not notes:
        text_box.insert(tk.END, "暂无笔记")
    else:
        for i, n in enumerate(notes, 1):
            text_box.insert(tk.END, f"{i}. {n}\n")


# 修改笔记
def edit_note():
    if not notes:
        messagebox.showwarning("提示", "没有笔记")
        return
    idx = simpledialog.askinteger("修改", f"输入要修改的序号（1-{len(notes)}）")
    if idx and 1 <= idx <= len(notes):
        new_content = simpledialog.askstring("修改", "输入新内容：")
        if new_content:
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            notes[idx - 1] = f"[{now}] {new_content}"
            save_notes()
            show_all()
            messagebox.showinfo("成功", "修改完成")


# 删除笔记
def del_note():
    if not notes:
        messagebox.showwarning("提示", "没有笔记")
        return
    idx = simpledialog.askinteger("删除", f"输入要删除的序号（1-{len(notes)}）")
    if idx and 1 <= idx <= len(notes):
        del notes[idx - 1]
        save_notes()
        show_all()
        messagebox.showinfo("成功", "删除成功")


# 搜索
def search_note():
    key = simpledialog.askstring("搜索", "输入关键词：")
    if not key:
        return
    text_box.delete(1.0, tk.END)
    find = False
    for i, n in enumerate(notes, 1):
        if key in n:
            text_box.insert(tk.END, f"{i}. {n}\n")
            find = True
    if not find:
        text_box.insert(tk.END, "未找到")


# 界面
text_box = scrolledtext.ScrolledText(root, width=60, height=18)
text_box.pack(pady=10)

# 按钮
tk.Button(root, text="添加笔记", command=add_note).pack(side=tk.LEFT, padx=5)
tk.Button(root, text="查看全部", command=show_all).pack(side=tk.LEFT, padx=5)
tk.Button(root, text="修改笔记", command=edit_note).pack(side=tk.LEFT, padx=5)
tk.Button(root, text="删除笔记", command=del_note).pack(side=tk.LEFT, padx=5)
tk.Button(root, text="搜索笔记", command=search_note).pack(side=tk.LEFT, padx=5)

show_all()
root.mainloop()
