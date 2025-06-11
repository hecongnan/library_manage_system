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


# ----------------- 读者信息管理窗口 -----------------
class ReaderManagerWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("读者信息管理")
        self.geometry("800x600")
        self.configure(bg="#f0f5f9")

        # 创建表格
        columns = ("user_id", "user_name", "gender", "student_id", "phone")
        self.reader_tree = ttk.Treeview(self, columns=columns, show="headings")

        # 设置列标题
        for col in columns:
            self.reader_tree.heading(col, text=col)
            self.reader_tree.column(col, width=120, anchor=tk.CENTER)

        self.reader_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 按钮框架
        btn_frame = tk.Frame(self, bg="#f0f5f9")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="刷新", command=self.refresh_readers, bg="#993333", fg="white").pack(side=tk.LEFT,
                                                                                                       padx=5)
        tk.Button(btn_frame, text="添加读者", command=self.add_reader, bg="#993333", fg="white").pack(side=tk.LEFT,
                                                                                                      padx=5)
        tk.Button(btn_frame, text="修改读者", command=self.edit_reader, bg="#993333", fg="white").pack(side=tk.LEFT,
                                                                                                       padx=5)
        tk.Button(btn_frame, text="删除读者", command=self.delete_reader, bg="#993333", fg="white").pack(side=tk.LEFT,
                                                                                                         padx=5)

        # 初始加载读者信息
        self.refresh_readers()

    def refresh_readers(self):
        """刷新读者表格"""
        # 清空表格
        for item in self.reader_tree.get_children():
            self.reader_tree.delete(item)

        # 从数据库加载
        conn = get_db_conn("user_db")
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM user_table"
                cursor.execute(sql)
                readers = cursor.fetchall()

                for reader in readers:
                    self.reader_tree.insert("", tk.END, values=(
                        reader["user_id"],
                        reader["user_name"],
                        reader["gender"],
                        reader["student_id"],
                        reader["phone"]
                    ))
        except pymysql.MySQLError as e:
            messagebox.showerror("查询失败", f"错误：{str(e)}")
        finally:
            conn.close()

    def add_reader(self):
        """添加读者"""
        # 创建添加读者窗口
        add_window = tk.Toplevel(self)
        add_window.title("添加读者")
        add_window.geometry("400x300")
        add_window.configure(bg="#f0f5f9")

        # 创建输入字段
        tk.Label(add_window, text="姓名:", bg="#f0f5f9").grid(row=0, column=0, padx=20, pady=10, sticky=tk.W)
        name_entry = tk.Entry(add_window, width=30)
        name_entry.grid(row=0, column=1, padx=20, pady=10)

        tk.Label(add_window, text="性别:", bg="#f0f5f9").grid(row=1, column=0, padx=20, pady=10, sticky=tk.W)
        gender_var = tk.StringVar(value="男")
        tk.Radiobutton(add_window, text="男", variable=gender_var, value="男", bg="#f0f5f9").grid(row=1, column=1,
                                                                                                  sticky=tk.W)
        tk.Radiobutton(add_window, text="女", variable=gender_var, value="女", bg="#f0f5f9").grid(row=1, column=1)

        tk.Label(add_window, text="学号:", bg="#f0f5f9").grid(row=2, column=0, padx=20, pady=10, sticky=tk.W)
        student_id_entry = tk.Entry(add_window, width=30)
        student_id_entry.grid(row=2, column=1, padx=20, pady=10)

        tk.Label(add_window, text="电话:", bg="#f0f5f9").grid(row=3, column=0, padx=20, pady=10, sticky=tk.W)
        phone_entry = tk.Entry(add_window, width=30)
        phone_entry.grid(row=3, column=1, padx=20, pady=10)

        def save_reader():
            name = name_entry.get().strip()
            gender = gender_var.get()
            student_id = student_id_entry.get().strip()
            phone = phone_entry.get().strip()

            if not all([name, student_id, phone]):
                messagebox.showerror("错误", "所有字段都必须填写")
                return

            conn = get_db_conn("user_db")
            if not conn:
                return

            try:
                with conn.cursor() as cursor:
                    sql = """
                    INSERT INTO user_table (user_name, gender, student_id, phone)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql, (name, gender, student_id, phone))
                    conn.commit()
                    messagebox.showinfo("成功", "读者添加成功")
                    add_window.destroy()
                    self.refresh_readers()
            except pymysql.MySQLError as e:
                conn.rollback()
                messagebox.showerror("添加失败", f"错误：{str(e)}")
            finally:
                conn.close()

        tk.Button(add_window, text="保存", command=save_reader, bg="#006699", fg="white").grid(row=4, column=0,
                                                                                               columnspan=2, pady=20)

    def edit_reader(self):
        """修改读者信息"""
        selected_item = self.reader_tree.selection()
        if not selected_item:
            messagebox.showinfo("提示", "请先选择一个读者")
            return

        # 获取选中读者的信息
        values = self.reader_tree.item(selected_item[0], "values")
        user_id = values[0]

        # 创建修改读者窗口
        edit_window = tk.Toplevel(self)
        edit_window.title("修改读者")
        edit_window.geometry("400x300")
        edit_window.configure(bg="#f0f5f9")

        # 创建输入字段
        tk.Label(edit_window, text="姓名:", bg="#f0f5f9").grid(row=0, column=0, padx=20, pady=10, sticky=tk.W)
        name_entry = tk.Entry(edit_window, width=30)
        name_entry.insert(0, values[1])
        name_entry.grid(row=0, column=1, padx=20, pady=10)

        tk.Label(edit_window, text="性别:", bg="#f0f5f9").grid(row=1, column=0, padx=20, pady=10, sticky=tk.W)
        gender_var = tk.StringVar(value=values[2])
        tk.Radiobutton(edit_window, text="男", variable=gender_var, value="男", bg="#f0f5f9").grid(row=1, column=1,
                                                                                                   sticky=tk.W)
        tk.Radiobutton(edit_window, text="女", variable=gender_var, value="女", bg="#f0f5f9").grid(row=1, column=1)

        tk.Label(edit_window, text="学号:", bg="#f0f5f9").grid(row=2, column=0, padx=20, pady=10, sticky=tk.W)
        student_id_entry = tk.Entry(edit_window, width=30)
        student_id_entry.insert(0, values[3])
        student_id_entry.grid(row=2, column=1, padx=20, pady=10)

        tk.Label(edit_window, text="电话:", bg="#f0f5f9").grid(row=3, column=0, padx=20, pady=10, sticky=tk.W)
        phone_entry = tk.Entry(edit_window, width=30)
        phone_entry.insert(0, values[4])
        phone_entry.grid(row=3, column=1, padx=20, pady=10)

        def update_reader():
            name = name_entry.get().strip()
            gender = gender_var.get()
            student_id = student_id_entry.get().strip()
            phone = phone_entry.get().strip()

            if not all([name, student_id, phone]):
                messagebox.showerror("错误", "所有字段都必须填写")
                return

            conn = get_db_conn("user_db")
            if not conn:
                return

            try:
                with conn.cursor() as cursor:
                    sql = """
                    UPDATE user_table
                    SET user_name = %s, gender = %s, student_id = %s, phone = %s
                    WHERE user_id = %s
                    """
                    cursor.execute(sql, (name, gender, student_id, phone, user_id))
                    conn.commit()
                    messagebox.showinfo("成功", "读者信息更新成功")
                    edit_window.destroy()
                    self.refresh_readers()
            except pymysql.MySQLError as e:
                conn.rollback()
                messagebox.showerror("更新失败", f"错误：{str(e)}")
            finally:
                conn.close()

        tk.Button(edit_window, text="保存", command=update_reader, bg="#006699", fg="white").grid(row=4, column=0,
                                                                                                  columnspan=2, pady=20)

    def delete_reader(self):
        """删除读者"""
        selected_item = self.reader_tree.selection()
        if not selected_item:
            messagebox.showinfo("提示", "请先选择一个读者")
            return

        # 获取选中读者的信息
        values = self.reader_tree.item(selected_item[0], "values")
        user_id = values[0]
        user_name = values[1]

        if messagebox.askyesno("确认", f"确定要删除读者 {user_name} 吗？"):
            conn = get_db_conn("user_db")
            if not conn:
                return

            try:
                with conn.cursor() as cursor:
                    # 检查该读者是否有未归还的图书
                    check_sql = """
                    SELECT COUNT(*) as count FROM library.borrow_records 
                    WHERE student_id IN (SELECT student_id FROM user_table WHERE user_id = %s)
                    AND return_date IS NULL
                    """
                    cursor.execute(check_sql, (user_id,))
                    result = cursor.fetchone()

                    if result["count"] > 0:
                        messagebox.showerror("错误", "该读者有未归还的图书，不能删除")
                        return

                    # 删除读者
                    delete_sql = "DELETE FROM user_table WHERE user_id = %s"
                    cursor.execute(delete_sql, (user_id,))
                    conn.commit()
                    messagebox.showinfo("成功", "读者删除成功")
                    self.refresh_readers()
            except pymysql.MySQLError as e:
                conn.rollback()
                messagebox.showerror("删除失败", f"错误：{str(e)}")
            finally:
                conn.close()


# ----------------- 图书信息管理窗口 -----------------
class BookManagerWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("图书信息管理")
        self.geometry("800x600")
        self.configure(bg="#f0f5f9")

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

        tk.Button(btn_frame, text="刷新", command=self.refresh_books, bg="#993333", fg="white").pack(side=tk.LEFT,
                                                                                                     padx=5)
        tk.Button(btn_frame, text="添加图书", command=self.add_book, bg="#993333", fg="white").pack(side=tk.LEFT,
                                                                                                    padx=5)
        tk.Button(btn_frame, text="修改图书", command=self.edit_book, bg="#993333", fg="white").pack(side=tk.LEFT,
                                                                                                     padx=5)
        tk.Button(btn_frame, text="删除图书", command=self.delete_book, bg="#993333", fg="white").pack(side=tk.LEFT,
                                                                                                       padx=5)

        # 初始加载图书信息
        self.refresh_books()

    def refresh_books(self):
        """刷新图书表格"""
        # 清空表格
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)

        # 从数据库加载
        conn = get_db_conn("library")
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM books"
                cursor.execute(sql)
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

    def add_book(self):
        """添加图书"""
        # 创建添加图书窗口
        add_window = tk.Toplevel(self)
        add_window.title("添加图书")
        add_window.geometry("400x300")
        add_window.configure(bg="#f0f5f9")

        # 创建输入字段
        tk.Label(add_window, text="书名:", bg="#f0f5f9").grid(row=0, column=0, padx=20, pady=10, sticky=tk.W)
        title_entry = tk.Entry(add_window, width=30)
        title_entry.grid(row=0, column=1, padx=20, pady=10)

        tk.Label(add_window, text="作者:", bg="#f0f5f9").grid(row=1, column=0, padx=20, pady=10, sticky=tk.W)
        author_entry = tk.Entry(add_window, width=30)
        author_entry.grid(row=1, column=1, padx=20, pady=10)

        tk.Label(add_window, text="类别:", bg="#f0f5f9").grid(row=2, column=0, padx=20, pady=10, sticky=tk.W)
        category_entry = tk.Entry(add_window, width=30)
        category_entry.grid(row=2, column=1, padx=20, pady=10)

        tk.Label(add_window, text="状态:", bg="#f0f5f9").grid(row=3, column=0, padx=20, pady=10, sticky=tk.W)
        status_var = tk.StringVar(value="可借阅")
        tk.Radiobutton(add_window, text="可借阅", variable=status_var, value="可借阅", bg="#f0f5f9").grid(row=3,
                                                                                                          column=1,
                                                                                                          sticky=tk.W)
        tk.Radiobutton(add_window, text="已借出", variable=status_var, value="已借出", bg="#f0f5f9").grid(row=3,
                                                                                                          column=1)

        def save_book():
            title = title_entry.get().strip()
            author = author_entry.get().strip()
            category = category_entry.get().strip()
            status = status_var.get()

            if not all([title, author, category]):
                messagebox.showerror("错误", "所有字段都必须填写")
                return

            conn = get_db_conn("library")
            if not conn:
                return

            try:
                with conn.cursor() as cursor:
                    sql = """
                    INSERT INTO books (title, author, category, status)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql, (title, author, category, status))
                    conn.commit()
                    messagebox.showinfo("成功", "图书添加成功")
                    add_window.destroy()
                    self.refresh_books()
            except pymysql.MySQLError as e:
                conn.rollback()
                messagebox.showerror("添加失败", f"错误：{str(e)}")
            finally:
                conn.close()

        tk.Button(add_window, text="保存", command=save_book, bg="#006699", fg="white").grid(row=4, column=0,
                                                                                             columnspan=2, pady=20)

    def edit_book(self):
        """修改图书信息"""
        selected_item = self.book_tree.selection()
        if not selected_item:
            messagebox.showinfo("提示", "请先选择一本图书")
            return

        # 获取选中图书的信息
        values = self.book_tree.item(selected_item[0], "values")
        book_id = values[0]

        # 创建修改图书窗口
        edit_window = tk.Toplevel(self)
        edit_window.title("修改图书")
        edit_window.geometry("400x300")
        edit_window.configure(bg="#f0f5f9")

        # 创建输入字段
        tk.Label(edit_window, text="书名:", bg="#f0f5f9").grid(row=0, column=0, padx=20, pady=10, sticky=tk.W)
        title_entry = tk.Entry(edit_window, width=30)
        title_entry.insert(0, values[1])
        title_entry.grid(row=0, column=1, padx=20, pady=10)

        tk.Label(edit_window, text="作者:", bg="#f0f5f9").grid(row=1, column=0, padx=20, pady=10, sticky=tk.W)
        author_entry = tk.Entry(edit_window, width=30)
        author_entry.insert(0, values[2])
        author_entry.grid(row=1, column=1, padx=20, pady=10)

        tk.Label(edit_window, text="类别:", bg="#f0f5f9").grid(row=2, column=0, padx=20, pady=10, sticky=tk.W)
        category_entry = tk.Entry(edit_window, width=30)
        category_entry.insert(0, values[3])
        category_entry.grid(row=2, column=1, padx=20, pady=10)

        tk.Label(edit_window, text="状态:", bg="#f0f5f9").grid(row=3, column=0, padx=20, pady=10, sticky=tk.W)
        status_var = tk.StringVar(value=values[4])
        tk.Radiobutton(edit_window, text="可借阅", variable=status_var, value="可借阅", bg="#f0f5f9").grid(row=3,
                                                                                                           column=1,
                                                                                                           sticky=tk.W)
        tk.Radiobutton(edit_window, text="已借出", variable=status_var, value="已借出", bg="#f0f5f9").grid(row=3,
                                                                                                           column=1)

        def update_book():
            title = title_entry.get().strip()
            author = author_entry.get().strip()
            category = category_entry.get().strip()
            status = status_var.get()

            if not all([title, author, category]):
                messagebox.showerror("错误", "所有字段都必须填写")
                return

            conn = get_db_conn("library")
            if not conn:
                return

            try:
                with conn.cursor() as cursor:
                    sql = """
                    UPDATE books
                    SET title = %s, author = %s, category = %s, status = %s
                    WHERE book_id = %s
                    """
                    cursor.execute(sql, (title, author, category, status, book_id))
                    conn.commit()
                    messagebox.showinfo("成功", "图书信息更新成功")
                    edit_window.destroy()
                    self.refresh_books()
            except pymysql.MySQLError as e:
                conn.rollback()
                messagebox.showerror("更新失败", f"错误：{str(e)}")
            finally:
                conn.close()

        tk.Button(edit_window, text="保存", command=update_book, bg="#006699", fg="white").grid(row=4, column=0,
                                                                                                columnspan=2, pady=20)

    def delete_book(self):
        """删除图书"""
        selected_item = self.book_tree.selection()
        if not selected_item:
            messagebox.showinfo("提示", "请先选择一本图书")
            return

        # 获取选中图书的信息
        values = self.book_tree.item(selected_item[0], "values")
        book_id = values[0]
        book_title = values[1]

        if messagebox.askyesno("确认", f"确定要删除图书 {book_title} 吗？"):
            conn = get_db_conn("library")
            if not conn:
                return

            try:
                with conn.cursor() as cursor:
                    # 检查该书是否被借出
                    check_sql = """
                    SELECT COUNT(*) as count FROM borrow_records 
                    WHERE book_id = %s AND return_date IS NULL
                    """
                    cursor.execute(check_sql, (book_id,))
                    result = cursor.fetchone()

                    if result["count"] > 0:
                        messagebox.showerror("错误", "该书已被借出，不能删除")
                        return

                    # 删除图书
                    delete_sql = "DELETE FROM books WHERE book_id = %s"
                    cursor.execute(delete_sql, (book_id,))
                    conn.commit()
                    messagebox.showinfo("成功", "图书删除成功")
                    self.refresh_books()
            except pymysql.MySQLError as e:
                conn.rollback()
                messagebox.showerror("删除失败", f"错误：{str(e)}")
            finally:
                conn.close()


# ----------------- 用户反馈管理窗口 -----------------
class FeedbackManagerWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("用户反馈管理")
        self.geometry("800x600")
        self.configure(bg="#f0f5f9")

        # 创建表格
        columns = ("feedback_id", "user_id", "user_name", "feedback_content", "feedback_date")
        self.feedback_tree = ttk.Treeview(self, columns=columns, show="headings")

        # 设置列标题
        for col in columns:
            self.feedback_tree.heading(col, text=col)
            if col == "feedback_content":
                self.feedback_tree.column(col, width=300, anchor=tk.W)
            else:
                self.feedback_tree.column(col, width=120, anchor=tk.CENTER)

        self.feedback_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 按钮框架
        btn_frame = tk.Frame(self, bg="#f0f5f9")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="刷新", command=self.refresh_feedbacks, bg="#993333", fg="white").pack(side=tk.LEFT,
                                                                                                         padx=5)
        tk.Button(btn_frame, text="查看详情", command=self.view_feedback_detail, bg="#993333", fg="white").pack(
            side=tk.LEFT, padx=5)

        # 初始加载用户反馈
        self.refresh_feedbacks()

    def refresh_feedbacks(self):
        """刷新用户反馈表格"""
        # 清空表格
        for item in self.feedback_tree.get_children():
            self.feedback_tree.delete(item)

        # 从数据库加载
        conn = get_db_conn("feedback_db")
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                # 联合查询获取用户名
                sql = """
                SELECT uf.feedback_id, uf.user_id, ut.user_name, uf.feedback_content, uf.feedback_date 
                FROM user_feedback uf 
                LEFT JOIN user_db.user_table ut ON uf.user_id = ut.user_id
                ORDER BY uf.feedback_date DESC
                """
                cursor.execute(sql)
                feedbacks = cursor.fetchall()

                for feedback in feedbacks:
                    self.feedback_tree.insert("", tk.END, values=(
                        feedback["feedback_id"],
                        feedback["user_id"],
                        feedback["user_name"],
                        feedback["feedback_content"],
                        feedback["feedback_date"].strftime("%Y-%m-%d %H:%M:%S") if feedback["feedback_date"] else ""
                    ))
        except pymysql.MySQLError as e:
            messagebox.showerror("查询失败", f"错误：{str(e)}")
        finally:
            conn.close()

    def view_feedback_detail(self):
        """查看反馈详情"""
        selected_item = self.feedback_tree.selection()
        if not selected_item:
            messagebox.showinfo("提示", "请先选择一条反馈")
            return

        # 获取选中反馈的信息
        values = self.feedback_tree.item(selected_item[0], "values")
        feedback_id = values[0]
        user_name = values[2]
        content = values[3]
        date = values[4]

        # 创建详情窗口
        detail_window = tk.Toplevel(self)
        detail_window.title("反馈详情")
        detail_window.geometry("600x400")
        detail_window.configure(bg="#f0f5f9")

        # 显示反馈信息
        tk.Label(detail_window, text=f"用户: {user_name}", bg="#f0f5f9", font=("微软雅黑", 12, "bold")).pack(pady=10,
                                                                                                             anchor=tk.W,
                                                                                                             padx=20)
        tk.Label(detail_window, text=f"时间: {date}", bg="#f0f5f9", font=("微软雅黑", 12, "bold")).pack(pady=5,
                                                                                                        anchor=tk.W,
                                                                                                        padx=20)

        tk.Label(detail_window, text="反馈内容:", bg="#f0f5f9", font=("微软雅黑", 12, "bold")).pack(pady=10,
                                                                                                    anchor=tk.W,
                                                                                                    padx=20)
        content_text = tk.Text(detail_window, width=70, height=15)
        content_text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        content_text.insert(tk.END, content)
        content_text.config(state=tk.DISABLED)

        # 关闭按钮
        tk.Button(detail_window, text="关闭", command=detail_window.destroy, bg="#006699", fg="white").pack(pady=20)


# ----------------- 管理员主界面 -----------------
def show_admin_dashboard(root, admin_username):
    admin_dash = tk.Toplevel(root)
    admin_dash.title(f"管理员面板 - {admin_username}")
    admin_dash.geometry("800x600")
    admin_dash.configure(bg="#f0f5f9")

    # 标题
    tk.Label(admin_dash, text="管理员功能面板", font=("微软雅黑", 24, "bold"), fg="#006699", bg="#f0f5f9").pack(pady=20)

    # 功能按钮
    tk.Button(admin_dash, text="读者信息管理", font=("微软雅黑", 14), bg="#006699", fg="white",
              command=lambda: ReaderManagerWindow(admin_dash)).pack(pady=10)
    tk.Button(admin_dash, text="图书信息管理", font=("微软雅黑", 14), bg="#006699", fg="white",
              command=lambda: BookManagerWindow(admin_dash)).pack(pady=10)
    tk.Button(admin_dash, text="用户反馈管理", font=("微软雅黑", 14), bg="#006699", fg="white",
              command=lambda: FeedbackManagerWindow(admin_dash)).pack(pady=10)

    # 返回登录界面按钮
    tk.Button(admin_dash, text="退出登录", command=admin_dash.destroy,
              bg="#006699", fg="white", width=15).pack(pady=10)
