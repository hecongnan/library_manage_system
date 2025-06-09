import tkinter as tk
from tkinter import messagebox

def user_login():
    username = user_name.get()
    password = user_pwd.get()
    if username and password:
        messagebox.showinfo("登录成功", f"欢迎回来，{username}！")
    else:
        messagebox.showerror("登录失败", "请输入正确的用户名和密码")
def admin_login():
    admin_username = admin_name.get()
    admin_password = admin_pwd.get()
    if admin_username and admin_password:
        messagebox.showinfo("登录成功", f"管理员 {admin_username} 已登录")
    else:
        messagebox.showerror("登录失败", "请输入正确的管理员账号和密码")
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
title_label = tk.Label(root, text="图书馆管理系统 - 用户登录", font=("微软雅黑", 36, "bold"), 
                      fg="#006699", bg="#f0f5f9")
title_label.pack(pady=60)
main_frame = tk.Frame(root, bg="#f0f5f9")
main_frame.pack(expand=True)
user_frame = tk.Frame(main_frame, bg="white", bd=2, relief="groove", padx=40, pady=30)
user_frame.pack(pady=20)
tk.Label(user_frame, text="用户登录", font=("微软雅黑", 20, "bold"), fg="#006699", bg="white").grid(row=0, column=0, columnspan=2, pady=10)

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
admin_frame = tk.Frame(main_frame, bg="white", bd=2, relief="groove", padx=40, pady=30)
tk.Label(admin_frame, text="管理员登录", font=("微软雅黑", 20, "bold"), fg="#993333", bg="white").grid(row=0, column=0, columnspan=2, pady=10)
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
footer_label = tk.Label(root, text="© 2025 图书馆管理系统 | 版权所有", font=("微软雅黑", 10),             fg="#666666", bg="#f0f5f9")
footer_label.pack(side="bottom", pady=20)
root.bind('<Return>', lambda event: user_btn.invoke() if user_frame.winfo_ismapped() else admin_btn.invoke())
root.mainloop()    
