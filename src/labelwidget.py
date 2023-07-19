from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import StringProperty, ObjectProperty


class LabeledValue(BoxLayout):
    text = StringProperty()
    value = StringProperty()
    getter = ObjectProperty()

    def update(self, value):
        self.value = str(value)


class StatusLabeledValue(LabeledValue):
    def update(self, value):
        if value == True:
            self.ids.val.color = (0, 1, 0, 1)
            self.ids.val.text = "Online"
        else:
            self.ids.val.color = (1, 0, 0, 1)
            self.ids.val.text = "Offline"


class ValuesWidget(BoxLayout):
    def update(self):
        for child in self.children:
            data = child.getter()
            child.update(data)
