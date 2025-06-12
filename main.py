import tkinter as tk
from tkinter import messagebox
import pymysql
import admin_dashboard  
 import user_dashboard  
from PIL import Image, ImageTk  

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "charset": "utf8mb4"
}

def get_database_connection(db_name):
    """获取数据库连接"""
    try:
        conn = pymysql.connect(**DB_CONFIG, database=db_name, cursorclass=pymysql.cursors.DictCursor)
        return conn
    except pymysql.MySQLError as e:
        messagebox.showerror("数据库连接失败", f"错误代码：{e.args[0]}\n错误信息：{e.args[1]}")
        return None

def verify_user_login(username, password):
    """验证用户登录信息"""
    conn = get_database_connection("user_db")
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            sql = "SELECT student_id FROM user_table WHERE student_id = %s AND phone = %s"
            cursor.execute(sql, (username, password))
            result = cursor.fetchone()
            return result is not None
    except pymysql.MySQLError as e:
        messagebox.showerror("数据库查询失败", f"错误信息：{str(e)}")
        return False
    finally:
        conn.close()

def verify_admin_login(username, password):
    """验证管理员登录信息"""
    conn = get_database_connection("manager_db")
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            sql = "SELECT job_number FROM managers WHERE job_number = %s AND phone = %s"
            cursor.execute(sql, (username, password))
            result = cursor.fetchone()
            return result is not None
    except pymysql.MySQLError as e:
        messagebox.showerror("数据库查询失败", f"错误信息：{str(e)}")
        return False
    finally:
        conn.close()

def user_login():
    username = user_name.get()
    password = user_pwd.get()
    if verify_user_login(username, password):
        messagebox.showinfo("登录成功", f"欢迎回来，{username}！")
        hide_login_frames()
        user_dashboard.show_user_dashboard(root, username)
    else:
        messagebox.showerror("登录失败", "用户名或密码错误")

def admin_login():
    admin_username = admin_name.get()
    admin_password = admin_pwd.get()
    if verify_admin_login(admin_username, admin_password):
        messagebox.showinfo("登录成功", f"管理员 {admin_username} 已登录")
        hide_login_frames()
        admin_dashboard.show_admin_dashboard(root, admin_username)
    else:
        messagebox.showerror("登录失败", "管理员账号或密码错误")

def hide_login_frames():
    """隐藏登录相关的框架"""
    user_frame.pack_forget()
    admin_frame.pack_forget()
    title_label.pack_forget()

def toggle_login_mode():
    if user_frame.winfo_ismapped():
        user_frame.pack_forget()
        admin_frame.pack(pady=40)
        title_label.config(text="图书馆管理系统 - 管理员登录")
    else:
        admin_frame.pack_forget()
        user_frame.pack(pady=20)
        title_label.config(text="图书馆管理系统 - 用户登录")

root = tk.Tk()
root.title("图书馆管理系统")
root.geometry("1024x768")

try:
    bg_image = Image.open("library_background.jpg")  
    bg_image = bg_image.resize((1024, 768), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_canvas = tk.Canvas(root, width=1024, height=768)
    bg_canvas.pack(fill="both", expand=True)
    bg_canvas.create_image(0, 0, image=bg_photo, anchor="nw")
    bg_canvas.image = bg_photo  
except Exception as e:
    print(f"加载背景图失败: {e}")
    root.configure(bg="#f0f5f9")  

# 标题标签，设置有效背景颜色
title_label = tk.Label(bg_canvas, text="图书馆管理系统 - 用户登录", font=("微软雅黑", 36, "bold"),
                       fg="#006699", bg="#f0f5f9")
bg_canvas.create_window(512, 60, window=title_label)

main_frame = tk.Frame(bg_canvas, bg="#f0f5f9")
bg_canvas.create_window(512, 384, window=main_frame)

# 用户登录框架
user_frame = tk.Frame(main_frame, bg="white", bd=2, relief="groove", padx=40, pady=30)
user_frame.pack(pady=20)
tk.Label(user_frame, text="用户登录", font=("微软雅黑", 20, "bold"), fg="#006699", bg="white").grid(row=0, column=0,
                                                                                                    columnspan=2,
                                                                                                    pady=10)

# 添加登录提示信息
hint_label = tk.Label(user_frame, 
                     text="提示：用户名为学号，密码为手机号", 
                     font=("微软雅黑", 10), 
                     fg="#ff6600", 
                     bg="white",
                     justify="left",
                     wraplength=250)
hint_label.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky="w")

tk.Label(user_frame, text="用户名：", font=("微软雅黑", 14), bg="white").grid(row=2, column=0, sticky="e", pady=10)
user_name = tk.Entry(user_frame, font=("微软雅黑", 12), width=20)
user_name.grid(row=2, column=1, pady=10)

tk.Label(user_frame, text="密码：", font=("微软雅黑", 14), bg="white").grid(row=3, column=0, sticky="e", pady=10)
user_pwd = tk.Entry(user_frame, font=("微软雅黑", 12), width=20, show="*")
user_pwd.grid(row=3, column=1, pady=10)

user_btn = tk.Button(user_frame, text="登录", font=("微软雅黑", 14), bg="#006699", fg="white",
                     command=user_login, width=10, height=1)
user_btn.grid(row=4, column=0, columnspan=2, pady=10)

toggle_btn = tk.Button(user_frame, text="切换到管理员登录", font=("微软雅黑", 10),
                       bg="#f0f5f9", fg="#006699", command=toggle_login_mode)
toggle_btn.grid(row=5, column=0, columnspan=2, pady=5)

# 管理员登录框架
admin_frame = tk.Frame(main_frame, bg="white", bd=2, relief="groove", padx=40, pady=30)
tk.Label(admin_frame, text="管理员登录", font=("微软雅黑", 20, "bold"), fg="#993333", bg="white").grid(row=0, column=0,
                                                                                                       columnspan=2,
                                                                                                       pady=10)

tk.Label(admin_frame, text="管理员账号：", font=("微软雅黑", 14), bg="white").grid(row=1, column=0, sticky="e", pady=10)
admin_name = tk.Entry(admin_frame, font=("微软雅黑", 12), width=20)
admin_name.grid(row=1, column=1, pady=10)

tk.Label(admin_frame, text="密码：", font=("微软雅黑", 14), bg="white").grid(row=2, column=0, sticky="e", pady=10)
admin_pwd = tk.Entry(admin_frame, font=("微软雅黑", 12), width=20, show="*")
admin_pwd.grid(row=2, column=1, pady=10)

admin_btn = tk.Button(admin_frame, text="登录", font=("微软雅黑", 14), bg="#993333", fg="white",
                      command=admin_login, width=10, height=1)
admin_btn.grid(row=3, column=0, columnspan=2, pady=10)

toggle_btn_admin = tk.Button(admin_frame, text="切换到用户登录", font=("微软雅黑", 10),
                             bg="#f0f5f9", fg="#993333", command=toggle_login_mode)
toggle_btn_admin.grid(row=4, column=0, columnspan=2, pady=5)

# 页脚标签，设置有效背景颜色
footer_label = tk.Label(bg_canvas, text="© 2025 图书馆管理系统 | 版权所有", font=("微软雅黑", 10),
                        fg="#666666", bg="#f0f5f9")
bg_canvas.create_window(512, 740, window=footer_label)

# 绑定回车键事件
root.bind('<Return>', lambda event: user_btn.invoke() if user_frame.winfo_ismapped() else admin_btn.invoke())

root.mainloop()
