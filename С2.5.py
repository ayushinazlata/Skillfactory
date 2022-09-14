from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return 'Вы стреляете за пределы доски!'


class BoardReShotException(BoardException):
    def __str__(self):
        return 'Вы уже стреляли в эту клетку!'


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Ship:
    def __init__(self, length, dot_bow, route):
        self.length = length
        self.dot_bow = dot_bow
        self.route = route
        self.num_lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            ship_x = self.dot_bow.x
            ship_y = self.dot_bow.y

            if self.route == 0:
                ship_x += i
            elif self.route == 1:
                ship_y += i

            ship_dots.append(Dot(ship_x, ship_y))

        return ship_dots

    def win_shoot(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.died_ship = 0

        self.field = [['O'] * size for _ in range(size)]

        self.state_cell = []
        self.live_ships = []

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.state_cell:
                raise BoardWrongShipException()
        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"
            self.state_cell.append(dot)

        self.live_ships.append(ship)
        self.countour(ship)

    def countour(self, ship, flag=False):
        around = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 0), (0, 1),
                  (1, -1), (1, 0), (1, 1)]

        for dot in ship.dots:
            for dotx, doty in around:
                ship = Dot(dot.x + dotx, dot.y + doty)
                if not(self.out(ship)) and ship not in self.state_cell:
                    if flag:
                        self.field[ship.x][ship.y] = '.'
                    self.state_cell.append(ship)

    def __str__(self):
        result = ''
        result += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i, row in enumerate(self.field):
            result += f"\n{i+1} | " + " | ".join(row) + " |"

        if self.hid:
            result = result.replace("■", "O")
        return result

    def out(self, dot):
        return not((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()

        if dot in self.state_cell:
            raise BoardReShotException()

        self.state_cell.append(dot)

        for ship in self.live_ships:
            if ship.win_shoot(dot):
                ship.num_lives -= 1
                self.field[dot.x][dot.y] = 'X'
                if ship.num_lives == 0:
                    self.died_ship += 1
                    self.countour(ship, flag=True)
                    print('Корабль уничтожен!')
                    return False
                else:
                    print('Корабль ранен...')
                    return True

        self.field[dot.x][dot.y] = '.'
        print('Мимо! Стреляем дальше!')
        return False

    def start(self):
        self.state_cell = []


class Player:
    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError

    def move(self):
        while True:
            try:
                aim = self.ask()
                enemy_aim = self.enemy_board.shot(aim)
                return enemy_aim
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        dot = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход компьютера: {dot.x + 1} {dot.y + 1}')
        return dot


class User(Player):
    def ask(self):
        while True:
            cord = input('Ваш ход:  ').split()

            if len(cord) != 2:
                print('Введите 2 координаты!')
                continue

            x, y = cord

            if not (x.isdigit()) or not (y.isdigit()):
                print('Введите числа!')
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        human = self.random_board()
        comp = self.random_board()
        comp.hid = True

        self.ai = AI(comp, human)
        self.us = User(human, comp)

    def gen_board(self):
        len_ships = [1, 1, 1, 1, 2, 2, 3]
        board = Board(size=self.size)
        tries = 0
        for len_ in len_ships:
            while True:
                tries += 1
                if tries > 1000:
                    return None
                ship = Ship(len_, Dot(randint(0, self.size), randint(0, self.size)), randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.start()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.gen_board()
        return board

    @staticmethod
    def salute():
        print('------------------')
        print(' Добро пожаловать ')
        print('      в игру      ')
        print('   "Морской бой"  ')
        print('------------------')
        print('  Правила ввода:  ')
        print('       x y        ')
        print('x - номер строки')
        print('y - номер столбца')
        print('------------------')
        print('   Начнём игру!   ')

    def print_board(self):
        print('-' * 20)
        print('Доска пользователя:')
        print(self.us.board)
        print('-' * 20)
        print('Доска компьютера:')
        print(self.ai.board)
        print('-' * 20)

    def loop(self):
        num = 0
        while True:
            self.print_board()
            if num % 2 == 0:
                print('Ходит пользователь!')
                repeat = self.us.move()
            else:
                print('Ходит компьютер!')
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.died_ship == 7:
                self.print_board()
                print('-' * 20)
                print('Выиграл пользователь!')
                break

            if self.us.board.died_ship == 7:
                self.print_board()
                print('-' * 20)
                print('Выиграл компьютер!')
                break
            num += 1

    def start(self):
        self.salute()
        self.loop()

g = Game()
g.start()
