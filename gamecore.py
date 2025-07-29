import random

class GameCore:
    def __init__(self):
        self.board_size = 30           # Размер игрового поля 30x30
        self.respawn_time = 3          # Время респауна змеи после смерти (секунды)
        self.invincible_time = 3       # Время неуязвимости после респауна (секунды)
        self.target_length = 30        # Длина змеи, при достижении которой игрок выигрывает
        self.fruit = self.random_fruit()  # Позиция основного фрукта
        self.extra_fruits = []         # Фрукты, появившиеся после смерти змей

    def new_snake(self):
        # Начальная змейка из двух сегментов
        return [{"x": 5, "y": 5}, {"x": 4, "y": 5}]

    def random_fruit(self):
        # Случайная позиция фрукта на поле
        return {
            "x": random.randint(0, self.board_size - 1),
            "y": random.randint(0, self.board_size - 1)
        }

    def wrap_position(self, pos):
        # Обёртка координат, чтобы змейка вышла с другого края поля (тороидальная карта)
        return {
            "x": pos["x"] % self.board_size,
            "y": pos["y"] % self.board_size
        }

    def is_collision(self, head, body):
        # Проверка столкновения головы змеи с её телом или телом других змей
        return any(part["x"] == head["x"] and part["y"] == head["y"] for part in body)
