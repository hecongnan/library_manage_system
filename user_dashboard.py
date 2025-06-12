import tkinter as tk
from tkinter import ttk, messagebox
import pymysql
from datetime import datetime, timedelta

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


# ----------------- 用户反馈窗口 -----------------
class UserFeedbackWindow(tk.Toplevel):
    def __init__(self, parent, student_id):
        super().__init__(parent)
        self.title("用户反馈")
        self.geometry("500x400")
        self.configure(bg="#f0f5f9")
        self.student_id = student_id

        # 获取用户ID
        self.user_id = None
        conn = get_db_conn("user_db")
        if conn:
            try:
                with conn.cursor() as cursor:
                    sql = "SELECT user_id FROM user_table WHERE student_id = %s"
                    cursor.execute(sql, (student_id,))
                    user = cursor.fetchone()
                    self.user_id = user["user_id"] if user else None
            except Exception as e:
                messagebox.showerror("错误", f"获取用户ID失败：{str(e)}")
            finally:
                conn.close()

        if not self.user_id:
            messagebox.showerror("错误", "无法获取用户ID，反馈提交失败")
            self.destroy()
            return

        # 反馈内容输入
        tk.Label(self, text="反馈内容:", bg="#f0f5f9").pack(pady=10, padx=20, anchor=tk.W)
        self.feedback_text = tk.Text(self, width=50, height=15)
        self.feedback_text.pack(pady=10, padx=20)

        # 提交按钮
        tk.Button(self, text="提交反馈", command=self.submit_feedback,
                  bg="#006699", fg="white").pack(pady=10)

    def submit_feedback(self):
        feedback = self.feedback_text.get("1.0", tk.END).strip()
        if not feedback:
            messagebox.showinfo("提示", "请输入反馈内容")
            return

        conn = get_db_conn("feedback_db")  # 使用新的 feedback_db 数据库
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                insert_sql = "INSERT INTO user_feedback (user_id, feedback_content, feedback_date) VALUES (%s, %s, %s)"
                feedback_date = datetime.now()
                cursor.execute(insert_sql, (self.user_id, feedback, feedback_date))
                conn.commit()
                messagebox.showinfo("成功", "反馈提交成功")
                self.destroy()
        except pymysql.MySQLError as e:
            conn.rollback()
            messagebox.showerror("提交失败", f"错误：{str(e)}")
        finally:
            conn.close()


# ----------------- 图书查询窗口（强化多条件查询） -----------------
class BookQueryWindow(tk.Toplevel):
    def __init__(self, parent, student_id):
        super().__init__(parent)
        self.title("图书查询")
        self.geometry("800x600")
        self.configure(bg="#f0f5f9")
        self.student_id = student_id

        # 查询条件输入框
        self.create_search_filters()

        # 创建表格
        columns = ("book_id", "title", "author", "category", "status")
        self.book_tree = ttk.Treeview(self, columns=columns, show="headings")

        # 设置列标题
        for col in columns:
            self.book_tree.heading(col, text=col)
            self.book_tree.column(col, width=120, anchor=tk.CENTER)

        self.book_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 按钮框架
        btn_frame = tk.Frame(self, bg="#f0f5f9")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="刷新/查询", command=self.query_books, bg="#993333", fg="white").pack(side=tk.LEFT,
                                                                                                        padx=5)
        tk.Button(btn_frame, text="借阅", command=self.borrow_book, bg="#006699", fg="white").pack(side=tk.LEFT, padx=5)

        # 初始加载图书信息
        self.query_books()

    def create_search_filters(self):
        """创建多条件查询输入框"""
        filter_frame = tk.Frame(self, bg="#f0f5f9")
        filter_frame.pack(pady=10, padx=20, anchor=tk.W)

        # 书名
        tk.Label(filter_frame, text="书名:", bg="#f0f5f9").pack(side=tk.LEFT, padx=5)
        self.title_var = tk.StringVar()
        tk.Entry(filter_frame, textvariable=self.title_var, width=15).pack(side=tk.LEFT, padx=5)

        # 作者
        tk.Label(filter_frame, text="作者:", bg="#f0f5f9").pack(side=tk.LEFT, padx=5)
        self.author_var = tk.StringVar()
        tk.Entry(filter_frame, textvariable=self.author_var, width=15).pack(side=tk.LEFT, padx=5)

        # 分类
        tk.Label(filter_frame, text="分类:", bg="#f0f5f9").pack(side=tk.LEFT, padx=5)
        self.category_var = tk.StringVar()
        tk.Entry(filter_frame, textvariable=self.category_var, width=15).pack(side=tk.LEFT, padx=5)

        # 状态
        tk.Label(filter_frame, text="状态:", bg="#f0f5f9").pack(side=tk.LEFT, padx=5)
        self.status_var = tk.StringVar(value="可借阅")  # 默认查可借阅
        status_choices = ["可借阅", "已借出", "维修中", "其他"]
        ttk.Combobox(filter_frame, textvariable=self.status_var, values=status_choices, width=12).pack(side=tk.LEFT,
                                                                                                       padx=5)

    def query_books(self):
        """多条件查询图书"""
        # 清空表格
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)

        # 拼接查询条件
        conditions = []
        params = []

        title = self.title_var.get().strip()
        if title:
            conditions.append("title LIKE %s")
            params.append(f"%{title}%")

        author = self.author_var.get().strip()
        if author:
            conditions.append("author LIKE %s")
            params.append(f"%{author}%")

        category = self.category_var.get().strip()
        if category:
            conditions.append("category LIKE %s")
            params.append(f"%{category}%")

        status = self.status_var.get().strip()
        if status and status != "其他":
            conditions.append("status = %s")
            params.append(status)
        elif status == "其他":
            conditions.append("status NOT IN ('可借阅', '已借出')")  # 自定义“其他”逻辑

        # 组装SQL
        base_sql = "SELECT * FROM books"
        if conditions:
            base_sql += " WHERE " + " AND ".join(conditions)

        conn = get_db_conn("library")
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                cursor.execute(base_sql, tuple(params))
                books = cursor.fetchall()

                for book in books:
                    self.book_tree.insert("", tk.END, values=(
                        book["book_id"],
                        book["title"],
                        book["author"],
                        book["category"],
                        book["status"]
                    ))
        except pymysql.MySQLError as e:
            messagebox.showerror("查询失败", f"错误：{str(e)}")
        finally:
            conn.close()

    def borrow_book(self):
        selected_item = self.book_tree.selection()
        if not selected_item:
            messagebox.showinfo("提示", "请选择要借阅的图书")
            return

        book_id = self.book_tree.item(selected_item, "values")[0]
        conn = get_db_conn("library")
        if not conn:
            return

        try:
            # 检查用户是否已经借阅了三本书
            with conn.cursor() as cursor:
                sql = "SELECT COUNT(*) as count FROM borrow_records WHERE student_id = %s AND return_date IS NULL"
                cursor.execute(sql, (self.student_id,))
                result = cursor.fetchone()
                if result["count"] >= 3:
                    messagebox.showinfo("提示", "您已经借阅了三本书，不能再借")
                    return

            # 检查图书是否可借阅
            with conn.cursor() as cursor:
                sql = "SELECT status FROM books WHERE book_id = %s"
                cursor.execute(sql, (book_id,))
                book = cursor.fetchone()
                if book["status"] != "可借阅":
                    messagebox.showinfo("提示", "该图书不可借阅")
                    return

            # 更新图书状态为“已借出”
            with conn.cursor() as cursor:
                sql = "UPDATE books SET status = '已借出' WHERE book_id = %s"
                cursor.execute(sql, (book_id,))

            # 插入借阅记录
            borrow_date = datetime.now().strftime("%Y-%m-%d")
            due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            with conn.cursor() as cursor:
                sql = "INSERT INTO borrow_records (student_id, book_id, borrow_date, due_date, return_date) VALUES (%s, %s, %s, %s, NULL)"
                cursor.execute(sql, (self.student_id, book_id, borrow_date, due_date))

            conn.commit()
            messagebox.showinfo("成功", "借阅成功，请在规定时间内归还")
            self.query_books()
        except pymysql.MySQLError as e:
            conn.rollback()
            messagebox.showerror("借阅失败", f"错误：{str(e)}")
        finally:
            conn.close()


# ----------------- 还书窗口 -----------------
class ReturnBookWindow(tk.Toplevel):
    def __init__(self, parent, student_id):
        super().__init__(parent)
        self.title("还书")
        self.geometry("800x600")
        self.configure(bg="#f0f5f9")
        self.student_id = student_id

        # 添加还书提醒
        self.show_return_reminder()

        # 创建表格
        columns = ("book_id", "title", "author", "category", "borrow_date", "due_date")
        self.book_tree = ttk.Treeview(self, columns=columns, show="headings")

        # 设置列标题
        for col in columns:
            self.book_tree.heading(col, text=col)
            self.book_tree.column(col, width=120, anchor=tk.CENTER)

        self.book_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 归还按钮
        tk.Button(self, text="归还", command=self.return_book, bg="#006699", fg="white").pack(pady=10)

        # 加载用户当前借阅的图书
        self.load_borrowed_books()

    def show_return_reminder(self):
        """显示还书提醒信息"""
        reminder_frame = tk.Frame(self, bg="#FFE6CC", bd=1, relief=tk.SOLID)
        reminder_frame.pack(fill=tk.X, padx=20, pady=10)

        reminder_text = """
        重要提醒：
        1. 请在归还期限内归还图书，逾期未还将暂停借阅权限。
        2. 若图书丢失或严重损坏，需按图书原价赔偿。
        3. 请爱护图书，保持图书整洁。
        """

        reminder_label = tk.Label(
            reminder_frame,
            text=reminder_text,
            bg="#FFE6CC",
            fg="#993300",
            font=("微软雅黑", 10, "bold"),
            justify=tk.LEFT,
            padx=10,
            pady=10
        )
        reminder_label.pack(fill=tk.X)

        # 添加确认按钮
        confirm_btn = tk.Button(
            reminder_frame,
            text="我已了解",
            bg="#006699",
            fg="white",
            command=lambda: reminder_frame.pack_forget(),
            width=10
        )
        confirm_btn.pack(anchor=tk.E, padx=10, pady=5)

    def load_borrowed_books(self):
        # 清空表格
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)

        conn = get_db_conn("library")
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                sql = """
                SELECT b.book_id, b.title, b.author, b.category, br.borrow_date, br.due_date
                FROM books b
                JOIN borrow_records br ON b.book_id = br.book_id
                WHERE br.student_id = %s AND br.return_date IS NULL
                """
                cursor.execute(sql, (self.student_id,))
                books = cursor.fetchall()

                for book in books:
                    self.book_tree.insert("", tk.END, values=(
                        book["book_id"],
                        book["title"],
                        book["author"],
                        book["category"],
                        book["borrow_date"],
                        book["due_date"]
                    ))
        except pymysql.MySQLError as e:
            messagebox.showerror("查询失败", f"错误：{str(e)}")
        finally:
            conn.close()

    def return_book(self):
        selected_item = self.book_tree.selection()
        if not selected_item:
            messagebox.showinfo("提示", "请选择要归还的图书")
            return

        book_id = self.book_tree.item(selected_item, "values")[0]
        conn = get_db_conn("library")
        if not conn:
            return

        try:
            # 更新图书状态为“可借阅”
            with conn.cursor() as cursor:
                sql = "UPDATE books SET status = '可借阅' WHERE book_id = %s"
                cursor.execute(sql, (book_id,))

            # 更新借阅记录中的归还日期
            return_date = datetime.now().date()  # 获取当前日期（date 类型）
            with conn.cursor() as cursor:
                sql = "UPDATE borrow_records SET return_date = %s WHERE student_id = %s AND book_id = %s AND return_date IS NULL"
                cursor.execute(sql, (return_date, self.student_id, book_id))

            # 检查是否逾期归还
            with conn.cursor() as cursor:
                sql = "SELECT due_date FROM borrow_records WHERE student_id = %s AND book_id = %s AND return_date = %s"
                cursor.execute(sql, (self.student_id, book_id, return_date))
                result = cursor.fetchone()
                if result:
                    due_date = result["due_date"]  # 本身是 datetime.date 类型
                    if datetime.now().date() > due_date:
                        messagebox.showinfo("提示", "您已逾期归还，暂时不能再借书")
                    else:
                        messagebox.showinfo("成功", "归还成功")

            conn.commit()
            self.load_borrowed_books()
        except pymysql.MySQLError as e:
            conn.rollback()
            messagebox.showerror("归还失败", f"错误：{str(e)}")
        finally:
            conn.close()


# ----------------- 借阅图书窗口 -----------------
class BorrowBookWindow(tk.Toplevel):
    def __init__(self, parent, student_id):
        super().__init__(parent)
        self.title("借阅图书")
        self.geometry("500x400")
        self.configure(bg="#f0f5f9")
        self.student_id = student_id
        # 用于存储查询到的图书信息，避免重复查询
        self.book_info = None

        # 标题
        tk.Label(self, text="图书借阅", font=("微软雅黑", 16, "bold"),
                 bg="#f0f5f9", fg="#006699").pack(pady=20)

        # book_id输入框
        input_frame = tk.Frame(self, bg="#f0f5f9")
        input_frame.pack(pady=10, padx=20)

        tk.Label(input_frame, text="图书ID:", bg="#f0f5f9").pack(side=tk.LEFT, padx=5)
        self.book_id_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=self.book_id_var, width=15).pack(side=tk.LEFT, padx=5)

        tk.Button(input_frame, text="查询图书", command=self.query_book,
                  bg="#993333", fg="white").pack(side=tk.LEFT, padx=5)

        # 图书信息显示区域
        self.info_frame = tk.Frame(self, bg="#f0f5f9", bd=1, relief=tk.SUNKEN)
        self.info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.info_label = tk.Label(self.info_frame, text="请输入图书ID并查询",
                                   bg="#f0f5f9", justify=tk.LEFT, wraplength=400)
        self.info_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 借阅按钮
        self.borrow_btn = tk.Button(self, text="确认借阅", command=self.confirm_borrow,
                                    bg="#006699", fg="white", state=tk.DISABLED)
        self.borrow_btn.pack(pady=10)

    def query_book(self):
        """根据book_id查询图书信息"""
        book_id = self.book_id_var.get().strip()
        if not book_id:
            messagebox.showinfo("提示", "请输入图书ID")
            return

        conn = get_db_conn("library")
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                sql = "SELECT book_id, title, author, category, status FROM books WHERE book_id = %s"
                cursor.execute(sql, (book_id,))
                self.book_info = cursor.fetchone()

                if not self.book_info:
                    messagebox.showinfo("提示", f"未找到ID为{book_id}的图书")
                    self.info_label.config(text="未找到图书信息")
                    self.borrow_btn.config(state=tk.DISABLED)
                    return

                # 显示图书信息
                info_text = f"图书ID: {self.book_info['book_id']}\n"
                info_text += f"书名: {self.book_info['title']}\n"
                info_text += f"作者: {self.book_info['author']}\n"
                info_text += f"分类: {self.book_info['category']}\n"
                info_text += f"状态: {self.book_info['status']}\n"
                info_text += f"简介: {self.book_info.get('description', '无简介')}"

                self.info_label.config(text=info_text)
                self.borrow_btn.config(state=tk.NORMAL)

        except pymysql.MySQLError as e:
            messagebox.showerror("查询失败", f"错误：{str(e)}")
        finally:
            conn.close()

    def confirm_borrow(self):
        """确认借阅图书"""
        if not self.book_info:
            messagebox.showinfo("提示", "请先查询图书信息")
            return

        book_id = self.book_id_var.get().strip()
        if not book_id:
            messagebox.showinfo("提示", "请输入图书ID")
            return

        conn = get_db_conn("library")
        if not conn:
            return

        try:
            # 检查用户是否已经借阅了三本书
            with conn.cursor() as cursor:
                sql = "SELECT COUNT(*) as count FROM borrow_records WHERE student_id = %s AND return_date IS NULL"
                cursor.execute(sql, (self.student_id,))
                result = cursor.fetchone()
                if result["count"] >= 3:
                    messagebox.showinfo("提示", "您已经借阅了三本书，不能再借")
                    return

            # 检查图书是否可借阅，使用已查询的book_info
            if self.book_info["status"] != "可借阅":
                messagebox.showinfo("提示", "该图书不可借阅")
                return

            # 显示确认对话框
            confirm = messagebox.askyesno("确认借阅", f"确定要借阅《{self.book_info['title']}》吗？")
            if not confirm:
                return

            # 更新图书状态为“已借出”
            with conn.cursor() as cursor:
                sql = "UPDATE books SET status = '已借出' WHERE book_id = %s"
                cursor.execute(sql, (book_id,))

            # 插入借阅记录
            borrow_date = datetime.now().strftime("%Y-%m-%d")
            due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            with conn.cursor() as cursor:
                sql = "INSERT INTO borrow_records (student_id, book_id, borrow_date, due_date, return_date) VALUES (%s, %s, %s, %s, NULL)"
                cursor.execute(sql, (self.student_id, book_id, borrow_date, due_date))

            conn.commit()
            messagebox.showinfo("成功", "借阅成功，请在规定时间内归还")
            self.destroy()

        except pymysql.MySQLError as e:
            conn.rollback()
            messagebox.showerror("借阅失败", f"错误：{str(e)}")
        finally:
            conn.close()

# 修改用户面板，添加借阅图书按钮
def show_user_dashboard(root, student_id):
    user_dash = tk.Toplevel(root)
    user_dash.title(f"用户面板 - {student_id}")
    user_dash.geometry("800x600")  # 调整窗口大小为垂直布局
    user_dash.configure(bg="#f0f5f9")

    # 标题（居中显示）
    tk.Label(
        user_dash,
        text="用户功能面板",
        font=("微软雅黑", 24, "bold"),
        fg="#006699",
        bg="#f0f5f9"
    ).pack(pady=20)

    # 功能按钮区（垂直排列）
    button_frame = tk.Frame(user_dash, bg="#f0f5f9")
    button_frame.pack(pady=20, expand=True)  # 垂直居中显示

    # 按钮通用样式
    btn_style = {
        "font": ("微软雅黑", 14),
        "bg": "#006699",
        "fg": "white",
        "relief": "flat",
        "width": 15,  # 统一按钮宽度
        "height": 2,  # 统一按钮高度
        "activebackground": "#004C80"  # 鼠标悬停效果
    }

    # 垂直排列的功能按钮
    tk.Button(
        button_frame,
        text="查询图书",
        command=lambda: BookQueryWindow(user_dash, student_id),
        **btn_style
    ).pack(pady=10, fill=tk.X)  # 水平填满，垂直间距10

    tk.Button(
        button_frame,
        text="借阅图书",  # 新增的借阅图书按钮
        command=lambda: BorrowBookWindow(user_dash, student_id),
        **btn_style
    ).pack(pady=10, fill=tk.X)

    tk.Button(
        button_frame,
        text="用户反馈",
        command=lambda: UserFeedbackWindow(user_dash, student_id),
        **btn_style
    ).pack(pady=10, fill=tk.X)

    tk.Button(
        button_frame,
        text="还书",
        command=lambda: ReturnBookWindow(user_dash, student_id),
        **btn_style
    ).pack(pady=10, fill=tk.X)

    # 退出按钮（底部单独放置）
    tk.Button(
        user_dash,
        text="退出登录",
        command=user_dash.destroy,
        font=("微软雅黑", 12),
        bg="#E74C3C",  # 红色按钮，突出退出功能
        fg="white",
        width=12,
        height=1
    ).pack(side=tk.BOTTOM, pady=20)  # 底部对齐，增加底部间距
