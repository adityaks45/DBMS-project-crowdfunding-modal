-- 22 SQLite query examples for the FundFlow project
-- 1 Approved campaigns
SELECT * FROM campaigns WHERE status='Approved';
-- 2 Campaign and creator
SELECT c.title,u.name FROM campaigns c JOIN users u ON c.creator_id=u.user_id;
-- 3 Total pledged per campaign
SELECT c.title,COALESCE(SUM(p.amount),0) total FROM campaigns c LEFT JOIN pledges p ON c.campaign_id=p.campaign_id GROUP BY c.campaign_id;
-- 4 Campaigns that met goal
SELECT c.title,SUM(p.amount) raised,c.goal_amount FROM campaigns c JOIN pledges p ON c.campaign_id=p.campaign_id GROUP BY c.campaign_id HAVING raised>=c.goal_amount;
-- 5 Backer totals
SELECT u.name,SUM(p.amount) total FROM users u JOIN pledges p ON u.user_id=p.backer_id GROUP BY u.user_id ORDER BY total DESC;
-- 6 Campaigns without pledges
SELECT c.title FROM campaigns c LEFT JOIN pledges p ON c.campaign_id=p.campaign_id WHERE p.pledge_id IS NULL;
-- 7 Count by status
SELECT status,COUNT(*) FROM campaigns GROUP BY status;
-- 8 Average pledge
SELECT AVG(amount) FROM pledges;
-- 9 Pledges above average
SELECT * FROM pledges WHERE amount>(SELECT AVG(amount) FROM pledges);
-- 10 Creator campaign count
SELECT u.name,COUNT(c.campaign_id) FROM users u LEFT JOIN campaigns c ON u.user_id=c.creator_id WHERE u.role='Creator' GROUP BY u.user_id;
-- 11 Recent pledges
SELECT * FROM pledges ORDER BY created_at DESC LIMIT 10;
-- 12 Payment demo records
SELECT * FROM payments;
-- 13 Audit trail
SELECT * FROM audit_logs ORDER BY created_at DESC;
-- 14 Campaign updates
SELECT c.title,cu.title,cu.created_at FROM campaign_updates cu JOIN campaigns c ON cu.campaign_id=c.campaign_id;
-- 15 Successful campaigns
SELECT c.title,SUM(p.amount) raised FROM campaigns c JOIN pledges p ON c.campaign_id=p.campaign_id WHERE c.status='Successful' GROUP BY c.campaign_id;
-- 16 Pending campaigns
SELECT * FROM campaigns WHERE status='Pending';
-- 17 Top 5 by amount
SELECT c.title,COALESCE(SUM(p.amount),0) raised FROM campaigns c LEFT JOIN pledges p ON c.campaign_id=p.campaign_id GROUP BY c.campaign_id ORDER BY raised DESC LIMIT 5;
-- 18 Progress percent
SELECT c.title,c.goal_amount,COALESCE(SUM(p.amount),0) raised,ROUND(COALESCE(SUM(p.amount),0)*100/c.goal_amount,2) progress FROM campaigns c LEFT JOIN pledges p ON c.campaign_id=p.campaign_id GROUP BY c.campaign_id;
-- 19 User count by role
SELECT role,COUNT(*) FROM users GROUP BY role;
-- 20 Campaigns created in last 30 days
SELECT * FROM campaigns WHERE created_at>=datetime('now','-30 days');
-- 21 Rank campaigns
SELECT title,raised,RANK() OVER(ORDER BY raised DESC) campaign_rank FROM (SELECT c.title,COALESCE(SUM(p.amount),0) raised FROM campaigns c LEFT JOIN pledges p ON c.campaign_id=p.campaign_id GROUP BY c.campaign_id);
-- 22 Schema version history
SELECT * FROM schema_versions ORDER BY version_id;
