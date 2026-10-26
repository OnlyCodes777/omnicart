# OmniCart QA project

This project is a small online-store dashboard with a Python API so it can be tested using manual checks, Jira, and Apache JMeter. The API and web server use Python's standard library; you do not need Java to run the app. Java is only needed if you choose to run JMeter.

## Project contents

- `server.py` — serves the dashboard and API on port 8000.
- `index.html`, `app.js`, `styles.css` — dashboard front end.
- `api.html` — a small page to try the forecast and order API in a browser.
- `OmniCart_TestPlan.jmx` — JMeter test plan (20 virtual users, 10-second ramp-up, 5 loops by default).
- `jira_test_cases.csv` — 12 starter Jira tasks/test cases.
- `make_jmx.py`, `make_csv.py` — optional scripts that regenerate the JMeter plan and CSV.

The demo now includes 35 sample orders and 24 catalog products across multiple categories. These records are local sample data; orders created through the API are kept in memory and reset when the server restarts.

## 1. Start OmniCart on Windows

1. Install Python 3 from [python.org](https://www.python.org/downloads/) if `py --version` does not work. In the installer, enable **Add Python to PATH**.
2. Extract this project folder if it is still in a ZIP.
3. Open the folder in File Explorer. Click the address bar, type `powershell`, and press Enter.
4. Run:

   ```powershell
   py server.py
   ```

   Keep this window open. The server prints the address it is using.
5. Open `http://localhost:8000` for the dashboard or `http://localhost:8000/api.html` for the API demo.

To stop the server, focus the PowerShell window and press Ctrl+C. The data is in memory, so restarting the server resets orders to the original sample orders.

## 2. Try the regression forecast

The API fits a simple linear regression model for `weekly_sales = intercept + slope × week`. It uses generated sample data for 52 weeks: weeks 1–42 train the model, and the last 10 weeks are held out to measure performance. This is a teaching/demo model, not a real sales forecast. The `test_r2` and `test_mae` values are measured on the held-out weeks.

In a browser, open `http://localhost:8000/api.html`, enter a week number, and click **Predict**. Or open these API URLs:

- `http://localhost:8000/api/model` — model coefficients and evaluation metrics.
- `http://localhost:8000/api/forecast?week=25` — prediction for week 25.
- `http://localhost:8000/api/forecast?week=abc` — invalid input; expected HTTP 400.

Other endpoints are `GET /api/health`, `GET /api/orders`, `GET /api/products`, and `POST /api/orders`. A valid order POST needs JSON such as `{"customer":"Asha Rao","email":"asha@example.com","total":99.5}` and returns HTTP 201. Invalid order data returns HTTP 400. Orders are not saved after stopping the server.

## 3. Create a Jira project and import the cases

1. In Jira, create a project named **OmniCart QA** (a team-managed Kanban project is fine).
2. Try Jira's CSV import for issues and select `jira_test_cases.csv`. Map `Summary`, `Issue Type`, `Description`, `Priority`, and `Labels` to the corresponding Jira fields. Set the project for the imported issues if Jira asks.
3. If your Jira account does not show issue CSV import, create a Task manually for each row. The CSV descriptions include the steps and expected result.
4. Before a run, move its task to **In Progress**. After running it, add a comment with the actual result, pass/fail, date, and evidence/screenshot, then move it to **Done** if it passed. If it failed, create a Bug with reproduction steps and link it to the test task.

Jira plans and issue types differ by account; if the CSV importer does not accept the `Issue Type` or `Priority` mapping, omit that mapping and create the issues as Tasks, then set priority in Jira.

## 4. Run functional/API checks with JMeter

JMeter requires Java. Install a current supported JDK (JDK 17 or newer is suitable), then open a **new** PowerShell window and check:

```powershell
java -version
```

Download the Apache JMeter binary ZIP from [jmeter.apache.org](https://jmeter.apache.org/download_jmeter.cgi), extract it, and launch `bin\jmeter.bat`. In JMeter choose **File > Open** and select `OmniCart_TestPlan.jmx` from this project. Make sure the Python server is still running on port 8000, then press the green Start button.

The plan sends eight kinds of requests: dashboard, health, products, model metrics, a valid forecast, an invalid forecast, a valid order, and an invalid order. It expects HTTP 200/201 for valid requests and HTTP 400 for deliberately invalid requests; those 400 responses are expected passes. Check **View Results Tree** for individual assertions and **Summary Report** or **Aggregate Report** for timing and error percentage. An error percentage above 0 means a request or assertion failed; inspect View Results Tree to see which one.

For a load comparison, run the plan three times and change **Users > Number of Threads** to 20, 50, and 100. Keep ramp-up at 10 seconds and loops at 5 for each run. Record the actual average, 90th/95th percentile if shown, throughput, and error percentage in Jira; do not claim performance thresholds as passed unless your measured results meet them. Disable **View Results Tree** for the larger runs because storing every response can use significant memory and affect measurements. Take screenshots of the Aggregate Report for each run.

To run without the GUI and save a results file, from the JMeter `bin` folder use:

```powershell
.\jmeter.bat -n -t "C:\path\to\omnicart-testing\OmniCart_TestPlan.jmx" -l results.jtl
```

Replace the example path with the actual folder path. Do not reuse an existing `results.jtl`; choose a new filename for each run.

## 5. Suggested course report

Include the goal and environment (Windows, Python/JMeter versions, local machine), test cases and expected results, Jira screenshots, the three load-test result tables/screenshots, any bugs found, and a short conclusion. State clearly that JMeter measures this local demo server and that the regression model uses generated sample data with only four held-out observations. Results depend on the computer running the test and are not evidence of production-scale capacity.
