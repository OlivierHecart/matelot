import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import matelot

df = pd.read_csv("data")

df["norm_msg/s"] = df.groupby(["run", "branch", "payload", "binary"])["msg/s"].transform(lambda x: x - x.median())

sns.set_style("whitegrid")

matelot.boxplot(
    data=df,
    x="payload",
    y="norm_msg/s",
    hue="branch",
    hue_order=["1.0", "main", "dev"],
    brightness="binary",
    gap=0.1,
    linewidth=0.8,
    fliersize=1.0,
    fill=False,
)
    
plt.legend(loc="lower right", title="median msg/s")
plt.xlabel("payload size (bytes)")
plt.ylabel("median-centered (msg/s)")
plt.grid(which="major", color="grey", linestyle="-", linewidth=0.2)
plt.grid(which="minor", color="grey", linestyle=":", linewidth=0.1, axis="y")
plt.title("Throughput (msg/s)")

plt.savefig("boxplot.svg")