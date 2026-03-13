import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import matelot


df = pd.read_csv("data")

df = df.astype({"payload": "str"})

sns.set_style("whitegrid")

matelot.lineplot(
    data=df,
    x="payload",
    y="msg/s",
    marker="o",
    estimator="median",
    hue="branch",
    hue_order=["1.0", "main", "dev"],
    brightness="binary",
    annotated=True,
)
    
plt.legend(loc="lower left", title="median msg/s")
plt.xlabel("payload size (bytes)")

plt.ylabel("median (msg/s)")
plt.yscale("log")

plt.grid(which="major", color="grey", linestyle="-", linewidth=0.2)
plt.grid(which="minor", color="grey", linestyle=":", linewidth=0.1, axis="y")
plt.title("Throughput (msg/s)")

matelot.savefig("lineplot.svg")