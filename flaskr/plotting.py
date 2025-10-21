"""
This code contains functions regarding the plotting of graphs, barcharts, piecharts, etc.
Based on data contained within the database
"""
from matplotlib.figure import Figure


def BarchartPlot():
    # Test data to plot
    x = ['Accounting', 'IT', 'Security', 'Janitorial']
    y1 = [4, 23, 14, 2]         # Accesses today
    y2 = [13, 74, 36, 14]       # Accesses this week
    y3 = [142, 362, 193, 102]   # Accesses this quarter
    y4 = [2, 4, 2, 1]           # Average accessed / day

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
