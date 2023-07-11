from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label


class CustomProgressBar(Widget):
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
        self.bar_height = 10  # Set the default height of the progress bar here.

    def draw(self):
        with self.canvas:
            self.canvas.clear()
            Color(0.5, 0.5, 0.5)
            Rectangle(
                pos=(self.pos[0], self.pos[1] + (self.size[1] - self.bar_height) / 2),
                size=(self.size[0], self.bar_height),
            )  # Adjusted the position and size here.
            Color(1, 1, 1)
            Rectangle(
                pos=(self.pos[0], self.pos[1] + (self.size[1] - self.bar_height) / 2),
                size=(self.size[0] * (self.value / self.max), self.bar_height),
            )  # Adjusted the position and size here.

            self.percentage_label.text = f"Epoch progress: {self.value/self.max*100:.1f}%"  # Set the percentage text.
            self.percentage_label.pos = (
                self.pos[0] + 75,
                self.pos[1] + (self.size[1] - self.bar_height) / 2 + 5,
            )  # Position it on the left.
            self.canvas.add(
                self.percentage_label.canvas
            )  # Add the label to the canvas.

    def set_value(self, value):
        if 0 <= value <= self.max:
            self.value = value
            self.draw()

    def set_height(self, height):
        self.bar_height = height
        self.draw()
