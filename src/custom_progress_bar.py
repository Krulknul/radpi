from kivy.clock import mainthread
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from data_fetcher import get_epoch_progress


class CustomProgressBar(Widget):
    height = 10

    def __init__(self, **kwargs):
        super(CustomProgressBar, self).__init__(**kwargs)
        self.max = 100
        self.value = 0
        self.title_label = Label(
            size=(10, 10), pos=(100, 100), font_family="IBM Plex Sans"
        )
        self.percentage_label = Label(
            size=(10, 10), color=(0, 0, 0, 1)
        )  # Create the label with black text.
        self.getter = get_epoch_progress

    async def update(self, value):
        self.value = value
        with self.canvas:
            self.canvas.clear()
            Color(0.5, 0.5, 0.5)
            Rectangle(
                pos=(self.pos[0], self.pos[1] + (self.size[1] - self.height) / 2),
                size=(self.size[0], 100),
            )  # Adjusted the position and size here.
            Color(1, 1, 1)
            Rectangle(
                pos=(self.pos[0], self.pos[1] + (self.size[1] - self.height) / 2),
                size=(self.size[0] * (self.value / self.max), 10000),
            )  # Adjusted the position and size here.

            self.percentage_label.text = f"Epoch progress: {self.value/self.max*100:.1f}%"  # Set the percentage text.
            self.percentage_label.pos = (
                self.pos[0] + 75,
                self.pos[1] + (self.size[1] - self.height) / 2 + 5,
            )  # Position it on the left.
            self.canvas.add(
                self.percentage_label.canvas
            )  # Add the label to the canvas.
