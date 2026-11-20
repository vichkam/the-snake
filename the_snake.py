import pygame
import random
import sys

# Константы размеров игрового поля и ячеек
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
CELL_SIZE = 20
BOARD_WIDTH = SCREEN_WIDTH // CELL_SIZE
BOARD_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

# Цвета
BACKGROUND_COLOR = (0, 0, 0)
SNAKE_COLOR = (0, 255, 0)
APPLE_COLOR = (255, 0, 0)

# Направления движения (векторы смещения)
UP = (0, -CELL_SIZE)
DOWN = (0, CELL_SIZE)
LEFT = (-CELL_SIZE, 0)
RIGHT = (CELL_SIZE, 0)


class GameObject:
    """
    Базовый класс для игровых объектов.
    Содержит общие атрибуты и методы для всех объектов на игровом поле.
    """

    def __init__(self, position=(0, 0), body_color=(0, 0, 0)):
        """
        Инициализирует базовые атрибуты объекта.

        :param position: Кортеж координат (x, y) верхнего левого угла объекта.
        :param body_color: Кортеж RGB значений цвета объекта.
        """
        self.position = position
        self.body_color = body_color

    def draw(self, surface):
        """
        Абстрактный метод для отрисовки объекта на игровом поле.
        Должен быть переопределён в дочерних классах.
        """
        pass


class Apple(GameObject):
    """
    Класс, описывающий яблоко на игровом поле.
    Наследуется от GameObject.
    """

    def __init__(self):
        """
        Инициализирует яблоко, задаёт ему красный цвет
        и случайную начальную позицию.
        """
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self):
        """
        Устанавливает случайную позицию яблока на игровом поле.
        Координаты кратны размеру ячейки, чтобы яблоко всегда
        находилось в пределах сетки.
        """
        self.position = (
            random.randint(0, BOARD_WIDTH - 1) * CELL_SIZE,
            random.randint(0, BOARD_HEIGHT - 1) * CELL_SIZE
        )

    def draw(self, surface):
        """
        Отрисовывает яблоко на игровой поверхности в виде квадрата.

        :param surface: Поверхность Pygame, на которой происходит отрисовка.
        """
        pygame.draw.rect(
            surface,
            self.body_color,
            (*self.position, CELL_SIZE, CELL_SIZE)
        )


class Snake(GameObject):
    """
    Класс, описывающий змейку, её поведение, движение и отрисовку.
    Наследуется от GameObject.
    """

    def __init__(self):
        """
        Инициализирует начальное состояние змейки.
        Задаёт зелёный цвет, длину 1, начальную позицию в центре экрана
        и направление движения вправо.
        """
        super().__init__(body_color=SNAKE_COLOR)
        self.reset()

    def update_direction(self):
        """
        Обновляет направление движения змейки на основе next_direction.
        Предотвращает разворот змейки на 180 градусов (в противоположную сторону).
        """
        if self.next_direction:
            # Проверяем, что новое направление не противоположно текущему
            if (self.next_direction[0] != -self.direction[0] or
                    self.next_direction[1] != -self.direction[1]):
                self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """
        Обновляет позицию змейки.
        Вычисляет координаты новой головы с учётом прохождения сквозь стены,
        добавляет её в начало списка positions и удаляет хвост,
        если длина змейки не увеличилась.
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        # Вычисляем новую позицию с учётом зацикливания поля
        new_x = (head_x + dx) % SCREEN_WIDTH
        new_y = (head_y + dy) % SCREEN_HEIGHT

        new_head = (new_x, new_y)

        # Вставляем новую голову в начало списка
        self.positions.insert(0, new_head)

        # Если длина списка превышает текущую длину змейки, удаляем хвост
        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self, surface):
        """
        Отрисовывает змейку на экране.
        Каждый сегмент змейки рисуется как квадрат размером в одну ячейку.

        :param surface: Поверхность Pygame, на которой происходит отрисовка.
        """
        for segment in self.positions:
            pygame.draw.rect(
                surface,
                self.body_color,
                (*segment, CELL_SIZE, CELL_SIZE)
            )

    def get_head_position(self):
        """
        Возвращает позицию головы змейки.

        :return: Кортеж координат (x, y) головы змейки.
        """
        return self.positions[0]

    def reset(self):
        """
        Сбрасывает змейку в начальное состояние.
        Используется при столкновении змейки с самой собой.
        """
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = None


def handle_keys(snake):
    """
    Обрабатывает нажатия клавиш для изменения направления движения змейки.
    Также обрабатывает событие закрытия окна игры.

    :param snake: Экземпляр класса Snake.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        snake.next_direction = UP
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        snake.next_direction = DOWN
    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
        snake.next_direction = LEFT
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        snake.next_direction = RIGHT


def main():
    """
    Основная функция игры.
    Инициализирует Pygame, создаёт игровое окно и запускает главный цикл.
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Змейка")
    clock = pygame.time.Clock()

    # Создание экземпляров игровых объектов
    snake = Snake()
    apple = Apple()

    # Основной игровой цикл
    while True:
        # 1. Обработка событий
        handle_keys(snake)

        # 2. Обновление состояния объектов
        snake.update_direction()
        snake.move()

        # Проверка: съела ли змейка яблоко
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()

        # Проверка: столкнулась ли змейка с самой собой
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()

        # 3. Отрисовка объектов
        # Затирание следа (очистка экрана перед новым кадром)
        screen.fill(BACKGROUND_COLOR)

        apple.draw(screen)
        snake.draw(screen)

        # 4. Обновление экрана
        pygame.display.update()

        # Ограничение частоты кадров для комфортной скорости игры
        clock.tick(20)


if __name__ == '__main__':
    main()
