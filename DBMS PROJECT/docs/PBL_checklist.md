# PBL checklist based on uploaded CSL0311 brief

| Requirement from brief | Current project |
|---|---|
| Stakeholder categories | Creator, Backer, Admin; Platform Operator can be described in report |
| 10–15 tables | 11 included |
| ER diagram with 10+ entities | Update diagram to match the 11 actual tables |
| 1NF/2NF/3NF/BCNF worksheets | Prepare and verify separately |
| 15 key constraints and 10 CHECK constraints | Basic PK/FK/UNIQUE/CHECK included; additional evidence needed |
| 5 indexes | 5 included |
| 5 views | Not included yet |
| Procedures/functions/triggers | Not included in SQLite starter |
| 20 meaningful queries | 22 query examples included; execute and capture output |
| Transaction and concurrency demonstrations | Not fully implemented |
| Security, role access and audit | App role checks and audit records; DB-level least privilege not implemented |
| Performance before/after | Not measured |
| Schema migrations and rollback | Version table included; executable migration/rollback scripts still needed |
| Automated tests | Run manual workflow tests; additional tests needed |
| 5 operational, 5 management, 3 trend, 2 exception reports and dashboard | Basic management summary and dashboard only |
| AI usage log and AI output audit | Record actual prompts, manual review and test results |
| Backup and recovery | Demonstrate copying/restoring `crowdfunding.db` |
| Git repository and deployment | Not included |

## Stakeholders
1. Creator: submits campaign.
2. Backer: browses and pledges.
3. Administrator: approves campaigns and views reports.
4. Platform operator: maintains application, database and backups.

## Business rules
1. Email is unique.
2. New campaign starts as Pending.
3. Campaign goal must be positive.
4. Only approved campaigns accept pledges.
5. Only Backers can pledge.
6. Pledge amount must be positive.
7. Every campaign belongs to one Creator.
8. Every pledge belongs to one Backer and one campaign.
9. Only Admin can approve/reject campaigns.
10. Payment entries are simulated; no actual money moves.
