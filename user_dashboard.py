import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pymysql
from datetime import datetime

# 数据库连接配置
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "charset": "utf8mb4"
}


def get_db_conn(db_name):
    """获取数据库连接"""
    try:
        conn = pymysql.connect(**DB_CONFIG, database=db_name, cursorclass=pymysql.cursors.DictCursor)
        return conn
    except pymysql.MySQLError as e:
        messagebox.showerror("数据库连接失败", f"错误代码：{e.args[0]}\n错误信息：{e.args[1]}")
        return None


# ----------------- 查询图书状态窗口 -----------------
class BookQueryWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("查询图书状态")
        self.geometry("800x600")
        self.configure(bg="#f0f5f9")

        # 搜索框架
        search_frame = tk.Frame(self, bg="#f0f5f9")
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="书名:", bg="#f0f5f9").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(search_frame, text="搜索", command=self.search_books, bg="#006699", fg="white").pack(side=tk.LEFT,
                                                                                                       padx=5)

        # 创建表格
        columns = ("book_id", "title", "author", "category", "status")
        self.book_tree = ttk.Treeview(self, columns=columns, show="headings")

        # 设置列标题
        for col in columns:
            self.book_tree.heading(col, text=col)
            self.book_tree.column(col, width=150, anchor=tk.CENTER)

        self.book_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 初始加载部分图书
        self.search_books()

    def search_books(self):
        """搜索图书"""
        keyword = self.search_entry.get().strip()

        # 清空表格
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)

        # 从数据库加载
        conn = get_db_conn("library_db")  # 假设图书在library_db库中
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                if keyword:
                    sql = "SELECT * FROM books WHERE title LIKE %s"
                    cursor.execute(sql, (f"%{keyword}%",))
                else:
                    sql = "SELECT * FROM books LIMIT 50"
                    cursor.execute(sql)

                books = cursor.fetchall()

                for book in books:
                    status_text = "已借出" if book["status"] == 1 else "可借阅"
                    self.book_tree.insert("", tk.END, values=(
                        book["book_id"], book["title"],
                        book["author"], book["category"],
                        status_text
                    ))
        except pymysql.MySQLError as e:
            messagebox.showerror("查询失败", f"错误：{str(e)}")
        finally:
            conn.close()


# ----------------- 归还图书窗口 -----------------
class ReturnBookWindow(tk.Toplevel):
    def __init__(self, parent, student_id):
        super().__init__(parent)
        self.title("归还图书")
        self.geometry("800x600")
        self.configure(bg="#f0f5f9")
        self.student_id = student_id

        # 创建表格
        columns = ("borrow_id", "book_id", "title", "borrow_date", "due_date", "return_date")
        self.borrow_tree = ttk.Treeview(self, columns=columns, show="headings")

        # 设置列标题
        for col in columns:
            self.borrow_tree.heading(col, text=col)
            if col == "title":
                self.borrow_tree.column(col, width=200, anchor=tk.W)
            else:
                self.borrow_tree.column(col, width=120, anchor=tk.CENTER)

        self.borrow_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 按钮框架
        btn_frame = tk.Frame(self, bg="#f0f5f9")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="刷新", command=self.refresh_borrows, bg="#006699", fg="white").pack(side=tk.LEFT,
                                                                                                       padx=5)
        tk.Button(btn_frame, text="归还选中图书", command=self.return_book, bg="#006699", fg="white").pack(side=tk.LEFT,
                                                                                                           padx=5)

        # 初始加载借阅记录
        self.refresh_borrows()

    def refresh_borrows(self):
        """刷新借阅记录表格"""
        # 清空表格
        for item in self.borrow_tree.get_children():
            self.borrow_tree.delete(item)

        # 从数据库加载
        conn = get_db_conn("library_db")  # 假设借阅记录在library_db库中
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                # 联合查询获取图书信息
                sql = """
                SELECT b.borrow_id, b.book_id, bo.title, b.borrow_date, b.due_date, b.return_date 
                FROM borrow_records b
                JOIN books bo ON b.book_id = bo.book_id
                WHERE b.student_id = %s AND b.return_date IS NULL
                ORDER BY b.borrow_date DESC
                """
                cursor.execute(sql, (self.student_id,))
                borrows = cursor.fetchall()

                for borrow in borrows:
                    borrow_date = borrow["borrow_date"].strftime("%Y-%m-%d") if borrow["borrow_date"] else ""
                    due_date = borrow["due_date"].strftime("%Y-%m-%d") if borrow["due_date"] else ""
                    return_date = borrow["return_date"].strftime("%Y-%m-%d") if borrow["return_date"] else ""

                    self.borrow_tree.insert("", tk.END, values=(
                        borrow["borrow_id"],
                        borrow["book_id"],
                        borrow["title"],
                        borrow_date,
                        due_date,
                        return_date
                    ))
        except pymysql.MySQLError as e:
            messagebox.showerror("查询失败", f"错误：{str(e)}")
        finally:
            conn.close()

    def return_book(self):
        """归还选中的图书"""
        selected_item = self.borrow_tree.selection()
        if not selected_item:
            messagebox.showinfo("提示", "请先选择要归还的图书")
            return

        values = self.borrow_tree.item(selected_item[0])["values"]
        borrow_id = values[0]
        book_id = values[1]
        title = values[2]

        if messagebox.askyesno("确认", f"确定要归还《{title}》吗？"):
            conn = get_db_conn("library_db")
            if not conn:
                return

            try:
                with conn.cursor() as cursor:
                    # 更新归还日期
                    return_date = datetime.now().strftime("%Y-%m-%d")
                    sql = "UPDATE borrow_records SET return_date = %s WHERE borrow_id = %s"
                    cursor.execute(sql, (return_date, borrow_id))

                    # 更新图书状态为可借阅
                    sql = "UPDATE books SET status = 0 WHERE book_id = %s"
                    cursor.execute(sql, (book_id,))

                    conn.commit()
                    messagebox.showinfo("成功", "归还图书成功")
                    self.refresh_borrows()
            except pymysql.MySQLError as e:
                conn.rollback()
                messagebox.showerror("归还失败", f"错误：{str(e)}")
            finally:
                conn.close()


# ----------------- 用户反馈窗口 -----------------
class UserFeedbackWindow(tk.Toplevel):
    def __init__(self, parent, student_id):
        super().__init__(parent)
        self.title("用户反馈")
        self.geometry("500x400")
        self.configure(bg="#f0f5f9")
        self.student_id = student_id

        # 获取用户信息
        conn = get_db_conn("user_db")
        if conn:
            try:
                with conn.cursor() as cursor:
                    sql = "SELECT user_id FROM user_table WHERE student_id = %s"
                    cursor.execute(sql, (student_id,))
                    user = cursor.fetchone()
                    self.user_id = user["user_id"] if user else None
            except:
                self.user_id = None
            finally:
                conn.close()
        else:
            self.user_id = None

        if not self.user_id:
            messagebox.showerror("错误", "无法获取用户ID")
            self.destroy()
            return

        tk.Label(self, text="反馈内容:", bg="#f0f5f9").pack(pady=10, padx=20, anchor=tk.W)

        self.feedback_text = tk.Text(self, width=50, height=15)
        self.feedback_text.pack(pady=10, padx=20)

        tk.Button(self, text="提交反馈", command=self.submit_feedback, bg="#006699", fg="white").pack(pady=10)

    def submit_feedback(self):
        """提交反馈"""
        content = self.feedback_text.get("1.0", tk.END).strip()

        if not content:
            messagebox.showinfo("提示", "反馈内容不能为空")
            return

        conn = get_db_conn("library_db")
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sql = "INSERT INTO feedback (user_id, content, create_time) VALUES (%s, %s, %s)"
                cursor.execute(sql, (self.user_id, content, create_time))
                conn.commit()
                messagebox.showinfo("成功", "反馈提交成功，感谢您的反馈！")
                self.destroy()
        except pymysql.MySQLError as e:
            conn.rollback()
            messagebox.showerror("提交失败", f"错误：{str(e)}")
        finally:
            conn.close()


# ----------------- 显示用户面板 -----------------
def show_user_dashboard(root, username):
    """显示用户功能面板"""
    user_dash = tk.Toplevel(root)
    user_dash.title(f"用户面板 - {username}")
    user_dash.geometry("800x600")
    user_dash.configure(bg="#f0f5f9")

    # 标题
    tk.Label(user_dash, text="用户功能面板", font=("微软雅黑", 24, "bold"), fg="#006699", bg="#f0f5f9").pack(pady=20)

    # 功能按钮
    tk.Button(user_dash, text="查询图书状态", font=("微软雅黑", 14), bg="#006699", fg="white",
              command=lambda: BookQueryWindow(user_dash), width=15).pack(pady=10)
    tk.Button(user_dash, text="归还图书", font=("微软雅黑", 14), bg="#006699", fg="white",
              command=lambda: ReturnBookWindow(user_dash, username), width=15).pack(pady=10)
    tk.Button(user_dash, text="用户反馈", font=("微软雅黑", 14), bg="#006699", fg="white",
              command=lambda: UserFeedbackWindow(user_dash, username), width=15).pack(pady=10)

    # 返回登录界面按钮
    tk.Button(user_dash, text="退出登录", font=("微软雅黑", 12), bg="#f0f5f9", fg="#006699",
              command=lambda: [user_dash.destroy(), root.deiconify()]).pack(pady=20)