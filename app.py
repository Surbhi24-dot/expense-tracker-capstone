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
       "DELETE FROM expenses WHERE id = %s",
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
        connection.close()

        return redirect("/")

    expense = connection.execute(
        "SELECT * FROM expenses WHERE id = %s",
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
