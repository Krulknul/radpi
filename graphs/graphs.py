import datetime
from matplotlib import ticker
from matplotlib.dates import DateFormatter, HourLocator, MinuteLocator


def update_proposal_graph(self, data):
    t, s = zip(*data["data"]["result"][0]["values"])
    t = [datetime.datetime.fromtimestamp(int(timestamp)) for timestamp in t]
    s = [float(value) for value in s]

    # find indices where s resets to 1
    reset_indices = [i for i, val in enumerate(s) if val == 1]

    # add the first index manually
    reset_indices = [0] + reset_indices

    # separate line styles for each epoch
    linestyles = [
        "-",
        "--",
    ]

    self.ax1.cla()

    # plot each epoch separately with a different linestyle
    for i in range(len(reset_indices) - 1):
        linestyle = linestyles[i % len(linestyles)]
        self.ax1.plot(
            t[reset_indices[i] : reset_indices[i + 1] + 1],
            s[reset_indices[i] : reset_indices[i + 1] + 1],
            color="white",
            linestyle=linestyle,
        )

    # plot the last epoch
    linestyle = linestyles[(len(reset_indices) - 1) % len(linestyles)]
    self.ax1.plot(
        t[reset_indices[-1] :],
        s[reset_indices[-1] :],
        color="white",
        linestyle=linestyle,
    )

    self.ax1.grid(color="#6e6e6e")
    self.ax1.set_title("Proposals completed (per epoch)", color="white")

    self.ax1.xaxis.set_major_locator(HourLocator())
    self.ax1.xaxis.set_minor_locator(MinuteLocator(byminute=[15, 30, 45]))
    self.ax1.xaxis.set_major_formatter(DateFormatter("%-I%p"))
    self.ax1.yaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=3))

    self.fig1.tight_layout()
    self.fig1.subplots_adjust(left=0.13, right=0.95, top=0.75, bottom=0.21)
    self.graph1.draw()


def update_activity_graph(app, data):
    t, s = zip(*data["data"]["result"][0]["values"])
    t = [datetime.datetime.fromtimestamp(int(timestamp) - 3600) for timestamp in t]
    s = [float(value) for value in s]

    app.ax2.cla()

    # Define colors and line styles for histogram
    colors = ["white"]

    width = datetime.timedelta(hours=1)

    # Generate histogram
    app.ax2.bar(
        t,
        height=s,
        width=width * 0.65,
        color=colors,
        align="edge",
    )

    app.ax2.grid(color="#6e6e6e")
    app.ax2.set_axisbelow(True)
    app.ax2.set_title("Transactions per hour", color="white")

    app.ax2.xaxis.set_major_locator(HourLocator(interval=4))  # 1 hour interval
    app.ax2.xaxis.set_minor_locator(HourLocator(interval=1))  # 1 hour interval
    app.ax2.xaxis.set_major_formatter(DateFormatter("%-I%p"))
    app.ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: round(x)))
    app.ax2.yaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=3))

    app.fig2.tight_layout()
    app.fig2.subplots_adjust(left=0.13, right=0.95, top=0.75, bottom=0.21)
    app.graph2.draw()
