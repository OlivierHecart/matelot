# Matelot: a [seaborn](https://seaborn.pydata.org/index.html) extension

## Brightness grouping

Add a grouping variable that will produce lines or boxplots with different brightnesses when using `lineplot` or `boxplot`.

Example:
```
matelot.lineplot(
    data=df,
    x="payload",
    y="msg/s",
    estimator="median",
    hue="branch",
    brightness="binary",
)
```

## Interactive annotations

Generate svg files that show plotted values as annotations when placing mouse cursor over a plotted line.

Example:
```
fig, ax = plt.subplots()

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
    ax=ax,
)

fig = matelot.interactive(fig)
fig.savefig("lineplot2.svg")
```

Example using implicit interface:
```
matelot.lineplot(
    data=df,
    x="payload",
    y="msg/s",
    estimator="median",
    hue="branch",
    brightness="binary",
    annotated=True,
)

matelot.savefig("linepot.svg")
```


## Example of generated svg:

<img src="https://github.com/OlivierHecart/matelot/blob/main/lineplot.svg?raw=true">

Note: to include the svg image in a web page, use an iframe:
```
<iframe src="lineplot.svg" style="border:none; width:100%; height:100vh;"></iframe>
```