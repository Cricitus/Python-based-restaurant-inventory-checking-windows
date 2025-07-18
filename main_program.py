import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import pathlib
from datetime import datetime, timedelta
import tkinter.font as tkFont

# 全局变量声明
root = None
notebook = None
conn = None
cur = None
ingredients_tree = None
containers_tree = None
meals_tree = None
meal_ingredients_tree = None
orders_tree = None
details_text = None


def connect_database():
    """连接到已存在的数据库"""
    global conn, cur
    db_path = pathlib.Path("food_company.sqlite3")
    if not db_path.exists():
        messagebox.showerror("Error", "The database file does not exist, please create the database first")
        root.destroy()
        return False
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Database error", f"Failed to connect to database: {str(e)}")
        root.destroy()
        return False


def create_inventory_tab():
    """创建库存管理标签页"""
    global ingredients_tree, containers_tree
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Inventory Management")

    # 原料库存框架
    ingredients_frame = ttk.LabelFrame(tab, text="Ingredients Inventory")
    ingredients_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # 原料库存表格
    columns = ("id", "name", "unit", "quantity", "unit_cost", "expiration_date", "total_value")
    ingredients_tree = ttk.Treeview(ingredients_frame, columns=columns, show="headings")
    for col in columns:
        ingredients_tree.heading(col, text=col.replace("_", " ").title())

    scrollbar = ttk.Scrollbar(ingredients_frame, orient="vertical", command=ingredients_tree.yview)
    ingredients_tree.configure(yscrollcommand=scrollbar.set)
    ingredients_tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 容器库存框架
    containers_frame = ttk.LabelFrame(tab, text="Containers Inventory")
    containers_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # 容器库存表格
    columns = ("id", "name", "quantity", "unit_cost", "total_value")
    containers_tree = ttk.Treeview(containers_frame, columns=columns, show="headings")
    for col in columns:
        containers_tree.heading(col, text=col.replace("_", " ").title())

    scrollbar2 = ttk.Scrollbar(containers_frame, orient="vertical", command=containers_tree.yview)
    containers_tree.configure(yscrollcommand=scrollbar2.set)
    containers_tree.pack(side="left", fill="both", expand=True)
    scrollbar2.pack(side="right", fill="y")

    # 按钮框架
    button_frame = ttk.Frame(tab)
    button_frame.pack(pady=10)

    ttk.Button(button_frame, text="Refresh Inventory", command=load_inventory_data).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Check Low Stock", command=check_low_stock).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Check Expiring Items", command=check_expiring_items).pack(side="left", padx=5)

    load_inventory_data()


def create_orders_tab():
    """创建订单管理标签页"""
    global orders_tree, details_text
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Order Tracking")

    # 订单管理框架
    orders_frame = ttk.LabelFrame(tab, text="Order Management")
    orders_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # 订单表格
    columns = ("id", "customer", "order_date", "delivery_date", "status", "total_amount")
    orders_tree = ttk.Treeview(orders_frame, columns=columns, show="headings")
    for col in columns:
        orders_tree.heading(col, text=col.replace("_", " ").title())

    scrollbar = ttk.Scrollbar(orders_frame, orient="vertical", command=orders_tree.yview)
    orders_tree.configure(yscrollcommand=scrollbar.set)
    orders_tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 订单详情框架
    details_frame = ttk.LabelFrame(tab, text="Order Details")
    details_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # 订单详情文本区域
    details_text = scrolledtext.ScrolledText(details_frame, height=8)
    details_text.pack(fill="both", expand=True, padx=5, pady=5)
    details_text.config(state=tk.DISABLED)

    # 按钮框架
    button_frame = ttk.Frame(tab)
    button_frame.pack(pady=10)

    ttk.Button(button_frame, text="Create New Order", command=create_new_order).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Update Order Status", command=update_order_status).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Refresh Orders", command=load_orders_data).pack(side="left", padx=5)

    # 绑定选择事件
    orders_tree.bind("<<TreeviewSelect>>", show_order_details)

    load_orders_data()


def create_customers_tab():
    """创建客户管理标签页"""
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Customer Management")

    # 客户表格
    customers_frame = ttk.LabelFrame(tab, text="Customer List")
    customers_frame.pack(fill="both", expand=True, padx=10, pady=5)

    columns = ("id", "name", "address", "phone", "email")
    customers_tree = ttk.Treeview(customers_frame, columns=columns, show="headings")
    for col in columns:
        customers_tree.heading(col, text=col.title())

    scrollbar = ttk.Scrollbar(customers_frame, orient="vertical", command=customers_tree.yview)
    customers_tree.configure(yscrollcommand=scrollbar.set)
    customers_tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 操作按钮
    btn_frame = ttk.Frame(tab)
    btn_frame.pack(pady=10)

    ttk.Button(btn_frame, text="Add Customer", command=lambda: open_customer_form(customers_tree)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Update", command=lambda: update_customer(customers_tree)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Delete", command=lambda: delete_customer(customers_tree)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Refresh", command=lambda: load_customers_data(customers_tree)).pack(side="left", padx=5)

    load_customers_data(customers_tree)

def load_customers_data(tree):
    """加载客户数据到表格"""
    for item in tree.get_children():
        tree.delete(item)

    cur.execute("SELECT id, name, address, phone, email FROM customers")
    for row in cur.fetchall():
        tree.insert("", "end", values=row)

def open_customer_form(tree):
    """打开添加客户窗口"""
    form = tk.Toplevel(root)
    form.title("Add New Customer")
    form.geometry("400x300")

    fields = ["Name", "Address", "Phone", "Email"]
    entries = {}

    for i, field in enumerate(fields):
        ttk.Label(form, text=field + ":").grid(row=i, column=0, padx=10, pady=5, sticky="e")
        entry = ttk.Entry(form, width=30)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[field.lower()] = entry

    def submit():
        values = {key: entries[key].get() for key in entries}
        if not values["name"]:
            messagebox.showerror("Input Error", "Name is required.")
            return

        try:
            cur.execute("INSERT INTO customers (name, address, phone, email) VALUES (?, ?, ?, ?)",
                        (values["name"], values["address"], values["phone"], values["email"]))
            conn.commit()
            messagebox.showinfo("Success", "Customer added successfully.")
            form.destroy()
            load_customers_data(tree)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    ttk.Button(form, text="Submit", command=submit).grid(row=len(fields), columnspan=2, pady=10)

def update_customer(tree):
    """更新选中的客户信息"""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a customer to update.")
        return

    item = tree.item(selected[0])
    customer_id, name, address, phone, email = item["values"]

    form = tk.Toplevel(root)
    form.title("Update Customer")
    form.geometry("400x300")

    fields = ["Name", "Address", "Phone", "Email"]
    entries = {}
    values = {"name": name, "address": address, "phone": phone, "email": email}

    for i, field in enumerate(fields):
        ttk.Label(form, text=field + ":").grid(row=i, column=0, padx=10, pady=5, sticky="e")
        entry = ttk.Entry(form, width=30)
        entry.insert(0, values[field.lower()])
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[field.lower()] = entry

    def submit():
        new_values = {key: entries[key].get() for key in entries}
        if not new_values["name"]:
            messagebox.showerror("Input Error", "Name is required.")
            return

        try:
            cur.execute("UPDATE customers SET name=?, address=?, phone=?, email=? WHERE id=?",
                        (new_values["name"], new_values["address"], new_values["phone"], new_values["email"], customer_id))
            conn.commit()
            messagebox.showinfo("Success", "Customer updated successfully.")
            form.destroy()
            load_customers_data(tree)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    ttk.Button(form, text="Submit", command=submit).grid(row=len(fields), columnspan=2, pady=10)

def delete_customer(tree):
    """删除选中的客户"""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a customer to delete.")
        return

    item = tree.item(selected[0])
    customer_id = item["values"][0]

    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete customer ID {customer_id}?"):
        try:
            cur.execute("DELETE FROM customers WHERE id=?", (customer_id,))
            conn.commit()
            messagebox.showinfo("Success", "Customer deleted successfully.")
            load_customers_data(tree)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

def create_meals_tab():
    """创建餐点管理标签页（完整修正版）"""
    global meals_tree, meal_ingredients_tree, cost_tree, container_listbox

    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Meal Management")

    # 主框架
    main_frame = ttk.Frame(tab)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # 左侧框架
    left_frame = ttk.Frame(main_frame)
    left_frame.pack(side="left", fill="both", expand=True)

    # 模式选择框架 (单选按钮)
    mode_frame = ttk.LabelFrame(left_frame, text="View Mode")
    mode_frame.pack(fill="x", padx=5, pady=5)

    mode_var = tk.StringVar(value="management")

    def change_view():
        if mode_var.get() == "management":
            cost_analysis_frame.pack_forget()
            details_frame.pack(fill="both", expand=True, padx=5, pady=5)
        else:
            details_frame.pack_forget()
            cost_analysis_frame.pack(fill="both", expand=True, padx=5, pady=5)
            calculate_meal_costs()

    ttk.Radiobutton(mode_frame, text="Meal Management", variable=mode_var,
                    value="management", command=change_view).pack(side="left", padx=5)
    ttk.Radiobutton(mode_frame, text="Cost Analysis", variable=mode_var,
                    value="cost", command=change_view).pack(side="left", padx=5)

    # 餐点管理框架
    meal_management_frame = ttk.LabelFrame(left_frame, text="Meal Management")
    meal_management_frame.pack(fill="both", expand=True, padx=5, pady=5)

    # 餐点表格
    columns = ("id", "name", "price", "description")
    meals_tree = ttk.Treeview(meal_management_frame, columns=columns, show="headings")
    for col in columns:
        meals_tree.heading(col, text=col.replace("_", " ").title())

    scrollbar = ttk.Scrollbar(meal_management_frame, orient="vertical", command=meals_tree.yview)
    meals_tree.configure(yscrollcommand=scrollbar.set)
    meals_tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 餐点详情框架
    details_frame = ttk.LabelFrame(left_frame, text="Meal Details")
    details_frame.pack(fill="both", expand=True, padx=5, pady=5)

    details_frame.grid_columnconfigure(1, weight=1)
    details_frame.grid_rowconfigure(2, weight=1)

    # 餐点详情表单
    ttk.Label(details_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    name_entry = ttk.Entry(details_frame)
    name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    ttk.Label(details_frame, text="Price:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    price_entry = ttk.Entry(details_frame)
    price_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    ttk.Label(details_frame, text="Description:").grid(row=2, column=0, padx=5, pady=5, sticky="ne")
    desc_text = tk.Text(details_frame, height=5)
    desc_text.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")

    # 餐点原料框架
    ingredients_frame = ttk.LabelFrame(details_frame, text="Ingredients")
    ingredients_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

    ingredients_frame.grid_columnconfigure(0, weight=1)
    ingredients_frame.grid_rowconfigure(0, weight=1)

    # 餐点原料表格
    columns = ("ingredient", "quantity", "unit")
    meal_ingredients_tree = ttk.Treeview(ingredients_frame, columns=columns, show="headings", height=5)
    for col in columns:
        meal_ingredients_tree.heading(col, text=col.title())

    scrollbar2 = ttk.Scrollbar(ingredients_frame, orient="vertical", command=meal_ingredients_tree.yview)
    meal_ingredients_tree.configure(yscrollcommand=scrollbar2.set)
    meal_ingredients_tree.pack(side="left", fill="both", expand=True)
    scrollbar2.pack(side="right", fill="y")

    # 添加原料控件 - 使用pack
    add_frame = ttk.Frame(ingredients_frame)
    add_frame.pack(fill="x", pady=5)

    ttk.Label(add_frame, text="Ingredient:").pack(side="left", padx=5)
    ingredient_var = tk.StringVar()
    ingredient_cbo = ttk.Combobox(add_frame, textvariable=ingredient_var, width=20)
    ingredient_cbo.pack(side="left", padx=5)

    # 加载原料数据
    cur.execute("SELECT id, name, unit FROM ingredients")
    ingredients = [f"{row[0]} - {row[1]} ({row[2]})" for row in cur.fetchall()]
    ingredient_cbo['values'] = ingredients
    if ingredients:
        ingredient_cbo.current(0)

    ttk.Label(add_frame, text="Qty:").pack(side="left", padx=5)
    qty_spin = ttk.Spinbox(add_frame, from_=0.1, to=100, increment=0.1, width=5)
    qty_spin.pack(side="left", padx=5)
    qty_spin.set(1)

    def add_ingredient():
        ingredient_str = ingredient_var.get()
        if not ingredient_str:
            return

        ingredient_id = int(ingredient_str.split(" - ")[0])
        ingredient_name = ingredient_str.split(" - ")[1].split(" (")[0]
        unit = ingredient_str.split("(")[1].split(")")[0]
        quantity = float(qty_spin.get())

        meal_ingredients_tree.insert("", "end", values=(ingredient_name, quantity, unit))

    add_btn = ttk.Button(add_frame, text="Add", command=add_ingredient)
    add_btn.pack(side="left", padx=10)

    def remove_ingredient():
        selected = meal_ingredients_tree.selection()
        if selected:
            meal_ingredients_tree.delete(selected)

    remove_btn = ttk.Button(add_frame, text="Remove", command=remove_ingredient)
    remove_btn.pack(side="left", padx=5)

    # 表单操作按钮框架
    form_button_frame = ttk.Frame(details_frame)
    form_button_frame.grid(row=4, column=0, columnspan=2, pady=10)

    def clear_form():
        name_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)
        desc_text.delete(1.0, tk.END)
        for item in meal_ingredients_tree.get_children():
            meal_ingredients_tree.delete(item)

    def load_meal_data():
        """加载餐点数据"""
        for item in meals_tree.get_children():
            meals_tree.delete(item)

        cur.execute("SELECT id, name, price, description FROM meals")
        for meal in cur.fetchall():
            meals_tree.insert("", "end", values=(
                meal[0], meal[1], f"{meal[2]:.2f}", meal[3]
            ))

    def add_meal():
        """添加餐点"""
        name = name_entry.get()
        price = price_entry.get()
        description = desc_text.get(1.0, tk.END).strip()

        if not name:
            messagebox.showerror("Error", "Please enter a meal name")
            return

        try:
            price = float(price)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid price")
            return

        # 检查餐点是否已存在
        cur.execute("SELECT id FROM meals WHERE name=?", (name,))
        if cur.fetchone():
            messagebox.showerror("Error", "Meal with this name already exists")
            return

        # 插入新餐点
        cur.execute("INSERT INTO meals (name, price, description) VALUES (?, ?, ?)",
                    (name, price, description))
        meal_id = cur.lastrowid

        # 保存原料
        for item in meal_ingredients_tree.get_children():
            values = meal_ingredients_tree.item(item)['values']
            ingredient_name = values[0]
            quantity = values[1]

            # 获取原料ID
            cur.execute("SELECT id FROM ingredients WHERE name=?", (ingredient_name,))
            ingredient_id = cur.fetchone()
            if not ingredient_id:
                messagebox.showerror("Error", f"Ingredient not found: {ingredient_name}")
                conn.rollback()
                return
            ingredient_id = ingredient_id[0]

            cur.execute("INSERT INTO meal_ingredients (meal_id, ingredient_id, quantity) VALUES (?, ?, ?)",
                        (meal_id, ingredient_id, quantity))

        conn.commit()
        messagebox.showinfo("Success", "Meal added successfully!")
        load_meal_data()
        clear_form()
        calculate_meal_costs()
        load_selection_data()

    def delete_meal():
        """删除餐点"""
        name = name_entry.get()

        if not name:
            messagebox.showerror("Error", "Please enter a meal name to delete")
            return

        # 检查餐点是否存在
        cur.execute("SELECT id FROM meals WHERE name=?", (name,))
        meal = cur.fetchone()

        if not meal:
            messagebox.showerror("Error", f"Meal not found: {name}")
            return

        if messagebox.askyesno("Confirm", f"Are you sure you want to delete {name}?"):
            meal_id = meal[0]
            # 先删除关联的原料和容器
            cur.execute("DELETE FROM meal_ingredients WHERE meal_id=?", (meal_id,))
            cur.execute("DELETE FROM meal_containers WHERE meal_id=?", (meal_id,))
            # 然后删除餐点
            cur.execute("DELETE FROM meals WHERE id=?", (meal_id,))
            conn.commit()
            messagebox.showinfo("Success", "Meal deleted successfully!")
            load_meal_data()
            clear_form()
            calculate_meal_costs()

    # 表单操作按钮
    add_btn = ttk.Button(form_button_frame, text="Add Meal", command=add_meal)
    add_btn.grid(row=0, column=0, padx=5)

    delete_btn = ttk.Button(form_button_frame, text="Delete Meal", command=delete_meal)
    delete_btn.grid(row=0, column=1, padx=5)

    clear_btn = ttk.Button(form_button_frame, text="Clear Form", command=clear_form)
    clear_btn.grid(row=0, column=2, padx=5)

    # 成本分析框架
    cost_analysis_frame = ttk.LabelFrame(left_frame, text="Meal Cost Analysis")

    # 餐点成本框架
    meals_cost_frame = ttk.LabelFrame(cost_analysis_frame)
    meals_cost_frame.pack(fill="both", expand=True, pady=5)

    # 成本计算表格
    cost_columns = ("id", "name", "ingredient_cost", "selected_container", "container_cost", "unit_total_cost")
    cost_tree = ttk.Treeview(meals_cost_frame, columns=cost_columns, show="headings", height=10)
    for col in cost_columns:
        cost_tree.heading(col, text=col.replace("_", " ").title())

    cost_tree.column("id", width=50)
    cost_tree.column("name", width=100)
    cost_tree.column("ingredient_cost", width=50)
    cost_tree.column("selected_container", width=100)
    cost_tree.column("container_cost", width=50)
    cost_tree.column("unit_total_cost", width=50)

    cost_scrollbar = ttk.Scrollbar(meals_cost_frame, orient="vertical", command=cost_tree.yview)
    cost_tree.configure(yscrollcommand=cost_scrollbar.set)
    cost_tree.pack(side="left", fill="both", expand=True)
    cost_scrollbar.pack(side="right", fill="y")

    # 选择框架
    selection_frame = ttk.Frame(cost_analysis_frame)
    selection_frame.pack(fill="x", pady=5)

    # 容器选择
    ttk.Label(selection_frame, text="Containers:").pack(side="left", padx=5)
    container_listbox = tk.Listbox(selection_frame, height=4, exportselection=False)
    container_listbox.pack(side="left", fill="x", expand=True, padx=5)

    meal_container_selections = {}

    def load_selection_data():
        container_listbox.delete(0, tk.END)
        cur.execute("SELECT id, name FROM containers ORDER BY name")
        for container in cur.fetchall():
            container_listbox.insert(tk.END, f"{container[0]} - {container[1]}")

    def calculate_meal_costs():
        """计算餐点成本"""
        # 清空现有数据
        for item in cost_tree.get_children():
            cost_tree.delete(item)

        # 获取所有餐点
        cur.execute("SELECT id, name FROM meals")
        meals = cur.fetchall()

        # 获取当前选择的容器
        container_selection = container_listbox.curselection()
        selected_container_id = None
        selected_container_name = "None"
        selected_container_cost = 0.0

        if container_selection:
            container_str = container_listbox.get(container_selection[0])
            selected_container_id = int(container_str.split(" - ")[0])
            cur.execute("SELECT name, unit_cost FROM containers WHERE id=?", (selected_container_id,))
            container_data = cur.fetchone()
            selected_container_name = container_data[0]
            selected_container_cost = container_data[1]

        for meal in meals:
            meal_id, meal_name = meal

            # 计算原料成本
            ingredient_cost = 0.0
            cur.execute('''
                SELECT i.unit_cost, mi.quantity 
                FROM meal_ingredients mi
                JOIN ingredients i ON mi.ingredient_id = i.id
                WHERE mi.meal_id = ?
            ''', (meal_id,))

            for row in cur.fetchall():
                ingredient_cost += row[0] * row[1]

            # 获取该餐点的容器选择
            container_cost = 0.0
            container_name = "None"
            if meal_id in meal_container_selections:
                container_id = meal_container_selections[meal_id]
                cur.execute("SELECT name, unit_cost FROM containers WHERE id=?", (container_id,))
                container_cost = cur.fetchone()
                container_name = container_data[0]
                container_cost = container_data[1]
            elif selected_container_id:  # 使用全局选择的容器
                container_cost = selected_container_cost
                container_name = selected_container_name

            total_cost = ingredient_cost + container_cost

            cost_tree.insert("", "end", values=(
                meal_id,
                meal_name,
                f"${ingredient_cost:.2f}",
                container_name,
                f"${container_cost:.2f}" if container_cost > 0 else "None",
                f"${total_cost:.2f}"
            ))
    cost_button_frame = ttk.Frame(cost_analysis_frame)
    cost_button_frame.pack(pady=5)
    # 计算按钮
    calc_button = ttk.Button(cost_analysis_frame, text="Calculate Costs", command=calculate_meal_costs)
    calc_button.pack(pady=5)
    def clear_container_selection():
        """清除容器选择"""
        container_listbox.selection_clear(0, tk.END)  # 取消选中容器
        calculate_meal_costs()  # 重新计算成本（此时容器为 None）

    clear_btn = ttk.Button(cost_button_frame, text="Clear Container", command=clear_container_selection)
    clear_btn.pack(side="left", padx=5)
    # 初始加载数据
    load_meal_data()
    load_selection_data()
    calculate_meal_costs()
    change_view()  # 默认显示管理视图


def create_budget_tab():
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from tkinter import ttk, messagebox
    from collections import defaultdict

    global tab
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Budget Management")

    chart_frame = ttk.Frame(tab)
    chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # month selection part
    ttk.Label(tab, text="Select Month:", font=("Arial", 10)).pack(pady=5)

    cur.execute("""
        SELECT DISTINCT strftime('%Y-%m', order_date) AS month
        FROM orders
        WHERE order_date IS NOT NULL
        ORDER BY month DESC
    """)
    months = [row[0] for row in cur.fetchall()]

    selected_month = tk.StringVar()
    month_combo = ttk.Combobox(tab, textvariable=selected_month, values=months, state="readonly")
    if months:
        selected_month.set(months[0])
    month_combo.pack(pady=5)

    def generate_chart():
        month_str = selected_month.get()
        if not month_str:
            messagebox.showerror("Error", "Please select a month.")
            return

        # fixed_cost detail
        labor_cost = 10000
        rent_cost = 3500
        utilities_cost = 2000
        overhead_cost = 1000
        fixed_cost = labor_cost + rent_cost + utilities_cost + overhead_cost

        # set sales & cogs
        sales = 0.0
        cogs = 0.0

        # check the order month
        cur.execute('''
            SELECT orders.id, orders.order_date 
            FROM orders
            WHERE substr(order_date, 1, 7) = ?
        ''', (month_str,))
        order_ids = [row[0] for row in cur.fetchall()]

        if not order_ids:
            messagebox.showinfo("No Data", f"No orders found in {month_str}")
            return

        order_id_placeholders = ",".join("?" for _ in order_ids)

        # calculate sales
        cur.execute(f'''
            SELECT meals.price, order_details.quantity
            FROM order_details
            JOIN meals ON meals.id = order_details.meal_id
            WHERE order_details.order_id IN ({order_id_placeholders})
        ''', order_ids)
        for price, qty in cur.fetchall():
            sales += price * qty

        # calculate cogs
        cur.execute(f'''
            SELECT mi.ingredient_id, SUM(mi.quantity * od.quantity) AS total_qty
            FROM order_details od
            JOIN meals m ON od.meal_id = m.id
            JOIN meal_ingredients mi ON m.id = mi.meal_id
            WHERE od.order_id IN ({order_id_placeholders})
            GROUP BY mi.ingredient_id
        ''', order_ids)

        ingredient_costs = defaultdict(float)
        for ing_id, total_qty in cur.fetchall():
            cur.execute("SELECT unit_cost FROM ingredients WHERE id = ?", (ing_id,))
            unit_cost = cur.fetchone()
            if unit_cost:
                ingredient_costs[ing_id] = total_qty * unit_cost[0]
                cogs += total_qty * unit_cost[0]

        net_income = sales - fixed_cost - cogs

        # before generating a new graph, clear the old graph to avoid error
        for widget in chart_frame.winfo_children():
            widget.destroy()

        # draw the graph
        fig, ax = plt.subplots(figsize=(5, 3))
        labels = ['Sales', 'Fixed Costs', 'COGS', 'Net Income']
        values = [sales, fixed_cost, cogs, net_income]
        colors = ['#4caf50', '#ff9800', '#f44336', '#2196f3']

        ax.bar(labels, values, color=colors)
        ax.set_ylabel("Amount ($)")
        ax.set_title(f"Financial Summary for {month_str}")
        for i, v in enumerate(values):
            ax.text(i, v + max(values) * 0.02, f"${v:,.2f}", ha='center', va='bottom', fontsize=8)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # fixed_cost detail
        fixed_cost_breakdown = (
            f"Fixed Costs Breakdown:\n"
            f"- Labor Costs: $10,000\n"
            f"- Rent: $3,500\n"
            f"- Utilities: $2,000\n"
            f"- Overhead Costs: $1,000\n"
            f"Total Fixed Costs: ${fixed_cost:,.2f}"
        )
        ttk.Label(chart_frame, text=fixed_cost_breakdown, font=("Arial", 9), justify="left").pack(pady=5)

    ttk.Button(tab, text="Generate Monthly Budget Chart", command=generate_chart).pack(pady=10)

def load_inventory_data():
    """加载库存数据（优化刷新逻辑）"""
    if not ingredients_tree or not containers_tree:
        return

    # 清空表格
    for item in ingredients_tree.get_children():
        ingredients_tree.delete(item)
    for item in containers_tree.get_children():
        containers_tree.delete(item)

    # 加载原料数据（包含库存价值计算）
    cur.execute("SELECT id, name, unit, quantity, unit_cost, expiration_date FROM ingredients")
    for ing in cur.fetchall():
        total_value = ing[3] * ing[4]
        ingredients_tree.insert("", "end", values=(
            ing[0], ing[1], ing[2], f"{ing[3]:.2f}", f"{ing[4]:.2f}", ing[5], f"{total_value:.2f}"
        ))

    # 加载容器数据（包含库存价值计算）
    cur.execute("SELECT id, name, quantity, unit_cost FROM containers")
    for con in cur.fetchall():
        total_value = con[2] * con[3]
        containers_tree.insert("", "end", values=(
            con[0], con[1], con[2], f"{con[3]:.2f}", f"{total_value:.2f}"
        ))


def update_inventory_from_order(order_id):
    """根据订单ID更新原材料和包装库存"""
    try:
        # 获取订单中的餐点及数量
        cur.execute('''
            SELECT od.meal_id, od.quantity
            FROM order_details od
            WHERE od.order_id = ?
        ''', (order_id,))
        order_items = cur.fetchall()

        if not order_items:
            return

        # 计算需要消耗的原材料
        ingredient_consumption = {}
        for meal_id, quantity in order_items:
            # 获取该餐点的原材料配方
            cur.execute('''
                SELECT mi.ingredient_id, mi.quantity
                FROM meal_ingredients mi
                WHERE mi.meal_id = ?
            ''', (meal_id,))
            for ing_id, required_qty in cur.fetchall():
                # 计算总消耗量 = 餐点数量 × 单份所需原材料数量
                total_consumption = quantity * required_qty
                if ing_id in ingredient_consumption:
                    ingredient_consumption[ing_id] += total_consumption
                else:
                    ingredient_consumption[ing_id] = total_consumption

        # 更新原材料库存
        for ing_id, consumption in ingredient_consumption.items():
            cur.execute('''
                UPDATE ingredients 
                SET quantity = quantity - ? 
                WHERE id = ? AND quantity >= ?
            ''', (consumption, ing_id, consumption))
            if cur.rowcount == 0:
                raise ValueError(f"原材料库存不足，ID: {ing_id}, 需消耗: {consumption}")

        # 计算需要消耗的包装
        container_consumption = {}
        for meal_id, quantity in order_items:
            # 获取该餐点使用的包装
            cur.execute('''
                SELECT mc.container_id, mc.quantity
                FROM meal_containers mc
                WHERE mc.meal_id = ?
            ''', (meal_id,))
            for con_id, required_qty in cur.fetchall():
                # 计算总消耗量 = 餐点数量 × 单份所需包装数量
                total_consumption = quantity * required_qty
                if con_id in container_consumption:
                    container_consumption[con_id] += total_consumption
                else:
                    container_consumption[con_id] = total_consumption

        # 更新包装库存
        for con_id, consumption in container_consumption.items():
            cur.execute('''
                UPDATE containers 
                SET quantity = quantity - ? 
                WHERE id = ? AND quantity >= ?
            ''', (consumption, con_id, consumption))
            if cur.rowcount == 0:
                raise ValueError(f"包装库存不足，ID: {con_id}, 需消耗: {consumption}")

    except Exception as e:
        conn.rollback()
        raise e


def load_orders_data():
    """加载订单数据"""
    if not orders_tree:
        return

    # 清空表格
    for item in orders_tree.get_children():
        orders_tree.delete(item)

    # 加载订单数据
    cur.execute('''
        SELECT orders.id, customers.name, orders.order_date, 
               orders.delivery_date, orders.status, orders.total_amount
        FROM orders
        JOIN customers ON orders.customer_id = customers.id
        ORDER BY orders.delivery_date DESC
    ''')
    for order in cur.fetchall():
        orders_tree.insert("", "end", values=(
            order[0], order[1], order[2], order[3], order[4], f"{order[5]:.2f}"
        ))


def show_order_details(event):
    """显示订单详情"""
    if not orders_tree or not details_text:
        return

    selected = orders_tree.selection()
    if not selected:
        return

    item = orders_tree.item(selected[0])
    order_id = item['values'][0]

    # 查询订单详情
    cur.execute('''
        SELECT meals.name, order_details.quantity, meals.price
        FROM order_details
        JOIN meals ON order_details.meal_id = meals.id
        WHERE order_details.order_id = ?
    ''', (order_id,))
    details = cur.fetchall()

    # 查询订单信息
    cur.execute('''
        SELECT orders.order_date, orders.delivery_date, orders.status, 
               orders.total_amount, customers.name, customers.address
        FROM orders
        JOIN customers ON orders.customer_id = customers.id
        WHERE orders.id = ?
    ''', (order_id,))
    order_info = cur.fetchone()

    # 显示详情
    details_text.config(state=tk.NORMAL)
    details_text.delete(1.0, tk.END)

    if order_info:
        details_text.insert(tk.END, f"Order ID: {order_id}\n")
        details_text.insert(tk.END, f"Customer: {order_info[4]}\n")
        details_text.insert(tk.END, f"Address: {order_info[5]}\n")
        details_text.insert(tk.END, f"Order Date: {order_info[0]}\n")
        details_text.insert(tk.END, f"Delivery Date: {order_info[1]}\n")
        details_text.insert(tk.END, f"Status: {order_info[2]}\n")
        details_text.insert(tk.END, f"Total Amount: ${order_info[3]:.2f}\n\n")
        details_text.insert(tk.END, "Order Items:\n--------------------------------------------\n")

        for item in details:
            line_total = item[1] * item[2]
            details_text.insert(tk.END, f"{item[0]} x {item[1]} @ ${item[2]:.2f} = ${line_total:.2f}\n")

    details_text.config(state=tk.DISABLED)


def create_new_order():
    """创建新订单"""
    if not conn:
        messagebox.showerror("Error", "Database not connected")
        return

    # 创建新订单窗口
    order_window = tk.Toplevel(root)
    order_window.title("Create New Order")
    order_window.geometry("1400x350")

    # 客户选择
    ttk.Label(order_window, text="Customer:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    customer_var = tk.StringVar()
    customer_cbo = ttk.Combobox(order_window, textvariable=customer_var, width=30)
    customer_cbo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    # 加载客户数据
    cur.execute("SELECT id, name FROM customers")
    customers = [f"{row[0]} - {row[1]}" for row in cur.fetchall()]
    customer_cbo['values'] = customers
    if customers:
        customer_cbo.current(0)

    # 交付日期
    ttk.Label(order_window, text="Delivery Date:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    delivery_entry = ttk.Entry(order_window, width=30)
    delivery_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
    delivery_entry.insert(0, (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"))

    # 订单项目框架
    items_frame = ttk.LabelFrame(order_window, text="Order Items")
    items_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    # 项目表格
    columns = ("meal", "quantity", "price", "total")
    items_tree = ttk.Treeview(items_frame, columns=columns, show="headings", height=5)
    items_tree.heading("meal", text="Meal")
    items_tree.heading("quantity", text="Qty")
    items_tree.heading("price", text="Price ($)")
    items_tree.heading("total", text="Total ($)")

    scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=items_tree.yview)
    items_tree.configure(yscrollcommand=scrollbar.set)
    items_tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 添加项目控件
    add_frame = ttk.Frame(items_frame)
    add_frame.pack(fill="x", pady=5)

    ttk.Label(add_frame, text="Meal:").pack(side="left", padx=5)
    meal_var = tk.StringVar()
    meal_cbo = ttk.Combobox(add_frame, textvariable=meal_var, width=25)
    meal_cbo.pack(side="left", padx=5)

    # 加载餐点数据
    cur.execute("SELECT id, name, price FROM meals")
    meals = [f"{row[0]} - {row[1]} (${row[2]:.2f})" for row in cur.fetchall()]
    meal_cbo['values'] = meals
    if meals:
        meal_cbo.current(0)

    ttk.Label(add_frame, text="Qty:").pack(side="left", padx=5)
    qty_spin = ttk.Spinbox(add_frame, from_=1, to=100, width=5)
    qty_spin.pack(side="left", padx=5)
    qty_spin.set(1)

    def add_item():
        meal_str = meal_var.get()
        if not meal_str:
            return

        meal_id = int(meal_str.split(" - ")[0])
        meal_name = meal_str.split(" - ")[1].split(" ($")[0]
        meal_price = float(meal_str.split("$")[1].split(")")[0])
        quantity = int(qty_spin.get())
        total = meal_price * quantity

        items_tree.insert("", "end", values=(meal_name, quantity, f"{meal_price:.2f}", f"{total:.2f}"))
        update_total()

    add_btn = ttk.Button(add_frame, text="Add Item", command=add_item)
    add_btn.pack(side="left", padx=10)

    def remove_item():
        selected = items_tree.selection()
        if selected:
            items_tree.delete(selected)
            update_total()

    remove_btn = ttk.Button(add_frame, text="Remove Item", command=remove_item)
    remove_btn.pack(side="left", padx=5)

    # 订单总计
    total_frame = ttk.Frame(order_window)
    total_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

    ttk.Label(total_frame, text="Order Total:", font=("Arial", 10, "bold")).pack(side="left", padx=5)
    total_var = tk.StringVar(value="$0.00")
    ttk.Label(total_frame, textvariable=total_var, font=("Arial", 10, "bold")).pack(side="left", padx=5)

    def update_total():
        total = 0.0
        for item in items_tree.get_children():
            values = items_tree.item(item)['values']
            total += float(values[3])
        total_var.set(f"${total:.2f}")

    # 保存订单
    def save_order():
        customer_id = int(customer_var.get().split(" - ")[0]) if customer_var.get() else 0
        delivery_date = delivery_entry.get()
        order_date = datetime.now().strftime("%Y-%m-%d")

        if not customer_id:
            messagebox.showerror("Error", "Please select a customer")
            return

        if not delivery_date:
            messagebox.showerror("Error", "Please enter a delivery date")
            return

        if not items_tree.get_children():
            messagebox.showerror("Error", "Please add at least one item to the order")
            return

        # 计算订单总额
        total_amount = float(total_var.get().replace("$", ""))

        # 插入订单
        cur.execute('''
            INSERT INTO orders (customer_id, order_date, delivery_date, status, total_amount)
            VALUES (?, ?, ?, ?, ?)
        ''', (customer_id, order_date, delivery_date, "Received", total_amount))
        order_id = cur.lastrowid

        # 插入订单详情
        for item in items_tree.get_children():
            values = items_tree.item(item)['values']
            meal_name = values[0]

            # 获取餐点ID
            cur.execute("SELECT id FROM meals WHERE name = ?", (meal_name,))
            meal_id = cur.fetchone()
            if not meal_id:
                messagebox.showerror("Error", f"Meal not found: {meal_name}")
                conn.rollback()
                return
            meal_id = meal_id[0]

            quantity = values[1]
            cur.execute('''
                INSERT INTO order_details (order_id, meal_id, quantity)
                VALUES (?, ?, ?)
            ''', (order_id, meal_id, quantity))

        conn.commit()
        messagebox.showinfo("Success", f"Order #{order_id} created successfully!")
        order_window.destroy()
        load_orders_data()  # 刷新订单列表

    save_btn = ttk.Button(order_window, text="Save Order", command=save_order)
    save_btn.grid(row=4, column=0, columnspan=2, pady=10)


def update_order_status():
    """更新订单状态并在完成时更新库存"""
    if not orders_tree:
        return
    selected = orders_tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an order first")
        return
    item = orders_tree.item(selected[0])
    order_id = item['values'][0]
    current_status = item['values'][4]

    # 状态选择窗口
    status_window = tk.Toplevel(root)
    status_window.title("Update Order Status")
    status_window.geometry("300x150")
    ttk.Label(status_window, text=f"Update Status for Order #{order_id}").pack(pady=10)

    status_var = tk.StringVar(value=current_status)
    status_cbo = ttk.Combobox(status_window, textvariable=status_var, state="readonly")
    status_cbo['values'] = ("Received", "In Progress", "Completed")
    status_cbo.pack(pady=5)

    def save_status():
        new_status = status_var.get()
        try:
            conn.execute("BEGIN TRANSACTION")  # 开启事务
            cur.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))

            # 当状态更新为Completed时更新库存
            if new_status == "Completed":
                update_inventory_from_order(order_id)

            conn.commit()  # 提交事务
            messagebox.showinfo("Success", f"Order #{order_id} status updated to {new_status}")
            status_window.destroy()
            load_orders_data()
            load_inventory_data()  # 刷新库存数据
        except Exception as e:
            conn.rollback()  # 事务回滚
            messagebox.showerror("Database Error", f"Update failed: {str(e)}")

    save_btn = ttk.Button(status_window, text="Update Status", command=save_status)
    save_btn.pack(pady=10)


def check_low_stock():
    """检查低库存"""
    # 检查低库存原料
    cur.execute("SELECT name, quantity, unit FROM ingredients WHERE quantity < 5")
    low_ingredients = cur.fetchall()

    # 检查低库存容器
    cur.execute("SELECT name, quantity FROM containers WHERE quantity < 10")
    low_containers = cur.fetchall()

    if not low_ingredients and not low_containers:
        messagebox.showinfo("Stock Check", "All inventory items are at sufficient levels")
        return
    # 显示警告
    warning_text = "Low Stock Warning:\n\n"

    if low_ingredients:
        warning_text += "Ingredients:\n"
        for ing in low_ingredients:
            warning_text += f"- {ing[0]}: {ing[1]} {ing[2]}\n"
        warning_text += "\n"

    if low_containers:
        warning_text += "Containers:\n"
        for con in low_containers:
            warning_text += f"- {con[0]}: {con[1]} units\n"

    messagebox.showwarning("Low Stock Alert", warning_text)


def check_expiring_items():
    """检查即将过期的原料"""
    cur.execute("SELECT name, expiration_date FROM ingredients WHERE expiration_date <= date('now', '+30 days')")
    expiring_items = cur.fetchall()

    if not expiring_items:
        messagebox.showinfo("Expiry Check", "No ingredients are expiring in the next 30 days")
        return

    # 显示警告
    warning_text = "Expiring Ingredients:\n\n"
    for item in expiring_items:
        warning_text += f"- {item[0]} expires on {item[1]}\n"

    messagebox.showwarning("Expiration Alert", warning_text)


def main_function():
    """主函数"""
    global root, notebook
    root = tk.Tk()
    root.title("Family Food Service Management System")
    root.geometry("1200x700")

    # 连接数据库
    if not connect_database():
        return

    # 创建标签页
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # 创建各功能标签页
    create_inventory_tab()
    create_orders_tab()
    create_customers_tab()
    create_meals_tab()
    create_budget_tab()

    # 状态栏
    status_bar = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    root.mainloop()

    # 程序退出时关闭数据库连接
    if conn:
        conn.close()


if __name__ == "__main__":
    main_function()
