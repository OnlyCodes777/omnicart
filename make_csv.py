import csv
T=[("TC01 Dashboard page loads","Open http://localhost:8000/index.html. Expected: dashboard renders with no console errors.","High"),
("TC02 Health endpoint","GET /api/health. Expected: 200 and {status: ok}.","High"),
 ("TC03 Product list","GET /api/products. Expected: 200 and 24 products.","Medium"),
("TC04 Model metrics","GET /api/model. Expected: 200, slope about 150, train_r2 above 0.9.","High"),
("TC05 Forecast valid week","GET /api/forecast?week=25. Expected: 200 and predicted_sales near 5750 (2000+150*25, give or take noise).","High"),
("TC06 Forecast invalid week","GET /api/forecast?week=abc and week=0 and week=500. Expected: 400 each time.","High"),
("TC07 Create valid order","POST /api/orders with customer, email, total 99.5. Expected: 201, status Processing, new id.","High"),
("TC08 Reject invalid order","POST /api/orders with empty customer, email without @, total -5. Expected: 400.","High"),
("TC09 Order appears in list","After TC07, GET /api/orders. Expected: new order is present.","Medium"),
("TC10 Unknown endpoint","GET /api/doesnotexist. Expected: 404.","Low"),
("TC11 Load test 20 users","Run OmniCart_TestPlan.jmx with 20 threads. Expected: error rate 0%, avg response under 200 ms.","High"),
("TC12 Load test 100 users","Set threads to 100, ramp-up 10s. Expected: error rate under 1%, record avg and 95th percentile.","High")]
w=csv.writer(open("jira_test_cases.csv","w",newline="",encoding="utf-8"))
w.writerow(["Summary","Issue Type","Description","Priority","Labels"])
for s,d,p in T: w.writerow([s,"Task",d,p,"test-case"])
