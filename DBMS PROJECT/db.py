import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash
DB=Path(__file__).with_name("crowdfunding.db")
def get_db():
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con
def init_db():
    db=get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,role TEXT NOT NULL CHECK(role IN ('Creator','Backer','Admin')),created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS campaigns(campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,creator_id INTEGER NOT NULL,title TEXT NOT NULL,purpose TEXT NOT NULL,goal_amount REAL NOT NULL CHECK(goal_amount>0),end_date TEXT,status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending','Approved','Rejected','Successful','Failed')),created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(creator_id) REFERENCES users(user_id));
    CREATE TABLE IF NOT EXISTS pledges(pledge_id INTEGER PRIMARY KEY AUTOINCREMENT,campaign_id INTEGER NOT NULL,backer_id INTEGER NOT NULL,amount REAL NOT NULL CHECK(amount>0),status TEXT DEFAULT 'Recorded',created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(campaign_id) REFERENCES campaigns(campaign_id),FOREIGN KEY(backer_id) REFERENCES users(user_id));
    CREATE TABLE IF NOT EXISTS rewards(reward_id INTEGER PRIMARY KEY AUTOINCREMENT,campaign_id INTEGER NOT NULL,reward_title TEXT NOT NULL,minimum_amount REAL CHECK(minimum_amount>=0),quantity_available INTEGER DEFAULT 0,FOREIGN KEY(campaign_id) REFERENCES campaigns(campaign_id));
    CREATE TABLE IF NOT EXISTS payments(payment_id INTEGER PRIMARY KEY AUTOINCREMENT,pledge_id INTEGER NOT NULL,amount REAL NOT NULL,payment_status TEXT DEFAULT 'Demo recorded',paid_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(pledge_id) REFERENCES pledges(pledge_id));
    CREATE TABLE IF NOT EXISTS disbursements(disbursement_id INTEGER PRIMARY KEY AUTOINCREMENT,campaign_id INTEGER NOT NULL,gross_amount REAL DEFAULT 0,fees REAL DEFAULT 0,net_amount REAL DEFAULT 0,status TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(campaign_id) REFERENCES campaigns(campaign_id));
    CREATE TABLE IF NOT EXISTS campaign_updates(update_id INTEGER PRIMARY KEY AUTOINCREMENT,campaign_id INTEGER NOT NULL,title TEXT,content TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(campaign_id) REFERENCES campaigns(campaign_id));
    CREATE TABLE IF NOT EXISTS refunds(refund_id INTEGER PRIMARY KEY AUTOINCREMENT,pledge_id INTEGER NOT NULL,amount REAL CHECK(amount>=0),status TEXT DEFAULT 'Pending review',refunded_at TEXT,FOREIGN KEY(pledge_id) REFERENCES pledges(pledge_id));
    CREATE TABLE IF NOT EXISTS audit_logs(log_id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,action TEXT,entity TEXT,entity_id INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(user_id) REFERENCES users(user_id));
    CREATE TABLE IF NOT EXISTS schema_versions(version_id INTEGER PRIMARY KEY AUTOINCREMENT,version_name TEXT UNIQUE,description TEXT,applied_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS categories(category_id INTEGER PRIMARY KEY AUTOINCREMENT,category_name TEXT UNIQUE NOT NULL);
    CREATE INDEX IF NOT EXISTS idx_campaign_creator ON campaigns(creator_id);
    CREATE INDEX IF NOT EXISTS idx_campaign_status ON campaigns(status);
    CREATE INDEX IF NOT EXISTS idx_pledge_campaign ON pledges(campaign_id);
    CREATE INDEX IF NOT EXISTS idx_pledge_backer ON pledges(backer_id);
    CREATE INDEX IF NOT EXISTS idx_pledge_created ON pledges(created_at);
    INSERT OR IGNORE INTO schema_versions(version_name,description) VALUES('V1','Core account and campaign tables');
    INSERT OR IGNORE INTO schema_versions(version_name,description) VALUES('V2','Pledges and supporting transaction tables');
    INSERT OR IGNORE INTO schema_versions(version_name,description) VALUES('V3','Audit, categories and performance indexes');
    """)
    if not db.execute("SELECT 1 FROM users WHERE email='admin@fundflow.demo'").fetchone():
        db.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)",("Demo Admin","admin@fundflow.demo",generate_password_hash("Admin123!"),"Admin"))
    if not db.execute("SELECT 1 FROM users WHERE email='creator@fundflow.demo'").fetchone():
        db.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)",("Demo Creator","creator@fundflow.demo",generate_password_hash("Creator123!"),"Creator"))
        uid=db.execute("SELECT user_id FROM users WHERE email='creator@fundflow.demo'").fetchone()[0]
        cur=db.execute("INSERT INTO campaigns(creator_id,title,purpose,goal_amount,status) VALUES(?,?,?,?,?)",(uid,"Community Library Project","A sample campaign to create a small community library.",50000,"Approved"))
        db.execute("INSERT INTO campaign_updates(campaign_id,title,content) VALUES(?,?,?)",(cur.lastrowid,"Welcome","This sample campaign is ready for demonstration."))
    db.commit(); db.close()
