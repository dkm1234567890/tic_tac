import pygame
import enum
import sys

class Mark(enum.Enum):
    X = "X"
    O = "O"

class Grid:
    def __init__(self):
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.x_count = 0
        self.o_count = 0

    def is_valid_move(self, row, col):
        return self.board[row][col] == " "

    def make_move(self, row, col, mark):
        if not self.is_valid_move(row, col):
            raise ValueError("Invalid move")
        self.board[row][col] = mark.value
        if mark == Mark.X:
            self.x_count += 1
        else:
            self.o_count += 1

    def undo_move(self, row, col):
        if self.board[row][col] != " ":
            if self.board[row][col] == Mark.X.value:
                self.x_count -= 1
            else:
                self.o_count -= 1
            self.board[row][col] = " "

    def is_terminal_state(self):
        for row in range(3):
            if self.board[row][0] == self.board[row][1] == self.board[row][2] != " ":
                return True
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != " ":
                return True
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            return True

        return all(cell != " " for row in self.board for cell in row)

    def evaluate(self):
        for mark in (Mark.X, Mark.O):
            mark_value = mark.value
            for row in range(3):
                if self.board[row][0] == self.board[row][1] == self.board[row][2] == mark_value:
                    return 1 if mark == Mark.X else -1
            for col in range(3):
                if self.board[0][col] == self.board[1][col] == self.board[2][col] == mark_value:
                    return 1 if mark == Mark.X else -1
            if self.board[0][0] == self.board[1][1] == self.board[2][2] == mark_value:
                return 1 if mark == Mark.X else -1
            if self.board[0][2] == self.board[1][1] == self.board[2][0] == mark_value:
                return 1 if mark == Mark.X else -1
        return 0

def minimax(grid, depth, is_maximizing_player):
    if grid.is_terminal_state():
        return grid.evaluate()
    if is_maximizing_player:
        best_val = -float("inf")
        for row in range(3):
            for col in range(3):
                if grid.is_valid_move(row, col):
                    grid.make_move(row, col, Mark.X)
                    val = minimax(grid, depth + 1, False)
                    grid.undo_move(row, col)
                    best_val = max(best_val, val)
        return best_val
    else:
        best_val = float("inf")
        for row in range(3):
            for col in range(3):
                if grid.is_valid_move(row, col):
                    grid.make_move(row, col, Mark.O)
                    val = minimax(grid, depth + 1, True)
                    grid.undo_move(row, col)
                    best_val = min(best_val, val)
        return best_val

def find_best_move(grid):
    best_move = None
    best_val = -float("inf")
    for row in range(3):
        for col in range(3):
            if grid.is_valid_move(row, col):
                grid.make_move(row, col, Mark.X)
                val = minimax(grid, 0, False)
                grid.undo_move(row, col)
                if val > best_val:
                    best_val = val
                    best_move = (row, col)
    return best_move

class TicTacToeUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((300, 300))
        pygame.display.set_caption("Tic Tac Toe")
        self.grid = Grid()
        self.font = pygame.font.Font(None, 74)
        self.bg_color = (255, 255, 255)
        self.line_color = (0, 0, 0)
        self.x_color = (200, 0, 0)
        self.o_color = (0, 0, 200)
        self.screen.fill(self.bg_color)
        self.draw_grid()

    def draw_grid(self):
        for x in range(1, 3):
            pygame.draw.line(self.screen, self.line_color, (0, 100 * x), (300, 100 * x), 2)
            pygame.draw.line(self.screen, self.line_color, (100 * x, 0), (100 * x, 300), 2)
        pygame.display.flip()

    def draw_move(self, row, col, mark):
        pos_x = col * 100 + 50
        pos_y = row * 100 + 50
        if mark == Mark.X:
            pygame.draw.line(self.screen, self.x_color, (pos_x - 25, pos_y - 25), (pos_x + 25, pos_y + 25), 2)
            pygame.draw.line(self.screen, self.x_color, (pos_x + 25, pos_y - 25), (pos_x - 25, pos_y + 25), 2)
        else:
            pygame.draw.circle(self.screen, self.o_color, (pos_x, pos_y), 25, 2)
        pygame.display.flip()

    def main(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    col = mouse_x // 100
                    row = mouse_y // 100
                    if self.grid.is_valid_move(row, col):
                        self.grid.make_move(row, col, Mark.O)
                        self.draw_move(row, col, Mark.O)
                        if self.grid.is_terminal_state():
                            self.end_game("Human wins!")
                            running = False
                            break
                        best_move = find_best_move(self.grid)
                        if best_move:
                            self.grid.make_move(best_move[0], best_move[1], Mark.X)
                            self.draw_move(best_move[0], best_move[1], Mark.X)
                        if self.grid.is_terminal_state():
                            if self.grid.evaluate() == 1:
                                self.end_game("AI wins!")
                            elif self.grid.evaluate() == -1:
                                self.end_game("Human wins!")
                            else:
                                self.end_game("Draw!")
                            running = False
                            break
            pygame.display.flip()

    def end_game(self, message):
        print(message)
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TicTacToeUI()
    game.main()
