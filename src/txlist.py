from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.recycleview import RecycleView
from data_fetcher import get_transactions
from util import format_large_number


class ListItem(BoxLayout):
    text = StringProperty()


class TxList(RecycleView):
    getter = get_transactions

    def __init__(self, **kwargs):
        super(TxList, self).__init__(**kwargs)
        self.data = [{"text": str(x), "value": str(x * 2)} for x in range(100)]

    def update(self, data):
        print("hallooooo")
        print(data)
        self.data = [
            {
                "text": str("..." + x["address"][-8:]),
                "type": "STAKE" if x["type"] == "PREPARED_STAKE" else "UNSTAKE",
                "value": format_large_number(int(x["amount"])) + " XRD",
            }
            for x in data
        ]
        print(self.data)
