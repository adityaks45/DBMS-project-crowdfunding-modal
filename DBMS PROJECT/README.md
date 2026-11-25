# FundFlow – Crowdfunding Platform (DBMS PBL)

## Run
1. Extract this ZIP and open the folder in VS Code.
2. Open Terminal and run:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

3. Open http://127.0.0.1:5000

## Demo login
- Admin: `admin@fundflow.demo` / `Admin123!`
- Creator: `creator@fundflow.demo` / `Creator123!`
- Backer: register a new account and choose Backer.

SQLite creates `crowdfunding.db` automatically. No MySQL or Workbench is required.

## Included
Flask web app, role-based login, campaign submission and approval, demo pledges, payment records, demo settlement, 11 database tables, 5 indexes, audit log, schema version table, reports and 22 SQL query examples.

## Important project limitation
The uploaded CSL0311 PBL brief (pages 3–8) asks for more evidence than a simple website: 10–15 tables, 20+ queries, 5 views, procedures/functions/triggers, transactions and concurrency, security/audit, 5 indexes, migration/rollback, testing, performance comparison, AI log/audit, multiple operational/management/trend/exception reports, backup/recovery and deployment. This starter includes 11 tables, 5 indexes and 22 query examples, but does NOT yet implement all those items. Do not claim incomplete items as completed. If MySQL is specifically mandatory, this SQLite prototype must be ported to MySQL.

Pledges, payment and settlement are academic demo records only. No real payment gateway or money transfer is connected. This is not production financial software.
