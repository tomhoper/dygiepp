import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# df = pd.read_csv("F1_at_th_res.tsv", sep="\t",names=["x","y1","y2"])
df = pd.read_csv("p_at_kres.tsv", sep="\t",names=["x","y1","y2"])
x = [(xx/453.0)*100 for xx in range(1,100)]

df=pd.DataFrame({'x': x, 'y1': df['y1'].values, 'y2': df['y2'].values})

# import pdb; pdb.set_trace()
plt.plot( 'x', 'y1', data=df, marker='', markerfacecolor='blue', markersize=12, color='skyblue', linewidth=2, label="covid")
plt.plot( 'x', 'y2', data=df, marker='', color='olive', linewidth=2,label="scierc-pretrained")
# plt.xlabel("th",fontsize=20)
# plt.ylabel("F1",fontsize=20)
# plt.legend(fontsize=14)
# plt.title("F1 Rouge scores by threshold",fontsize=20)
# plt.show()


plt.xlabel("K(%)",fontsize=20)
plt.ylabel("P@K",fontsize=20)
plt.legend(fontsize=12)
plt.title("P@K scores",fontsize=20)
plt.show()
