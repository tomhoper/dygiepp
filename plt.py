import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


df = pd.read_csv("p_at_kres.tsv", sep="\t",names=["x","y1","y2"])
df=pd.DataFrame({'x': range(1,100), 'y1': df['y1'].values, 'y2': df['y2'].values})

import pdb; pdb.set_trace()
plt.plot( 'x', 'y1', data=df, marker='', markerfacecolor='blue', markersize=12, color='skyblue', linewidth=2)
plt.plot( 'x', 'y2', data=df, marker='', color='olive', linewidth=2)

plt.show()

