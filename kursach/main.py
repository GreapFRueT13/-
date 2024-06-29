import sys
import time
from typing import List, Tuple, Set
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel
from PySide6.QtGui import QPainter, QColor, QBrush
from PySide6.QtCore import Qt

# Функция которая задаёт ходы
def poser(row: int, col: int, board: List[List[str]]) -> List[List[str]]:
    king_camel_figure = [
        (row + 1, col + 1),
        (row - 1, col - 1),
        (row + 1, col - 1),
        (row - 1, col + 1),
        (row - 1, col),
        (row + 1, col),
        (row, col - 1),
        (row, col + 1),
        (row + 3, col + 1),
        (row + 3, col - 1),
        (row - 3, col + 1),
        (row - 3, col - 1),
        (row + 1, col + 3),
        (row + 1, col - 3),
        (row - 1, col + 3),
        (row - 1, col - 3)
    ]

    board[row][col] = '#'

    # Помечаем ячейки, на которые нельзя ставить фигуры
    for i in king_camel_figure:
        m, n = i[0], i[1]
        if 0 <= m < len(board) and 0 <= n < len(board):
            board[m][n] = '*'
    return board

# Функция которая создает доску
def create_board(N: int, solutions: List[Tuple[int, int]]) -> List[List[str]]:
    board: List[List[str]] = [["0"] * N for _ in range(N)]
    for row, col in solutions:
        poser(row, col, board)
    return board

# Функция возвращающая список ходов
def move(row: int, col: int) -> Set[Tuple[int, int]]:
    moves = {
        (row + 1, col + 1),
        (row - 1, col - 1),
        (row + 1, col - 1),
        (row - 1, col + 1),
        (row - 1, col),
        (row + 1, col),
        (row, col - 1),
        (row, col + 1),
        (row + 3, col + 1),
        (row + 3, col - 1),
        (row - 3, col + 1),
        (row - 3, col - 1),
        (row + 1, col + 3),
        (row + 1, col - 3),
        (row - 1, col + 3),
        (row - 1, col - 3),
    }
    return moves

# Функция для вывода решений и записи их в файл
def show_solutions(solutions: List[List[Tuple[int, int]]], startTime: float) -> None:
    print("Всего решений:", len(solutions))

    # Запись решений в файл
    with open("output.txt", "w") as output_file:
        if not solutions:
            output_file.write("no solutions")
        else:
            for solution in solutions:
                output_file.write(" ".join(f"({x},{y})" for x, y in solution) + "\n")

# Основная функция для решения задачи
def solve(L: int, N: int, solutions: List[Tuple[int, int]], allSolutions: List[List[Tuple[int, int]]], startTime: float):
    backtrack(L, N, 0, -1, solutions, allSolutions)
    show_solutions(allSolutions, startTime)

# Рекурсивная функция
def backtrack(
    L: int,
    N: int,
    row: int,
    col: int,
    solutions: List[Tuple[int, int]],
    allSolutions: List[List[Tuple[int, int]]],
) -> None:
    if L == 0:
        allSolutions.append(solutions.copy())
        if len(allSolutions) == 1:
            for i in create_board(N, solutions):
                print(i)
        return

    for r in range(row, N):
        start_col = col + 1 if r == row else 0
        for c in range(start_col, N):
            if (r, c) not in solutions and not move(r, c).intersection(solutions):
                solutions.append((r, c))
                backtrack(L - 1, N, r, c, solutions, allSolutions)
                solutions.pop()

# Инициализация данных
def init_data():
    startTime = time.time()

    solutions: List[Tuple[int, int]] = []
    allSolutions: List[List[Tuple[int, int]]] = []

    with open("input.txt", "r") as input_file:
        N, L, K = map(int, input_file.readline().split())

        board: List[List[str]] = [["0"] * N for _ in range(N)]

        for _ in range(K):
            row, col = map(int, input_file.readline().split())
            solutions.append((row, col))
            poser(row, col, board)

    return startTime, board, solutions, allSolutions, N, L, K

class ChessBoardWidget(QWidget):
    def __init__(self, N: int, solutions: List[List[Tuple[int, int]]], existing_positions: List[Tuple[int, int]], parent=None):
        super().__init__(parent)
        self.N = N
        self.solutions = solutions
        self.existing_positions = existing_positions
        self.setFixedSize(N * 50, N * 50)

    def paintEvent(self, event):
        painter = QPainter(self)
        cell_size = 50

        # Рисуем шахматную доску
        for row in range(self.N):
            for col in range(self.N):
                if (row + col) % 2 == 0:
                    painter.setBrush(QBrush(QColor(255, 255, 255)))
                else:
                    painter.setBrush(QBrush(QColor(0, 0, 0)))
                painter.drawRect(col * cell_size, row * cell_size, cell_size, cell_size)

        # Рисуем фигуры
        if self.solutions:
            solution_board = [[0] * self.N for _ in range(self.N)]
            for x, y in self.solutions[0]:
                solution_board[x][y] = 1
            for x, y in self.existing_positions:
                solution_board[x][y] = 2
            for row in range(self.N):
                for col in range(self.N):
                    if solution_board[row][col] == 1:
                        painter.setBrush(QBrush(QColor(0, 0, 255)))
                        painter.drawEllipse(col * cell_size, row * cell_size, cell_size, cell_size)
                    elif solution_board[row][col] == 2:
                        painter.setBrush(QBrush(QColor(0, 255, 0)))
                        painter.drawEllipse(col * cell_size, row * cell_size, cell_size, cell_size)

class MainWindow(QMainWindow):
    def __init__(self, N: int, solutions: List[List[Tuple[int, int]]], existing_positions: List[Tuple[int, int]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Princess Chess Solver")
        self.setFixedSize(N * 50, N * 50)
        self.board_widget = ChessBoardWidget(N, solutions, existing_positions)
        self.setCentralWidget(self.board_widget)

def main():
    # Чтение входных данных из файла
    startTime, board, solutions, allSolutions, N, L, K = init_data()

    print("Размер доски:", N, "Нужно разместить фигур:", L, "Фигур стоит:", K)
    if L == 0:
        if not (len(solutions) == 0):
            allSolutions.append(solutions)
        for row in board:
            row_of_board = " ".join(row)
            print(row_of_board)
        show_solutions(allSolutions, startTime)
        return

    solve(L, N, solutions, allSolutions, startTime)

    if allSolutions:
        print("Solutions found!")
    else:
        print("No solutions found")

    app = QApplication(sys.argv)
    main_window = MainWindow(N, allSolutions, solutions)
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
