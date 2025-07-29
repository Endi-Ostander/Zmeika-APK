import asyncio
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
import websockets
import json

CELL_SIZE = 20
BOARD_SIZE = 30
WIDTH = CELL_SIZE * BOARD_SIZE
HEIGHT = CELL_SIZE * BOARD_SIZE

class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snakes = []
        self.fruit = None
        self.extra_fruits = []
        self.connected = False
        self.invincibles = []
        self.canvas.clear()
        Clock.schedule_interval(self.update_canvas, 1/30)

    def update_game_state(self, data):
        self.snakes = data["players"]
        self.fruit = data["fruit"]
        self.extra_fruits = data.get("extra_fruits", [])
        self.invincibles = [p["invincible"] for p in data["players"]]

    def update_canvas(self, dt):
        self.canvas.clear()
        with self.canvas:
            for i, p in enumerate(self.snakes):
                if not p["alive"]:
                    continue
                Color(0, 1, 0) if i == 0 else Color(1, 0, 0)
                for part in p["snake"]:
                    Rectangle(pos=(part["x"] * CELL_SIZE, part["y"] * CELL_SIZE), size=(CELL_SIZE, CELL_SIZE))
            if self.fruit:
                Color(1, 1, 0)
                Rectangle(pos=(self.fruit["x"] * CELL_SIZE, self.fruit["y"] * CELL_SIZE), size=(CELL_SIZE, CELL_SIZE))
            Color(1, 0.5, 0)
            for ef in self.extra_fruits:
                Rectangle(pos=(ef["x"] * CELL_SIZE, ef["y"] * CELL_SIZE), size=(CELL_SIZE, CELL_SIZE))

class ZmeikaApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical')
        self.game = GameWidget(size=(WIDTH, HEIGHT))
        root.add_widget(self.game)
        controls = BoxLayout(size_hint_y=None, height=100)
        for (x, y, label) in [(0, -1, '▲'), (-1, 0, '◀'), (1, 0, '▶'), (0, 1, '▼')]:
            btn = Button(text=label, font_size=32)
            btn.bind(on_press=lambda _, dx=x, dy=y: self.send_dir(dx, dy))
            controls.add_widget(btn)
        root.add_widget(controls)
        Clock.schedule_once(lambda dt: self.start_client(), 1)
        return root

    async def ws_loop(self):
        uri = "ws://localhost:8765"
        try:
            async with websockets.connect(uri) as websocket:
                self.websocket = websocket
                while True:
                    data = await websocket.recv()
                    parsed = json.loads(data)
                    if parsed["type"] == "update":
                        self.game.update_game_state(parsed)
        except Exception as e:
            print("❌ WebSocket error:", e)

    def send_dir(self, x, y):
        if hasattr(self, 'websocket'):
            asyncio.run(self.websocket.send(json.dumps({"type": "dir", "dir": {"x": x, "y": y}})))

    def start_client(self):
        asyncio.ensure_future(self.ws_loop())

if __name__ == '__main__':
    from server import run_server
    asyncio.ensure_future(run_server())
    ZmeikaApp().run()
