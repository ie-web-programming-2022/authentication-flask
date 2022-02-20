from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine

app = Flask(__name__)
engine = create_engine("sqlite:///paymepal.db")
app.config["SECRET_KEY"] = "this is a secret, change me!"


@app.route("/login")
def login():
    return render_template(
        "login.html")

@app.route("/login", methods=["POST"])
def handle_login():
    username = request.form["user"]
    password = request.form["password"]

    query = f"""
    SELECT id
    FROM users
    WHERE username='{username}'
    AND password='{password}'
    """

    with engine.connect() as connection:
        user = connection.execute(query).fetchone()

        if user:
            session["username"] = username
            session["user_id"] = user[0]
            
        return redirect(url_for("index"))

# In order to logout we just delete the values from the session
@app.route("/logout")
def logout():
    session.pop("username")
    session.pop("user_id")

    return redirect(url_for("index"))

@app.route("/")
def index():
    with engine.connect() as connection:
        transactions = []
        if "username" in session:
            transactions_query = f"""
            SELECT t.amount, t.currency, s.name
            FROM transactions t
            INNER JOIN users u on t.user_id=u.id
            INNER JOIN shops s on t.shop_id=s.id
            WHERE u.username='{session["username"]}'
            """
            transactions = connection.execute(transactions_query).fetchall()

        return render_template(
            "index.html",
            transactions=transactions)


app.run(debug = True)
