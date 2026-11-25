
from flask import Flask, request, redirect, session, render_template_string
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "fundflow_college_demo_secret"

DB_NAME = "crowdfunding.db"


# DATABASE CONNECTION
def get_db():
    con = sqlite3.connect(DB_NAME)
    con.row_factory = sqlite3.Row
    return con


# DATABASE INITIALIZATION
def init_db():
    con = get_db()

    con.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    con.execute("""
    CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        creator_id INTEGER,
        title TEXT NOT NULL,
        purpose TEXT,
        goal REAL NOT NULL,
        raised REAL DEFAULT 0,
        status TEXT DEFAULT 'Pending',
        FOREIGN KEY (creator_id) REFERENCES users(id)
    )
    """)

    con.execute("""
    CREATE TABLE IF NOT EXISTS pledges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id INTEGER,
        backer_id INTEGER,
        amount REAL,
        status TEXT DEFAULT 'Recorded',
        FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
        FOREIGN KEY (backer_id) REFERENCES users(id)
    )
    """)

    con.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pledge_id INTEGER,
        amount REAL,
        payment_status TEXT DEFAULT 'Demo Recorded'
    )
    """)

    # Default admin account
    admin = con.execute(
        "SELECT id FROM users WHERE email=?",
        ("admin@fundflow.demo",)
    ).fetchone()

    if not admin:
        con.execute("""
        INSERT INTO users(name,email,password,role)
        VALUES(?,?,?,?)
        """, (
            "Admin",
            "admin@fundflow.demo",
            generate_password_hash("Admin123!"),
            "Admin"
        ))

    con.commit()
    con.close()


# LOGIN REQUIRED
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return func(*args, **kwargs)
    return wrapper


# WEBSITE DESIGN
STYLE = """
<style>
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f3f5fa;
    color: #202b43;
}
nav {
    background: #172554;
    color: white;
    padding: 18px 7%;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
nav a {
    color: white;
    text-decoration: none;
    margin-left: 15px;
}
.container {
    max-width: 1000px;
    margin: 35px auto;
    padding: 20px;
}
.card {
    background: white;
    padding: 22px;
    border-radius: 12px;
    margin-bottom: 18px;
    box-shadow: 0 3px 12px #00000010;
}
input, textarea, select {
    display: block;
    width: 100%;
    box-sizing: border-box;
    padding: 12px;
    margin: 12px 0;
    border: 1px solid #ccd3df;
    border-radius: 7px;
}
button, .btn {
    background: #2563eb;
    color: white;
    padding: 11px 18px;
    border: 0;
    border-radius: 7px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
}
.danger { background: #dc2626; }
.success { color: #15803d; }
.muted { color: #64748b; }
</style>
"""

PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>FundFlow - Crowdfunding Platform</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
""" + STYLE + """
</head>
<body>
<nav>
    <strong>FundFlow</strong>
    <div>
    <a href="/">Home</a>
    {% if session.get('user_id') %}
        <a href="/dashboard">Dashboard</a>
        <a href="/logout">Logout</a>
    {% else %}
        <a href="/login">Login</a>
        <a href="/register">Register</a>
    {% endif %}
    </div>
</nav>

<div class="container">
{% with messages = get_flashed_messages() %}
{% for message in messages %}
<div class="card success">{{ message }}</div>
{% endfor %}
{% endwith %}

{{ content|safe }}
</div>
</body>
</html>
"""


def page(content):
    return render_template_string(PAGE, content=content)


# HOME PAGE
@app.route("/")
def home():
    con = get_db()
    campaigns = con.execute("""
        SELECT campaigns.*, users.name
        FROM campaigns
        JOIN users ON campaigns.creator_id=users.id
        WHERE campaigns.status='Approved'
        ORDER BY campaigns.id DESC
    """).fetchall()
    con.close()

    html = """
    <div class="card">
        <h1>Welcome to FundFlow</h1>
        <p>Support ideas. Help creators. Make a difference.</p>
        <a class="btn" href="/register">Get Started</a>
    </div>
    <h2>Approved Campaigns</h2>
    """

    if not campaigns:
        html += '<div class="card">No approved campaigns yet.</div>'

    for c in campaigns:
        html += f"""
        <div class="card">
            <h2>{c['title']}</h2>
            <p>{c['purpose']}</p>
            <p>Creator: {c['name']}</p>
            <p>Goal: ₹{c['goal']:.2f}</p>
            <p>Raised: ₹{c['raised']:.2f}</p>
            <a class="btn" href="/campaign/{c['id']}">View Campaign</a>
        </div>
        """

    return page(html)


# REGISTRATION
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        role = request.form["role"]

        if role not in ["Creator", "Backer"]:
            return "Invalid role"

        con = get_db()
        try:
            con.execute("""
                INSERT INTO users(name,email,password,role)
                VALUES(?,?,?,?)
            """, (
                name, email,
                generate_password_hash(password),
                role
            ))
            con.commit()
        except sqlite3.IntegrityError:
            con.close()
            return "Email already registered. Go back and try another."
        con.close()

        return redirect("/login")

    return page("""
    <div class="card">
    <h2>Create Account</h2>
    <form method="post">
        <input name="name" placeholder="Full Name" required>
        <input name="email" type="email" placeholder="Email" required>
        <input name="password" type="password" placeholder="Password" required>
        <select name="role">
            <option value="Creator">Creator</option>
            <option value="Backer">Backer</option>
        </select>
        <button type="submit">Register</button>
    </form>
    </div>
    """)


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        con = get_db()
        user = con.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()
        con.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            return redirect("/dashboard")

        return "Invalid email or password. Go back and retry."

    return page("""
    <div class="card">
    <h2>Login</h2>
    <form method="post">
        <input name="email" type="email" placeholder="Email" required>
        <input name="password" type="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
    </div>
    """)


# DASHBOARD
@app.route("/dashboard")
@login_required
def dashboard():
    role = session["role"]
    con = get_db()

    if role == "Admin":
        campaigns = con.execute("""
            SELECT campaigns.*, users.name
            FROM campaigns JOIN users
            ON campaigns.creator_id=users.id
            ORDER BY campaigns.id DESC
        """).fetchall()

        html = "<div class='card'><h2>Admin Dashboard</h2></div>"

        for c in campaigns:
            html += f"""
            <div class="card">
            <h3>{c['title']}</h3>
            <p>Creator: {c['name']}</p>
            <p>Status: {c['status']}</p>
            <p>Goal: ₹{c['goal']:.2f}</p>
            """

            if c["status"] == "Pending":
                html += f"""
                <form method="post" action="/approve/{c['id']}">
                    <button>Approve Campaign</button>
                </form>
                """

            html += "</div>"

    elif role == "Creator":
        campaigns = con.execute(
            "SELECT * FROM campaigns WHERE creator_id=?",
            (session["user_id"],)
        ).fetchall()

        html = """
        <div class="card">
        <h2>Creator Dashboard</h2>
        <h3>Create Campaign</h3>
        <form method="post" action="/create">
            <input name="title" placeholder="Campaign Title" required>
            <textarea name="purpose" placeholder="Campaign Purpose" required></textarea>
            <input name="goal" type="number" min="1" step="0.01"
                   placeholder="Funding Goal" required>
            <button>Create Campaign</button>
        </form>
        </div>
        <h2>My Campaigns</h2>
        """

        for c in campaigns:
            html += f"""
            <div class="card">
            <h3>{c['title']}</h3>
            <p>Goal: ₹{c['goal']:.2f}</p>
            <p>Raised: ₹{c['raised']:.2f}</p>
            <p>Status: {c['status']}</p>
            </div>
            """

    else:
        pledges = con.execute("""
            SELECT pledges.*, campaigns.title
            FROM pledges JOIN campaigns
            ON pledges.campaign_id=campaigns.id
            WHERE pledges.backer_id=?
        """, (session["user_id"],)).fetchall()

        html = "<div class='card'><h2>Backer Dashboard</h2></div>"

        for p in pledges:
            html += f"""
            <div class="card">
            <h3>{p['title']}</h3>
            <p>Pledged: ₹{p['amount']:.2f}</p>
            <p>Status: {p['status']}</p>
            </div>
            """

    con.close()
    return page(html)


# CREATE CAMPAIGN
@app.route("/create", methods=["POST"])
@login_required
def create_campaign():
    if session["role"] != "Creator":
        return "Only creators can create campaigns."

    try:
        goal = float(request.form["goal"])
        if goal <= 0:
            return "Goal must be greater than zero."

        con = get_db()
        con.execute("""
            INSERT INTO campaigns(creator_id,title,purpose,goal)
            VALUES(?,?,?,?)
        """, (
            session["user_id"],
            request.form["title"].strip(),
            request.form["purpose"].strip(),
            goal
        ))
        con.commit()
        con.close()

    except ValueError:
        return "Enter a valid funding goal."

    return redirect("/dashboard")


# APPROVE CAMPAIGN
@app.route("/approve/<int:cid>", methods=["POST"])
@login_required
def approve_campaign(cid):
    if session["role"] != "Admin":
        return "Admin access required."

    con = get_db()
    con.execute("""
        UPDATE campaigns SET status='Approved'
        WHERE id=? AND status='Pending'
    """, (cid,))
    con.commit()
    con.close()

    return redirect("/dashboard")


# CAMPAIGN DETAILS
@app.route("/campaign/<int:cid>")
def campaign_detail(cid):
    con = get_db()
    c = con.execute("""
        SELECT campaigns.*, users.name
        FROM campaigns JOIN users
        ON campaigns.creator_id=users.id
        WHERE campaigns.id=? AND campaigns.status='Approved'
    """, (cid,)).fetchone()
    con.close()

    if not c:
        return "Campaign not found."

    html = f"""
    <div class="card">
    <h1>{c['title']}</h1>
    <p>{c['purpose']}</p>
    <p>Creator: {c['name']}</p>
    <p>Goal: ₹{c['goal']:.2f}</p>
    <p>Raised: ₹{c['raised']:.2f}</p>
    """

    if session.get("role") == "Backer":
        html += f"""
        <form method="post" action="/pledge/{cid}">
            <input name="amount" type="number" min="1" step="0.01"
                   placeholder="Pledge Amount" required>
            <button>Pledge Now</button>
        </form>
        """

    html += "</div>"
    return page(html)


# RECORD PLEDGE
@app.route("/pledge/<int:cid>", methods=["POST"])
@login_required
def pledge(cid):
    if session["role"] != "Backer":
        return "Only backers can pledge."

    try:
        amount = float(request.form["amount"])
        if amount <= 0:
            return "Amount must be greater than zero."

        con = get_db()
        campaign = con.execute("""
            SELECT id FROM campaigns
            WHERE id=? AND status='Approved'
        """, (cid,)).fetchone()

        if not campaign:
            con.close()
            return "Campaign is unavailable."

        cursor = con.execute("""
            INSERT INTO pledges(campaign_id,backer_id,amount)
            VALUES(?,?,?)
        """, (cid, session["user_id"], amount))

        pledge_id = cursor.lastrowid

        # Demo payment record only; no real money is transferred.
        con.execute("""
            INSERT INTO payments(pledge_id,amount,payment_status)
            VALUES(?,?,?)
        """, (pledge_id, amount, "Demo Recorded"))

        con.execute("""
            UPDATE campaigns SET raised=raised+?
            WHERE id=?
        """, (amount, cid))

        con.commit()
        con.close()

    except ValueError:
        return "Enter a valid amount."

    return redirect("/dashboard")


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# START APPLICATION
if __name__ == "__main__":
    init_db()
    app.run(debug=True)

