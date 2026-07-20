from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


# Create Database Tables
def create_table():

    conn = sqlite3.connect("waste.db")
    cur = conn.cursor()

    # Waste Bin Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bins(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT,
        level INTEGER,
        status TEXT
    )
    """)


    # User Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT,
        phone TEXT,
        address TEXT
    )
    """)


    # Pickup Request Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pickup_requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        waste_type TEXT,
        location TEXT,
        date TEXT,
        status TEXT
    )
    """)


    conn.commit()
    conn.close()


# Call Database Creation
create_table()



# Home Page
@app.route("/")
def home():
    return render_template("index.html")



# Admin Login
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            return redirect("/dashboard")

        else:
            return "Invalid Username or Password"


    return render_template("login.html")



# User Registration
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]
        address = request.form["address"]


        conn = sqlite3.connect("waste.db")
        cur = conn.cursor()


        cur.execute(
            """
            INSERT INTO users(name,email,password,phone,address)
            VALUES(?,?,?,?,?)
            """,
            (name,email,password,phone,address)
        )


        conn.commit()
        conn.close()


        return redirect("/user_login")


    return render_template("register.html")



# User Login
@app.route("/user_login", methods=["GET","POST"])
def user_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]


        conn = sqlite3.connect("waste.db")
        cur = conn.cursor()


        cur.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email,password)
        )


        user = cur.fetchone()


        conn.close()


        if user:
            return redirect("/user_dashboard")

        else:
            return "Invalid Email or Password"



    return render_template("user_login.html")



# User Dashboard
@app.route("/user_dashboard")
def user_dashboard():

    return render_template("user_dashboard.html")

# Waste Pickup Request
@app.route("/pickup", methods=["GET","POST"])
def pickup():

    if request.method == "POST":

        waste_type = request.form["waste_type"]
        location = request.form["location"]
        date = request.form["date"]


        conn = sqlite3.connect("waste.db")
        cur = conn.cursor()


        cur.execute(
            """
            INSERT INTO pickup_requests
            (user_id,waste_type,location,date,status)
            VALUES(?,?,?,?,?)
            """,
            (1,waste_type,location,date,"Pending")
        )


        conn.commit()
        conn.close()


        return "Pickup Request Sent Successfully"


    return render_template("pickup.html")



# Admin Dashboard
@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("waste.db")
    cur = conn.cursor()


    # Bin Count
    cur.execute("SELECT COUNT(*) FROM bins")
    total = cur.fetchone()[0]


    cur.execute("SELECT COUNT(*) FROM bins WHERE status='Full'")
    full = cur.fetchone()[0]


    cur.execute("SELECT COUNT(*) FROM bins WHERE status='Empty'")
    empty = cur.fetchone()[0]


    # Pickup Request Count
    cur.execute("SELECT COUNT(*) FROM pickup_requests")
    requests = cur.fetchone()[0]


    cur.execute("SELECT COUNT(*) FROM pickup_requests WHERE status='Pending'")
    pending = cur.fetchone()[0]


    cur.execute("SELECT COUNT(*) FROM pickup_requests WHERE status='Completed'")
    completed = cur.fetchone()[0]


    conn.close()


    return render_template(
        "dashboard.html",
        total=total,
        full=full,
        empty=empty,
        requests=requests,
        pending=pending,
        completed=completed
    )

# Add Waste Bin
@app.route("/add", methods=["GET","POST"])
def add():

    if request.method == "POST":

        location = request.form["location"]
        level = request.form["level"]
        status = request.form["status"]


        conn = sqlite3.connect("waste.db")
        cur = conn.cursor()


        cur.execute(
            "INSERT INTO bins(location,level,status) VALUES(?,?,?)",
            (location,level,status)
        )


        conn.commit()
        conn.close()


        return redirect("/view")


    return render_template("add_bin.html")



# View Waste Bins
@app.route("/view")
def view():

    conn = sqlite3.connect("waste.db")
    cur = conn.cursor()


    cur.execute("SELECT * FROM bins")

    data = cur.fetchall()


    conn.close()


    return render_template(
        "view_bins.html",
        data=data
    )



# Delete Bin
@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("waste.db")
    cur = conn.cursor()


    cur.execute(
        "DELETE FROM bins WHERE id=?",
        (id,)
    )


    conn.commit()
    conn.close()


    return redirect("/view")



# Update Bin
# View Pickup Requests
@app.route("/requests")
def requests():

    conn = sqlite3.connect("waste.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM pickup_requests")

    data = cur.fetchall()

    conn.close()

    return render_template(
        "requests.html",
        data=data
    )
@app.route("/update/<int:id>", methods=["GET","POST"])
def update(id):

    conn = sqlite3.connect("waste.db")
    cur = conn.cursor()


    if request.method == "POST":

        location = request.form["location"]
        level = request.form["level"]
        status = request.form["status"]


        cur.execute(
            """
            UPDATE bins
            SET location=?, level=?, status=?
            WHERE id=?
            """,
            (location,level,status,id)
        )


        conn.commit()
        conn.close()


        return redirect("/view")



    cur.execute(
        "SELECT * FROM bins WHERE id=?",
        (id,)
    )


    data = cur.fetchone()


    conn.close()


    return render_template(
        "update_bin.html",
        data=data
    )
# Update Pickup Status
@app.route("/update_request/<int:id>")
def update_request(id):

    conn = sqlite3.connect("waste.db")
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE pickup_requests
        SET status='Completed'
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/requests")



# Run App
if __name__ == "__main__":
    app.run(debug=True)