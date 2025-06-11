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

        # 搜索框架 - 新增搜索条件选择
        search_frame = tk.Frame(self, bg="#f0f5f9")
        search_frame.pack(pady=10)

        # 搜索条件下拉框
        tk.Label(search_frame, text="搜索条件:", bg="#f0f5f9").pack(side=tk.LEFT, padx=5)
        self.search_type = tk.StringVar(value="title")  # 默认按书名搜索
        search_types = {"书名": "title", "类型": "category", "状态": "status", "书号": "book_id"}
        search_type_combo = ttk.Combobox(search_frame, textvariable=self.search_type, values=list(search_types.keys()),
                                        width=10, state="readonly")
        search_type_combo.pack(side=tk.LEFT, padx=5)

        # 搜索输入框
        tk.Label(search_frame, text="关键词:", bg="#f0f5f9").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        # 状态筛选
        tk.Label(search_frame, text="状态:", bg="#f0f5f9").pack(side=tk.LEFT, padx=5)
        self.status_var = tk.StringVar(value="全部")
        status_options = ["全部", "可借阅", "已借出"]
        status_combo = ttk.Combobox(search_frame, textvariable=self.status_var, values=status_options,
                                   width=8, state="readonly")
        status_combo.pack(side=tk.LEFT, padx=5)

        # 搜索按钮
        tk.Button(search_frame, text="搜索", command=self.search_books, bg="#006699", fg="white").pack(side=tk.LEFT, padx=5)

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
        """搜索图书 - 支持多条件筛选"""
        # 获取搜索条件
        search_type = self.search_type.get()  # 获取搜索类型（书名、类型等）
        keyword = self.search_entry.get().strip()
        status = self.status_var.get()  # 获取状态筛选条件

        # 清空表格
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)

        # 从数据库加载
        conn = get_db_conn("library")
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                # 构建基础SQL和参数列表
                sql = "SELECT * FROM books WHERE 1=1"
                params = []

                # 添加搜索条件
                if keyword:
                    # 根据搜索类型拼接不同的WHERE条件
                    if search_type == "书名":
                        sql += " AND title LIKE %s"
                    elif search_type == "类型":
                        sql += " AND category LIKE %s"
                    elif search_type == "书号":
                        sql += " AND book_id = %s"  # 书号精确匹配
                    params.append(f"%{keyword}%" if search_type != "书号" else keyword)

                # 添加状态筛选
                if status != "全部":
                    sql += " AND status = %s"
                    params.append(status)

                # 执行查询
                cursor.execute(sql, params)
                books = cursor.fetchall()

                # 显示结果
                for book in books:
                    self.book_tree.insert("", tk.END, values=(
                        book["book_id"], book["title"],
                        book["author"], book["category"],
                        book["status"]
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

        # 创建表格，定义列
        columns = ("borrow_id", "book_id", "title", "author", "category", "borrow_date", "due_date", "return_date")
        self.borrow_tree = ttk.Treeview(self, columns=columns, show="headings")

        # 设置列标题和宽度，优化显示
        self.borrow_tree.heading("borrow_id", text="借阅ID")
        self.borrow_tree.heading("book_id", text="图书ID")
        self.borrow_tree.heading("title", text="书名")
        self.borrow_tree.heading("author", text="作者")
        self.borrow_tree.heading("category", text="分类")
        self.borrow_tree.heading("borrow_date", text="借阅日期")
        self.borrow_tree.heading("due_date", text="应还日期")
        self.borrow_tree.heading("return_date", text="归还日期")

        self.borrow_tree.column("borrow_id", width=80, anchor=tk.CENTER)
        self.borrow_tree.column("book_id", width=80, anchor=tk.CENTER)
        self.borrow_tree.column("title", width=180, anchor=tk.W)
        self.borrow_tree.column("author", width=120, anchor=tk.W)
        self.borrow_tree.column("category", width=100, anchor=tk.W)
        self.borrow_tree.column("borrow_date", width=120, anchor=tk.CENTER)
        self.borrow_tree.column("due_date", width=120, anchor=tk.CENTER)
        self.borrow_tree.column("return_date", width=120, anchor=tk.CENTER)

        self.borrow_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 按钮框架，放置刷新和归还按钮
        btn_frame = tk.Frame(self, bg="#f0f5f9")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="刷新", command=self.refresh_borrows, bg="#006699", fg="white").pack(side=tk.LEFT,
                                                                                                       padx=5)
        tk.Button(btn_frame, text="归还选中图书", command=self.show_return_confirmation, bg="#006699", fg="white").pack(
            side=tk.LEFT, padx=5)

        # 初始加载借阅记录
        self.refresh_borrows()

    def refresh_borrows(self):
        """刷新借阅记录表格，加载当前学生已借出（未归还）的图书数据"""
        # 清空表格现有数据
        for item in self.borrow_tree.get_children():
            self.borrow_tree.delete(item)

        # 获取数据库连接，连接 borrow_records_db 数据库
        conn = get_db_conn("borrow_records_db")
        if not conn:
            return

        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                # 联合查询，关联 borrow_records 和 library.books 表
                # 筛选条件：学生ID匹配、return_date 为 NULL（未归还，即已借出状态 ）
                sql = """
                SELECT b.borrow_id, b.book_id, bo.title, bo.author, bo.category, 
                       b.borrow_date, b.due_date, b.return_date 
                FROM borrow_records b
                JOIN library.books bo ON b.book_id = bo.book_id  
                WHERE b.student_id = %s AND b.return_date IS NULL
                ORDER BY b.borrow_date DESC
                """
                cursor.execute(sql, (self.student_id,))
                borrows = cursor.fetchall()  # 获取查询结果

                # 遍历结果，格式化日期并插入表格
                for borrow in borrows:
                    # 处理日期字段，若为 None 则显示空字符串
                    borrow_date = borrow["borrow_date"].strftime("%Y-%m-%d") if borrow["borrow_date"] else ""
                    due_date = borrow["due_date"].strftime("%Y-%m-%d") if borrow["due_date"] else ""
                    return_date = borrow["return_date"].strftime("%Y-%m-%d") if borrow["return_date"] else ""

                    self.borrow_tree.insert("", tk.END, values=(
                        borrow["borrow_id"],
                        borrow["book_id"],
                        borrow["title"],
                        borrow["author"],
                        borrow["category"],
                        borrow_date,
                        due_date,
                        return_date
                    ))
        except pymysql.MySQLError as e:
            messagebox.showerror("查询失败", f"数据库错误：{str(e)}")
        finally:
            conn.close()  # 关闭数据库连接

    def show_return_confirmation(self):
        """显示归还确认对话框，逻辑保持不变"""
        selected_item = self.borrow_tree.selection()
        if not selected_item:
            messagebox.showinfo("提示", "请先选择要归还的图书")
            return

        values = self.borrow_tree.item(selected_item[0])["values"]
        self.selected_borrow_id = values[0]
        self.selected_book_id = values[1]
        self.selected_title = values[2]
        self.selected_author = values[3]
        self.selected_category = values[4]

        # 创建确认对话框
        self.confirm_window = tk.Toplevel(self)
        self.confirm_window.title("确认归还图书")
        self.confirm_window.geometry("400x300")
        self.confirm_window.configure(bg="#f0f5f9")
        self.confirm_window.transient(self)
        self.confirm_window.grab_set()

        # 显示图书信息
        tk.Label(self.confirm_window, text="图书信息", font=("SimHei", 12, "bold"), bg="#f0f5f9").pack(pady=10)

        info_frame = tk.Frame(self.confirm_window, bg="#f0f5f9")
        info_frame.pack(pady=10)

        tk.Label(info_frame, text="书名:", bg="#f0f5f9").grid(row=0, column=0, sticky=tk.W, pady=5)
        tk.Label(info_frame, text=self.selected_title, bg="#f0f5f9").grid(row=0, column=1, sticky=tk.W, pady=5)

        tk.Label(info_frame, text="作者:", bg="#f0f5f9").grid(row=1, column=0, sticky=tk.W, pady=5)
        tk.Label(info_frame, text=self.selected_author, bg="#f0f5f9").grid(row=1, column=1, sticky=tk.W, pady=5)

        tk.Label(info_frame, text="分类:", bg="#f0f5f9").grid(row=2, column=0, sticky=tk.W, pady=5)
        tk.Label(info_frame, text=self.selected_category, bg="#f0f5f9").grid(row=2, column=1, sticky=tk.W, pady=5)

        # 归还原因输入
        tk.Label(self.confirm_window, text="归还原因:", bg="#f0f5f9").pack(pady=5, padx=20, anchor=tk.W)
        self.return_reason = tk.Text(self.confirm_window, width=40, height=3)
        self.return_reason.pack(pady=5, padx=20)

        # 按钮框架
        btn_frame = tk.Frame(self.confirm_window, bg="#f0f5f9")
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="确认归还", command=self.confirm_return, bg="#006699", fg="white").pack(side=tk.LEFT,
                                                                                                          padx=10)
        tk.Button(btn_frame, text="取消", command=self.confirm_window.destroy, bg="#993333", fg="white").pack(
            side=tk.LEFT, padx=10)

    def confirm_return(self):
        """确认归还操作，更新数据库逻辑（可根据实际需求完善）"""
        return_reason = self.return_reason.get("1.0", tk.END).strip()

        if messagebox.askyesno("确认", f"确定要归还《{self.selected_title}》吗？"):
            # 连接相关数据库
            borrow_conn = get_db_conn("borrow_records_db")
            library_conn = get_db_conn("library")

            if not borrow_conn or not library_conn:
                if borrow_conn:
                    borrow_conn.close()
                if library_conn:
                    library_conn.close()
                return

            try:
                with borrow_conn.cursor() as borrow_cursor, library_conn.cursor() as library_cursor:
                    # 更新 borrow_records 表的归还日期
                    return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    update_borrow_sql = "UPDATE borrow_records SET return_date = %s WHERE borrow_id = %s"
                    borrow_cursor.execute(update_borrow_sql, (return_date, self.selected_borrow_id))

                    # 更新 books 表的图书状态为可借阅
                    update_book_sql = "UPDATE books SET status = 0, last_return_time = %s WHERE book_id = %s"
                    library_cursor.execute(update_book_sql, (return_date, self.selected_book_id))

                    # 若有归还原因，插入日志（假设存在 return_logs 表 ）
                    if return_reason:
                        log_sql = "INSERT INTO return_logs (book_id, student_id, return_date, reason) VALUES (%s, %s, %s, %s)"
                        library_cursor.execute(log_sql,
                                               (self.selected_book_id, self.student_id, return_date, return_reason))

                    # 提交事务
                    borrow_conn.commit()
                    library_conn.commit()

                    messagebox.showinfo("成功", "归还图书成功")
                    self.refresh_borrows()  # 刷新表格
                    self.confirm_window.destroy()  # 关闭确认窗口
            except pymysql.MySQLError as e:
                # 回滚事务
                borrow_conn.rollback()
                library_conn.rollback()
                messagebox.showerror("归还失败", f"数据库错误：{str(e)}")
            finally:
                borrow_conn.close()
                library_conn.close()

            # ----------------- 用户反馈窗口 -----------------
class UserFeedbackWindow(tk.Toplevel):
    def __init__(self, parent, student_id):
        super().__init__(parent)
        self.title("用户反馈")
        self.geometry("500x400")
        self.configure(bg="#f0f5f9")
        self.student_id = student_id  # 这里的 student_id 要和 user_table 的 student_id 一致
        self.user_id = None

        # 修复：明确指定数据库名，避免 get_db_conn 可能的歧义
        conn = get_db_conn("user_db")  # 强制连接 user_db
        if conn:
            try:
                with conn.cursor() as cursor:
                    # 确保 SQL 条件正确：用 student_id 查 user_id
                    sql = "SELECT user_id FROM user_table WHERE student_id = %s"
                    cursor.execute(sql, (self.student_id,))
                    user = cursor.fetchone()
                    if user:
                        self.user_id = user["user_id"]
                    else:
                        messagebox.showerror("错误", "未找到该学生的用户信息")
                        self.destroy()
                        return
            except pymysql.MySQLError as e:
                messagebox.showerror("查询失败", f"错误：{str(e)}")
                self.destroy()
                return
            finally:
                conn.close()
        else:
            self.destroy()
            return

        tk.Label(self, text="反馈内容:", bg="#f0f5f9").pack(pady=10, padx=20, anchor=tk.W)
        self.feedback_text = tk.Text(self, width=50, height=15)
        self.feedback_text.pack(pady=10, padx=20)
        tk.Button(self, text="提交反馈", command=self.submit_feedback, bg="#006699", fg="white").pack(pady=10)

    def submit_feedback(self):
        content = self.feedback_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showinfo("提示", "反馈内容不能为空")
            return

        # 修复：明确指定连接 feedback_db
        conn = get_db_conn("feedback_db")
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # 确保 feedback 表字段匹配：只有 user_id、content、create_time
                sql = "INSERT INTO feedback (user_id, content, create_time) VALUES (%s, %s, %s)"
                cursor.execute(sql, (self.user_id, content, create_time))
                conn.commit()
                messagebox.showinfo("成功", "反馈提交成功，感谢您的反馈！")
                self.destroy()
        except pymysql.MySQLError as e:
            conn.rollback()
            # 打印详细错误，方便排查（比如表结构不匹配、字段缺失）
            messagebox.showerror("提交失败", f"错误代码：{e.args[0]}\n错误信息：{e.args[1]}")
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