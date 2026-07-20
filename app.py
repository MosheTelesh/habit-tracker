from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.config["DATABASE"] = str(Path(__file__).resolve().with_name("habits.db"))
def connect_db():
    connection = sqlite3.connect(app.config["DATABASE"])
    connection.row_factory = sqlite3.Row
    db = connection.cursor()
    return connection, db
@app.route("/")
def index():
    connection, db = connect_db()
    habits = db.execute("SELECT * FROM habits").fetchall()
    connection.close()
    return render_template("index.html", habits=habits)
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        habit = request.form.get("name", "").strip()
        if habit:
            connection, db = connect_db()
            db.execute("INSERT INTO habits (name) VALUES (?)", (habit,))
            connection.commit()
            connection.close()
        return redirect(url_for("index"))
    return render_template("add.html")
@app.route("/done", methods=["POST"])
def done():
    habit_id = request.form.get("id")
    if not habit_id:
        return redirect(url_for("index"))
    connection, db = connect_db()
    row = db.execute("SELECT done FROM habits WHERE id = ?", (habit_id,)).fetchone()
    if row is None:
        connection.close()
        return redirect(url_for("index"))
    new_done = 0 if row["done"] else 1
    db.execute("UPDATE habits SET done = ? WHERE id = ?", (new_done, habit_id))
    connection.commit()
    connection.close()
    return redirect(url_for("index"))
@app.route("/delete", methods=["POST"])
def delete():
    habit_id = request.form.get("id")
    if habit_id:
        connection, db = connect_db()
        db.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        connection.commit()
        connection.close()
    return redirect(url_for("index"))
@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        habit_id = request.form.get("id")
        new_name = request.form.get("name", "").strip()
        if habit_id and new_name:
            connection, db = connect_db()
            db.execute("UPDATE habits SET name = ? WHERE id = ?", (new_name, habit_id))
            connection.commit()
            connection.close()
        return redirect(url_for("index"))
    habit_id = request.args.get("id")
    if not habit_id:
        return redirect(url_for("index"))
    connection, db = connect_db()
    habit = db.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
    connection.close()
    if habit is None:
        return redirect(url_for("index"))
    return render_template("edit.html", habit=habit)
if __name__ == "__main__":
    app.run(debug=True)

    
