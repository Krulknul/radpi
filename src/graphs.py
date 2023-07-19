import datetime
from matplotlib import ticker
from matplotlib.dates import (
    DateFormatter,
    HourLocator,
    MinuteLocator,
    DayLocator,
)
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.uix.boxlayout import BoxLayout
from data_fetcher import get_proposal_data, get_activity_data, get_historic_stake
from kivy.clock import mainthread
import matplotlib.pyplot as plt
from util import format_large_number


class GraphWidget(BoxLayout):
    adjust = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(GraphWidget, self).__init__(**kwargs)
        self.fig, self.ax = plt.subplots()
        self.plot = FigureCanvasKivyAgg(self.fig)
        self.add_widget(self.plot)


class ProposalGraph(GraphWidget):
    def __init__(self, **kwargs):
        super(ProposalGraph, self).__init__(**kwargs)
        self.getter = get_proposal_data

    @mainthread
    def update(self, data):
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
        self.ax.cla()

        # plot each epoch separately with a different linestyle
        for i in range(len(reset_indices) - 1):
            linestyle = linestyles[i % len(linestyles)]
            self.ax.plot(
                t[reset_indices[i] : reset_indices[i + 1] + 1],
                s[reset_indices[i] : reset_indices[i + 1] + 1],
                color="white",
                linestyle=linestyle,
            )

        # plot the last epoch
        linestyle = linestyles[(len(reset_indices) - 1) % len(linestyles)]
        self.ax.plot(
            t[reset_indices[-1] :],
            s[reset_indices[-1] :],
            color="white",
            linestyle=linestyle,
        )

        self.ax.grid(color="#6e6e6e")
        self.ax.set_title("Proposals completed (per epoch)", color="white")

        self.ax.xaxis.set_major_locator(HourLocator())
        self.ax.xaxis.set_minor_locator(MinuteLocator(byminute=[15, 30, 45]))
        self.ax.xaxis.set_major_formatter(DateFormatter("%-I%p"))
        self.ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=3))

        self.fig.tight_layout()
        self.fig.subplots_adjust(
            self.adjust[0], self.adjust[1], self.adjust[2], self.adjust[3]
        )
        self.plot.draw()


class ActivityGraph(GraphWidget):
    def __init__(self, **kwargs):
        super(ActivityGraph, self).__init__(**kwargs)
        self.getter = get_activity_data

    @mainthread
    def update(self, data):
        t, s = zip(*data["data"]["result"][0]["values"])
        t = [datetime.datetime.fromtimestamp(int(timestamp) - 3600) for timestamp in t]
        s = [float(value) for value in s]

        self.ax.cla()

        width = datetime.timedelta(hours=1)

        # Generate histogram
        self.ax.bar(
            t,
            height=s,
            width=width * 0.65,
            color="white",
            align="edge",
        )

        self.ax.grid(color="#6e6e6e")
        self.ax.set_axisbelow(True)
        self.ax.set_title("Transactions per hour", color="white")

        self.ax.xaxis.set_major_locator(HourLocator(interval=4))  # 1 hour interval
        self.ax.xaxis.set_minor_locator(HourLocator(interval=1))  # 1 hour interval
        self.ax.xaxis.set_major_formatter(DateFormatter("%-I%p"))
        self.ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: round(x)))
        self.ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=3))

        self.fig.tight_layout()
        self.fig.subplots_adjust(
            self.adjust[0], self.adjust[1], self.adjust[2], self.adjust[3]
        )
        self.plot.draw()


class StakeGraph(GraphWidget):
    def __init__(self, **kwargs):
        super(StakeGraph, self).__init__(**kwargs)
        self.getter = get_historic_stake

    @mainthread
    def update(self, data):
        t = [row["time"] for row in data]
        s = [row["total_xrd_staked"] for row in data]

        self.ax.cla()
        # Generate graph
        self.ax.plot(
            t,
            s,
            color="white",
        )

        self.ax.grid(color="#6e6e6e")
        self.ax.set_axisbelow(True)
        self.ax.set_title("XRD staked over time", color="white")

        self.ax.xaxis.set_major_locator(
            DayLocator(bymonthday=[5, 10, 15, 20, 25, 30])
        )  # 1 hour interval
        self.ax.xaxis.set_minor_locator(DayLocator())  # 1 hour interval
        self.ax.xaxis.set_major_formatter(DateFormatter("%-d/%-m"))
        self.ax.yaxis.set_major_formatter(
            ticker.FuncFormatter(lambda x, _: format_large_number(int(x)))
        )
        self.ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=5))

        self.fig.tight_layout()
        self.fig.subplots_adjust(
            self.adjust[0], self.adjust[1], self.adjust[2], self.adjust[3]
        )
        self.plot.draw()
