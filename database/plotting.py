"""
This code contains functions regarding the plotting of graphs, barcharts, piecharts, etc.
Based on data contained within the database
"""
from matplotlib.figure import Figure

def testPlot():
    """
    A testing function to see if graphs will show up
    TODO: Remove this once tested
    """
    # the figure that will contain the plot
    fig = Figure(figsize = (5, 5),
                 dpi = 100)

    # list of squares
    y = [i**2 for i in range(101)]

    # adding the subplot and plot graph
    plot1 = fig.add_subplot(111)
    plot1.plot(y)

    return fig
