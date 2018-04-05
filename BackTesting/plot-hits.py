import sys
import numpy as np
import pandas as pd, csv
import matplotlib.pyplot as plt

if len(sys.argv) > 1:
    plot_file = sys.argv[1]
    df = pd.read_csv(plot_file)
    df.time = pd.to_datetime(df['Date'], format='%d-%m-%Y')
    df.set_index(['Date'],inplace=True)
    ax = df[['Miss','Hit','SQO']].plot()
    ax.set_xlabel("Date")
    ax.set_ylabel("Stocks Count")
    plt.show()
