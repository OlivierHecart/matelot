# Matelot: a [seaborn](https://seaborn.pydata.org/index.html) extension

## Brightness grouping

Matelot provides `lineplot` and `boxplot` functions that behave as seaborn `lineplot` and `boxplot` functions with an extra `brightness` argument:

**brightness** : *vector or key in `data`*

- Grouping variable that will produce points with different colors. 

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

<img src="https://github.com/OlivierHecart/matelot/blob/main/lineplot1.svg?raw=true">

## Annotations

Matelot `lineplot` function accepts an extra `annotate` argument:

**annotate** : *bool or literal*
- Automatic annotation of lineplot points with their y value.

Example:
```
matelot.lineplot(
    data=df,
    x="payload",
    y="msg/s",
    estimator="median",
    annotate=True,
)
```

<img src="https://github.com/OlivierHecart/matelot/blob/main/lineplot2.svg?raw=true">

## Interactive annotations

Matelot `lineplot` function `annotate` argument accepts literal value `"interactive"` that makes annotations only appear on mouseover events.

When using the interactive annotation the matplotlib figure needs to be either:
 - turned to an interactive figure through the matelot `interactive` function.
 - saved through the matelot `savefig` function.

 Interactive annotations only work with `svg` output format.

Example:
```
fig, ax = plt.subplots()

matelot.lineplot(
    data=df,
    x="payload",
    y="msg/s",
    marker="o",
    estimator="median",
    annotate=True,
    ax=ax,
)

fig = matelot.interactive(fig)
fig.savefig("lineplot.svg")
```

Example using implicit interface:
```
matelot.lineplot(
    data=df,
    x="payload",
    y="msg/s",
    estimator="median",
    annotate=True,
)

matelot.savefig("lineplot.svg")
```

Note: to include the svg image in a web page, use an iframe:
```
<iframe src="lineplot.svg" style="border:none; width:100%; height:100vh;"></iframe>
```