from flask import Flask, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)


def get_db_connection():
    connection = sqlite3.connect("expenses.db")
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


@app.route("/", methods=["GET", "POST"])
def home():

    connection = get_db_connection()

    if request.method == "POST":

        description = request.form["description"]
        amount = float(request.form["amount"])
        category = request.form["category"]
        expense_date = request.form["date"]

        connection.execute(
            "INSERT INTO expenses (description, amount, category, date) VALUES (?, ?, ?, ?)",
            (description, amount, category, expense_date)
        )

        connection.commit()
        connection.close()

        return redirect("/")

    expenses = connection.execute(
        "SELECT * FROM expenses ORDER BY id DESC"
    ).fetchall()

    total = connection.execute(
        "SELECT SUM(amount) FROM expenses"
    ).fetchone()[0]

    if total is None:
        total = 0

    category_totals = connection.execute(
        "SELECT category, SUM(amount) AS total FROM expenses GROUP BY category"
    ).fetchall()

    connection.close()

    html = f"""
    <html>
    <head>
        <title>Expense Tracker</title>
    </head>

    <body>

        <h1>Expense Tracker</h1>

        <h2>Total Expenses: €{total:.2f}</h2>

        <h2>Add Expense</h2>

        <form method="POST">

            <label>Description:</label>
            <input type="text" name="description" required>

            <br><br>

            <label>Amount (€):</label>
            <input type="number" name="amount" step="0.01" required>

            <br><br>

            <label>Category:</label>

            <select name="category">
                <option value="Food">Food</option>
                <option value="Transport">Transport</option>
                <option value="Shopping">Shopping</option>
                <option value="Bills">Bills</option>
                <option value="Other">Other</option>
            </select>

            <br><br>

            <label>Date:</label>
            <input type="date" name="date" value="{date.today()}" required>

            <br><br>

            <button type="submit">Add Expense</button>

        </form>

        <h2>Category Summary</h2>

        <ul>
    """

    for row in category_totals:

        html += f"""
        <li>
            {row["category"]}: €{row["total"]:.2f}
        </li>
        """

    html += """
        </ul>

        <h2>All Expenses</h2>

        <ul>
    """

    for expense in expenses:

        expense_date = expense["date"] if expense["date"] else "No date"

        html += f"""
        <li>

            {expense["description"]}
            - €{expense["amount"]:.2f}
            - {expense["category"]}
            - {expense_date}

            <form method="GET"
                  action="/edit/{expense["id"]}"
                  style="display:inline;">

                <button type="submit">Edit</button>

            </form>

            <form method="POST"
                  action="/delete/{expense["id"]}"
                  style="display:inline;">

                <button type="submit">Delete</button>

            </form>

        </li>
        """

    html += """
        </ul>

    </body>
    </html>
    """

    return html


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/")


@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):

    connection = get_db_connection()

    if request.method == "POST":

        description = request.form["description"]
        amount = float(request.form["amount"])
        category = request.form["category"]
        expense_date = request.form["date"]

        connection.execute(
            """
            UPDATE expenses
            SET description = ?,
                amount = ?,
                category = ?,
                date = ?
            WHERE id = ?
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
        connection.close()

        return redirect("/")

    expense = connection.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (expense_id,)
    ).fetchone()

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
