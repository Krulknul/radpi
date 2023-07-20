import asyncio
import datetime
from functools import partial
import os
import threading
import time
import traceback

# os.environ["KIVY_NO_CONSOLELOG"] = "1"
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
        self.clock = None

    def async_caller(self, dt=None):
        # Create an event loop if it doesn't exist
        loop = (
            asyncio.get_event_loop()
            if asyncio.get_event_loop().is_running()
            else asyncio.new_event_loop()
        )
        asyncio.set_event_loop(loop)

        # Schedule the execution of the async function
        loop.create_task(self.update())

    def on_enter(self):
        if not self.clock:
            self.clock = Clock.schedule_interval(self.async_caller, 5)

    def on_pre_leave(self, *args):
        pass
        # self.clock.cancel()

    # async def updater(self):
    #     while not self.thread.stopped():
    #         await self.update()
    #         time.sleep(5)

    async def update(self):
        try:
            for widget in self.ids.graphs.children:
                data = await widget.getter()
                await widget.update(data)
            data = await self.ids.progress_bar.getter()
            await self.ids.progress_bar.update(data)
            await self.ids.valueswidget.update()
        except Exception as e:
            traceback.print_exc()


class MainScreen(GeneralScreen):
    def __init__(self, **kw):
        super().__init__(**kw)


class AltScreen(GeneralScreen):
    def __init__(self, **kw):
        super().__init__(**kw)

    async def update(self):
        try:
            data = await get_transactions()
            await self.ids.graphs.children[1].update(data)
            data = await self.ids.graph1.getter()
            await self.ids.graph1.update(data)
            # data = self.ids.graph2.getter()
            # self.ids.graph2.update(data)
            data = await self.ids.progress_bar.getter()
            await self.ids.progress_bar.update(data)
            await self.ids.valueswidget.update()
        except Exception as e:
            traceback.print_exc()


class MyApp(App):
    def build(self):
        Clock.schedule_interval(self.toggle_screen, int(os.environ["SCREEN_TIMEOUT"]))
        transition = NoTransition()
        return ScreenManager(transition=transition)

    def toggle_screen(self, dt):
        if self.root.current == "main":
            # self.root.ids.alt.update()
            self.root.current = "alt"
        else:
            # self.root.ids.main.update()
            self.root.current = "main"


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MyApp().async_run())

    loop.close()
