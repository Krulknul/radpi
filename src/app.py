import datetime
from functools import partial
import os
import threading
import time

os.environ["KIVY_NO_CONSOLELOG"] = "1"
from matplotlib import ticker
from matplotlib.dates import DateFormatter, HourLocator, MinuteLocator
import matplotlib.pyplot as plt
import kivy
from kivy.config import Config
from kivy.uix.screenmanager import NoTransition
from data_fetcher import get_epoch

HEIGHT = 320
WIDTH = 480
BAR_HEIGHT_PERCENTAGE = 3.2

# Kivy config setup. Must happen before importing other kivy modules.
Config.set("graphics", "width", f"{WIDTH}")
Config.set("graphics", "height", f"{HEIGHT}")
Config.set("graphics", "resizable", False)
from kivy.logger import Logger, LOG_LEVELS


from kivy.core.window import Window

if os.environ["ENVIRONMENT"] == "prod":
    Window.fullscreen = True
    Window.show_cursor = False
from kivy.clock import Clock

from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

from kivy.app import App

from graphs import ProposalGraph, ActivityGraph
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from custom_progress_bar import CustomProgressBar
from labelwidget import ValuesWidget
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
import txlist
from data_fetcher import get_transactions


kivy.require("2.2.1")


class StoppableThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class GeneralScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        plt.style.use("dark_background")

    def on_enter(self):
        self.thread = StoppableThread(target=self.updater, daemon=True)
        print("Starting thread")
        self.thread.start()

    def on_pre_leave(self, *args):
        print("Stopping thread")
        self.thread.stop()
        self.thread.join()

    def updater(self):
        while not self.thread.stopped():
            self.update()
            time.sleep(5)

    def update(self):
        try:
            for widget in self.ids.graphs.children:
                data = widget.getter()
                widget.update(data)
            data = self.ids.progress_bar.getter()
            self.ids.progress_bar.update(data)
            self.ids.valueswidget.update()
        except Exception as e:
            print("Error updating screen")
            print(e)


class MainScreen(GeneralScreen):
    def __init__(self, **kw):
        super().__init__(**kw)


class AltScreen(GeneralScreen):
    def __init__(self, **kw):
        super().__init__(**kw)

    def update(self):
        try:
            data = get_transactions()
            self.ids.graphs.children[1].update(data)
            data = self.ids.graph1.getter()
            self.ids.graph1.update(data)
            # data = self.ids.graph2.getter()
            # self.ids.graph2.update(data)
            data = self.ids.progress_bar.getter()
            self.ids.progress_bar.update(data)
            self.ids.valueswidget.update()
        except Exception as e:
            print(e)


class MyApp(App):
    def build(self):
        Clock.schedule_interval(self.toggle_screen, int(os.environ["SCREEN_TIMEOUT"]))
        transition = NoTransition()
        return ScreenManager()

    def toggle_screen(self, dt):
        if self.root.current == "main":
            # self.root.ids.alt.update()
            self.root.current = "alt"
        else:
            # self.root.ids.main.update()
            self.root.current = "main"


if __name__ == "__main__":
    MyApp().run()
