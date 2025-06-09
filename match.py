import tkinter as tk
from tkinter import messagebox
import pymysql  # 新增数据库连接库

# 数据库连接配置
DB_CONFIG = {
    "host": "120.194.82.136",
    "user": "root",
    "password": "365214",
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
            # 查询student_id和phone匹配的记录
            sql = "SELECT student_id FROM user_info WHERE student_id = %s AND phone = %s"
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
            # 查询job_number和phone匹配的记录
            sql = "SELECT job_number FROM manager_info WHERE job_number = %s AND phone = %s"
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
    else:
        messagebox.showerror("登录失败", "用户名或密码错误")


def admin_login():
    admin_username = admin_name.get()
    admin_password = admin_pwd.get()
    if verify_admin_login(admin_username, admin_password):
        messagebox.showinfo("登录成功", f"管理员 {admin_username} 已登录")
    else:
        messagebox.showerror("登录失败", "管理员账号或密码错误")


# 以下为原界面代码（保持不变）
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
root.configure(bg="#f0f5f9")

# 标题标签
title_label = tk.Label(root, text="图书馆管理系统 - 用户登录", font=("微软雅黑", 36, "bold"),
                       fg="#006699", bg="#f0f5f9")
title_label.pack(pady=60)

main_frame = tk.Frame(root, bg="#f0f5f9")
main_frame.pack(expand=True)

# 用户登录框架
user_frame = tk.Frame(main_frame, bg="white", bd=2, relief="groove", padx=40, pady=30)
user_frame.pack(pady=20)
tk.Label(user_frame, text="用户登录", font=("微软雅黑", 20, "bold"), fg="#006699", bg="white").grid(row=0, column=0,
                                                                                                    columnspan=2,
                                                                                                    pady=10)

tk.Label(user_frame, text="用户名：", font=("微软雅黑", 14), bg="white").grid(row=1, column=0, sticky="e", pady=10)
user_name = tk.Entry(user_frame, font=("微软雅黑", 12), width=20)
user_name.grid(row=1, column=1, pady=10)

tk.Label(user_frame, text="密码：", font=("微软雅黑", 14), bg="white").grid(row=2, column=0, sticky="e", pady=10)
user_pwd = tk.Entry(user_frame, font=("微软雅黑", 12), width=20, show="*")
user_pwd.grid(row=2, column=1, pady=10)

user_btn = tk.Button(user_frame, text="登录", font=("微软雅黑", 14), bg="#006699", fg="white",
                     command=user_login, width=10, height=1)
user_btn.grid(row=3, column=0, columnspan=2, pady=10)

toggle_btn = tk.Button(user_frame, text="切换到管理员登录", font=("微软雅黑", 10),
                       bg="#f0f5f9", fg="#006699", command=toggle_login_mode)
toggle_btn.grid(row=4, column=0, columnspan=2, pady=5)

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

# 页脚标签
footer_label = tk.Label(root, text="© 2025 图书馆管理系统 | 版权所有", font=("微软雅黑", 10),
                        fg="#666666", bg="#f0f5f9")
footer_label.pack(side="bottom", pady=20)

# 绑定回车键事件
root.bind('<Return>', lambda event: user_btn.invoke() if user_frame.winfo_ismapped() else admin_btn.invoke())

root.mainloop()
