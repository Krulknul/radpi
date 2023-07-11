from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout


class LabeledValue(BoxLayout):
    def __init__(self, label_text, value=0, **kwargs):
        super(LabeledValue, self).__init__(**kwargs)
        self.orientation = "vertical"

        self.label_layout = AnchorLayout(anchor_x="center", anchor_y="top")
        self.label = Label(halign="center", valign="middle")
        self.label_layout.add_widget(self.label)

        self.value_layout = AnchorLayout(anchor_x="center", anchor_y="top")
        self.value = Label(
            halign="center",
            valign="middle",
            font_size=20,
        )
        self.value_layout.add_widget(self.value)

        # Set text_size to the size of the label itself
        self.label.bind(size=self.label.setter("text_size"))
        self.value.bind(size=self.value.setter("text_size"))

        self.label.text = label_text
        self.value.text = str(value)

        self.add_widget(self.label_layout)
        self.add_widget(self.value_layout)

    def set_value(self, value):
        self.value.text = str(value)


class ValuesWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(ValuesWidget, self).__init__(**kwargs)
        self.orientation = "vertical"

        self.main = LabeledValue("Main node")
        self.backup = LabeledValue("Backup node")
        self.epoch = LabeledValue("Current epoch")
        self.stake = LabeledValue("Stake amount")
        self.rank = LabeledValue("Ranking")
        self.uptime = LabeledValue("Recent uptime")
        self.spacing = 13
        self.padding = [0, 10, 0, 10]
        self.add_widget(self.main)
        self.add_widget(self.backup)
        self.add_widget(self.epoch)
        self.add_widget(self.stake)
        self.add_widget(self.rank)
        self.add_widget(self.uptime)

    def set_main(self, value):
        if value:
            self.main.set_value("Online")
            self.main.value.color = (0, 1, 0, 1)
        else:
            self.main.set_value("Offline")
            self.main.value.color = (1, 0, 0, 1)

    def set_backup(self, value):
        if value:
            self.backup.set_value("Online")
            self.backup.value.color = (0, 1, 0, 1)
        else:
            self.backup.set_value("Offline")
            self.backup.value.color = (1, 0, 0, 1)

    def set_epoch(self, value):
        self.epoch.set_value(f"{int(value):,}")

    def set_stake(self, value):
        self.stake.set_value(f"{value:,}")

    def set_rank(self, value):
        self.rank.set_value(f"{value}")

    def set_uptime(self, value):
        self.uptime.set_value(f"{value:.2f}%")
