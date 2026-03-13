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

<img src="https://github.com/OlivierHecart/matelot/blob/main/lineplot.png?raw=true">

