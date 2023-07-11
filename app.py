import os
import threading
import matplotlib.pyplot as plt
import kivy
from kivy.config import Config


HEIGHT = 320
WIDTH = 480
BAR_HEIGHT_PERCENTAGE = 3.2

# Kivy config setup. Must happen before importing other kivy modules.
Config.set("graphics", "width", f"{WIDTH}")
Config.set("graphics", "height", f"{HEIGHT}")
Config.set("graphics", "resizable", False)
from kivy.core.window import Window

if os.environ["ENVIRONMENT"] == "prod":
    Window.fullscreen = True
    Window.show_cursor = False

from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

from kivy.app import App
from graphs.graphs import update_proposal_graph, update_activity_graph
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from widgets.custom_progress_bar import CustomProgressBar
from widgets.labelwidget import ValuesWidget
from fetcher.data_fetcher import data_fetcher
from kivy.uix.label import Label


kivy.require("2.2.1")


class MyApp(App):
    alert_mode = False

    def start_alert_mode(self):
        if not self.alert_mode:
            self.alert_mode = True
            self.alert_overlay = Widget(size=(Window.width, Window.height))
            with self.alert_overlay.canvas:
                self.color = Color(1, 0, 0, 1)
                self.rect = Rectangle(pos=(0, 0), size=(Window.width, Window.height))
            Window.add_widget(self.alert_overlay)
            self._start_alert_animation()

    def _start_alert_animation(self):
        alert_anim = Animation(a=0, duration=0.5) + Animation(a=1, duration=0.5)
        alert_anim.repeat = True
        alert_anim.start(self.color)

    def stop_alert_mode(self):
        if self.alert_mode:
            self.alert_mode = False
            Window.remove_widget(self.alert_overlay)

    def update_proposal_graph(self, data):
        update_proposal_graph(self, data)

    def update_activity_graph(self, data):
        update_activity_graph(self, data)

    def update_progress(self, data):
        self.progress_bar.set_value(int(data["data"]["result"][0]["value"][1]) / 100)

    def build(self):
        # Initializing the progress bar
        self.init_progress_bar()

        # Initializing the layout columns
        self.init_columns()

        # Initializing the plots
        self.init_plots()

        # Creating a floating layout with label
        self.init_floating_layout()

        # Creating the root layout
        root = self.init_root_layout()

        # Starting the data fetching thread
        threading.Thread(target=data_fetcher, args=(self,), daemon=True).start()

        return root

    def init_progress_bar(self):
        self.top = BoxLayout(
            orientation="horizontal", size_hint=(1, BAR_HEIGHT_PERCENTAGE * 2 / 100)
        )
        self.progress_bar = CustomProgressBar()
        self.progress_bar.set_height(HEIGHT * (BAR_HEIGHT_PERCENTAGE / 100 * 2))
        self.progress_bar.draw()
        self.top.add_widget(self.progress_bar)

    def init_columns(self):
        self.columns = BoxLayout(orientation="horizontal")
        self.grid = BoxLayout(orientation="vertical")
        self.rightbox = BoxLayout(orientation="vertical", size_hint=(0.3, 1))
        self.values = ValuesWidget()

        self.columns.add_widget(self.grid)
        self.columns.add_widget(self.rightbox)
        self.rightbox.add_widget(self.values)

    def init_plots(self):
        plt.style.use("dark_background")
        self.fig1, self.ax1 = plt.subplots()
        self.ax1.set_facecolor("#252525")
        self.graph1 = FigureCanvasKivyAgg(figure=self.fig1, size_hint=(1, 0.5))

        self.fig2, self.ax2 = plt.subplots()
        self.ax2.set_facecolor("#252525")
        self.graph2 = FigureCanvasKivyAgg(figure=self.fig2, size_hint=(1, 0.5))

        self.grid.add_widget(self.graph1)
        self.grid.add_widget(self.graph2)

    def init_floating_layout(self):
        self.fl = FloatLayout(size=(Window.width, Window.height))
        floating_label = Label(
            text="Dashboard by krulknul.com",
            size_hint=(0.2, 0.1),
            pos_hint={"x": 0.702, "y": 0.918},
            color=(0, 0, 0, 1),
            font_family="IBM Plex Sans",
        )
        self.fl.add_widget(floating_label)

    def init_root_layout(self):
        root = FloatLayout()
        box_layout = BoxLayout(orientation="vertical")
        box_layout.add_widget(self.top)
        box_layout.add_widget(self.columns)
        root.add_widget(box_layout)
        root.add_widget(self.fl)

        return root


if __name__ == "__main__":
    MyApp().run()
