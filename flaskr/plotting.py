"""
This code contains functions regarding the plotting of graphs, barcharts, piecharts, etc.
Based on data contained within the database
"""
import datetime
from matplotlib.figure import Figure
import flaskr.querying as querying


# Separate const because it's too long
QUARTER_QUERY = """
    SELECT COUNT(*) 
    FROM accessLog
    WHERE strftime('%Y', accessed) = strftime('%Y', 'now')
    AND ((CAST(strftime('%m', accessed) AS INTEGER) - 1)/3 + 1) = ((CAST(strftime('%m', 'now') AS INTEGER) - 1)/3 + 1)
"""

def get_days_in_quarter():
    # Get the start and end of the quarter
    now = datetime.datetime.now()
    current_month = now.month
    start_month = (current_month - 1) // 3 * 3 + 1  # First month of the current quarter
    start_date = datetime.datetime(now.year, start_month, 1)
    if current_month % 3 == 0:
        end_date = datetime.datetime(now.year, current_month, 31)
    else:
        end_month = start_month + 2  # Last month of the current quarter
        end_date = datetime.datetime(now.year, end_month + 1, 1) - datetime.timedelta(days=1)

    # Calculate the number of days in the current quarter
    delta = end_date - start_date
    return delta.days + 1  # Include end date

def BarchartPlot(app):
    # Test data to plot
    x = ['Accounting', 'IT', 'Security', 'Janitorial']
    
    # Get access counts
    with app.app_context():
        y1_result = querying.execute_sql_query("SELECT COUNT(*) FROM accessLog WHERE accessed >= DATE('now') AND accessed < DATE('now', '+1 day')", -1)
        y2_result = querying.execute_sql_query("SELECT COUNT(*) FROM accessLog WHERE accessed >= date('now', 'weekday 0', '-6 day') AND accessed < date('now', 'weekday 0', '+1 day')", -1)
        y3_result = querying.execute_sql_query(QUARTER_QUERY, -1)
    
    # Extracting values from query results
    y1 = [r[0] for r in y1_result]  # Number of accesses today
    y2 = [r[0] for r in y2_result]  # Number of accesses this week
    y3 = [r[0] for r in y3_result]  # Total number of accesses this quarter

    # Calculate average accesses per day for this quarter (y4)
    total_accesses = y3[0] if y3 else 0  # Total accesses from the query result
    days_in_quarter = get_days_in_quarter()  # Calculate the number of days in the quarter
    y4 = [total_accesses / days_in_quarter] * len(x) if days_in_quarter else [0] * len(x)  # Average accesses per day for all departments

    print("Accesses Today:", y1)
    print("Accesses This Week:", y2)
    print("Accesses This Quarter:", y3)
    print("Average Accesses per Day This Quarter:", y4)

    # Create the figure for the bar chart
    fig = Figure(figsize=(10, 8), dpi=100)
    
    ax1 = fig.add_subplot(2, 2, 1)  # 2 rows, 2 columns, position 1
    ax1.bar(x, y1, color='blue')
    ax1.set_title('Accesses today')
    ax1.set_xlabel('Departments')
    ax1.set_ylabel('Authorised Accesses')

    ax2 = fig.add_subplot(2, 2, 2)  # 2 rows, 2 columns, position 2
    ax2.bar(x, y2, color='red')
    ax2.set_title('Accesses this week')
    ax2.set_xlabel('Departments')
    ax2.set_ylabel('Authorised Accesses')

    ax3 = fig.add_subplot(2, 2, 3)  # 2 rows, 2 columns, position 3
    ax3.bar(x, y3, color='purple')
    ax3.set_title('Accesses this quarter')
    ax3.set_xlabel('Departments')
    ax3.set_ylabel('Authorised Accesses')

    ax4 = fig.add_subplot(2, 2, 4)  # 2 rows, 2 columns, position 4
    ax4.bar(x, y4, color='green')
    ax4.set_title('Average accesses / day')
    ax4.set_xlabel('Departments')
    ax4.set_ylabel('Authorised Accesses')

    fig.tight_layout(pad=3)  # Adjust layout to prevent overlap
    return fig
