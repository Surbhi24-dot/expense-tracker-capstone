from flask import Flask, request, redirect
import os
import pymysql
from datetime import date

app = Flask(__name__)


def get_db_connection():
    connection = pymysql.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection


def init_db():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)

    connection.commit()
    cursor.close()
    connection.close()


@app.route("/", methods=["GET", "POST"])
def home():

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        description = request.form["description"]
        amount = float(request.form["amount"])
        category = request.form["category"]
        expense_date = request.form["date"]

        cursor.execute(
            "INSERT INTO expenses (description, amount, category, date) VALUES (%s, %s, %s, %s)",
            (description, amount, category, expense_date)
        )

        connection.commit()
        cursor.close()
        connection.close()

        return redirect("/")

    cursor.execute(
        "SELECT * FROM expenses ORDER BY id DESC"
    )
    expenses = cursor.fetchall()

    cursor.execute(
        "SELECT SUM(amount) AS total FROM expenses"
    )
    total = cursor.fetchone()["total"]

    if total is None:
        total = 0

    cursor.execute(
        "SELECT category, SUM(amount) AS total FROM expenses GROUP BY category"
    )
    category_totals = cursor.fetchall()

    cursor.close()
    connection.close()

    html = f"""
    <html>

    <head>
        <title>Expense Tracker</title>

        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>

            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: #f4f6fb;
                color: #1f2937;
            }}

            .header {{
                background: linear-gradient(135deg, #4f46e5, #7c3aed);
                color: white;
                padding: 35px 20px;
                text-align: center;
            }}

            .header h1 {{
                margin: 0;
                font-size: 34px;
            }}

            .header p {{
                margin: 8px 0 0;
                opacity: 0.9;
            }}

            .container {{
                max-width: 1100px;
                margin: 30px auto;
                padding: 0 20px;
            }}

            .total-card {{
                background: white;
                border-radius: 16px;
                padding: 25px;
                margin-bottom: 25px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                border-left: 6px solid #6366f1;
            }}

            .total-card h2 {{
                margin: 0;
                color: #6b7280;
                font-size: 16px;
            }}

            .total-amount {{
                margin-top: 8px;
                font-size: 34px;
                font-weight: bold;
                color: #4f46e5;
            }}

            .card {{
                background: white;
                border-radius: 16px;
                padding: 25px;
                margin-bottom: 25px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.06);
            }}

            .card h2 {{
                margin-top: 0;
                color: #111827;
            }}

            .form-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 18px;
            }}

            .form-group {{
                display: flex;
                flex-direction: column;
            }}

            .form-group label {{
                margin-bottom: 7px;
                font-weight: bold;
                color: #374151;
            }}

            input,
            select {{
                padding: 12px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                font-size: 15px;
                background: white;
            }}

            input:focus,
            select:focus {{
                outline: none;
                border-color: #6366f1;
                box-shadow: 0 0 0 3px rgba(99,102,241,0.15);
            }}

            .add-button {{
                margin-top: 20px;
                padding: 13px 24px;
                border: none;
                border-radius: 9px;
                background: #4f46e5;
                color: white;
                font-size: 15px;
                font-weight: bold;
                cursor: pointer;
            }}

            .add-button:hover {{
                background: #4338ca;
            }}

            .category-grid {{
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 12px;
            }}

            .category-card {{
                background: #f8f7ff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 16px;
                text-align: center;
            }}

            .category-name {{
                font-size: 14px;
                color: #6b7280;
                margin-bottom: 8px;
            }}

            .category-amount {{
                font-size: 20px;
                font-weight: bold;
                color: #4f46e5;
            }}

            .expense-table-wrapper {{
                overflow-x: auto;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                min-width: 650px;
            }}

            th {{
                background: #f3f4f6;
                color: #4b5563;
                text-align: left;
                padding: 14px;
                font-size: 14px;
            }}

            td {{
                padding: 14px;
                border-bottom: 1px solid #e5e7eb;
            }}

            tr:hover {{
                background: #fafafa;
            }}

            .category-badge {{
                display: inline-block;
                padding: 5px 10px;
                border-radius: 20px;
                background: #ede9fe;
                color: #6d28d9;
                font-size: 13px;
                font-weight: bold;
            }}

            .action-button {{
                padding: 7px 12px;
                border-radius: 7px;
                border: none;
                cursor: pointer;
                font-size: 13px;
                font-weight: bold;
            }}

            .edit-button {{
                background: #e0e7ff;
                color: #3730a3;
            }}

            .delete-button {{
                background: #fee2e2;
                color: #b91c1c;
            }}

            .empty-message {{
                text-align: center;
                color: #6b7280;
                padding: 25px;
            }}

            @media (max-width: 700px) {{

                .form-grid {{
                    grid-template-columns: 1fr;
                }}

                .category-grid {{
                    grid-template-columns: repeat(2, 1fr);
                }}

                .header h1 {{
                    font-size: 28px;
                }}

            }}

        </style>

    </head>

    <body>

        <div class="header">
            <h1>💰 Expense Tracker</h1>
            <p>Manage your personal expenses in one place</p>
        </div>

        <div class="container">

            <div class="total-card">
                <h2>Total Expenses</h2>
                <div class="total-amount">€{total:.2f}</div>
            </div>

            <div class="card">

                <h2>➕ Add New Expense</h2>

                <form method="POST">

                    <div class="form-grid">

                        <div class="form-group">
                            <label>Description</label>
                            <input
                                type="text"
                                name="description"
                                placeholder="e.g. Grocery shopping"
                                required>
                        </div>

                        <div class="form-group">
                            <label>Amount (€)</label>
                            <input
                                type="number"
                                name="amount"
                                step="0.01"
                                placeholder="0.00"
                                required>
                        </div>

                        <div class="form-group">
                            <label>Category</label>

                            <select name="category">
                                <option value="Food">Food</option>
                                <option value="Transport">Transport</option>
                                <option value="Shopping">Shopping</option>
                                <option value="Bills">Bills</option>
                                <option value="Other">Other</option>
                            </select>

                        </div>

                        <div class="form-group">
                            <label>Date</label>

                            <input
                                type="date"
                                name="date"
                                value="{date.today()}"
                                required>

                        </div>

                    </div>

                    <button class="add-button" type="submit">
                        Add Expense
                    </button>

                </form>

            </div>

            <div class="card">

                <h2>📊 Category Summary</h2>

                <div class="category-grid">
    """

    for row in category_totals:

        html += f"""
                    <div class="category-card">

                        <div class="category-name">
                            {row["category"]}
                        </div>

                        <div class="category-amount">
                            €{row["total"]:.2f}
                        </div>

                    </div>
        """

    html += """
                </div>

            </div>

            <div class="card">

                <h2>📋 All Expenses</h2>

                <div class="expense-table-wrapper">

                    <table>

                        <thead>
                            <tr>
                                <th>Description</th>
                                <th>Amount</th>
                                <th>Category</th>
                                <th>Date</th>
                                <th>Actions</th>
                            </tr>
                        </thead>

                        <tbody>
    """

    if not expenses:

        html += """
                            <tr>
                                <td colspan="5" class="empty-message">
                                    No expenses yet. Add your first expense above.
                                </td>
                            </tr>
        """

    for expense in expenses:

        expense_date = expense["date"] if expense["date"] else "No date"

        html += f"""
                            <tr>

                                <td>
                                    {expense["description"]}
                                </td>

                                <td>
                                    €{expense["amount"]:.2f}
                                </td>

                                <td>
                                    <span class="category-badge">
                                        {expense["category"]}
                                    </span>
                                </td>

                                <td>
                                    {expense_date}
                                </td>

                                <td>

                                    <form method="GET"
                                          action="/edit/{expense["id"]}"
                                          style="display:inline;">

                                        <button
                                            type="submit"
                                            class="action-button edit-button">
                                            Edit
                                        </button>

                                    </form>

                                    <form method="POST"
                                          action="/delete/{expense["id"]}"
                                          style="display:inline;">

                                        <button
                                            type="submit"
                                            class="action-button delete-button">
                                            Delete
                                        </button>

                                    </form>

                                </td>

                            </tr>
        """

    html += """
                        </tbody>

                    </table>

                </div>

            </div>

        </div>

    </body>

    </html>
    """

    return html


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id = %s",
        (expense_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/")

@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        description = request.form["description"]
        amount = float(request.form["amount"])
        category = request.form["category"]
        expense_date = request.form["date"]

        cursor.execute(
            """
            UPDATE expenses
            SET description = %s,
                amount = %s,
                category = %s,
                date = %s
            WHERE id = %s
            """,
            (
                description,
                amount,
                category,
                expense_date,
                expense_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/")

    cursor.execute(
        "SELECT * FROM expenses WHERE id = %s",
        (expense_id,)
    )

    expense = cursor.fetchone()

    cursor.close()
    connection.close()

    if expense is None:
        return "Expense not found", 404

    food_selected = "selected" if expense["category"] == "Food" else ""
    transport_selected = "selected" if expense["category"] == "Transport" else ""
    shopping_selected = "selected" if expense["category"] == "Shopping" else ""
    bills_selected = "selected" if expense["category"] == "Bills" else ""
    other_selected = "selected" if expense["category"] == "Other" else ""

    expense_date = expense["date"] if expense["date"] else ""

    return f"""
    <html>

    <head>
        <title>Edit Expense</title>
    </head>

    <body>

        <h1>Edit Expense</h1>

        <form method="POST">

            <label>Description:</label>

            <input type="text"
                   name="description"
                   value="{expense["description"]}"
                   required>

            <br><br>

            <label>Amount (€):</label>

            <input type="number"
                   name="amount"
                   value="{expense["amount"]:.2f}"
                   step="0.01"
                   required>

            <br><br>

            <label>Category:</label>

            <select name="category">

                <option value="Food" {food_selected}>Food</option>
                <option value="Transport" {transport_selected}>Transport</option>
                <option value="Shopping" {shopping_selected}>Shopping</option>
                <option value="Bills" {bills_selected}>Bills</option>
                <option value="Other" {other_selected}>Other</option>

            </select>

            <br><br>

            <label>Date:</label>

            <input type="date"
                   name="date"
                   value="{expense_date}"
                   required>

            <br><br>

            <button type="submit">
                Save Changes
            </button>

        </form>

        <br>

        <a href="/">Back to Expense Tracker</a>

    </body>

    </html>
    """

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
