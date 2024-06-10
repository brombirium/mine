import numpy as np
import time


def get_col(index):
    return f"\033[{90 + index}m"


class Colors:
    DARK_GRAY = get_col(0)
    RED = get_col(1)
    GREEN = get_col(2)
    YELLOW = get_col(3)
    BLUE = get_col(4)
    PURPLE = get_col(5)
    LIGHT_BLUE = get_col(6)
    WHITE = get_col(7)
    GRAY = get_col(8)
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_col(color, string, endline):
    if endline: print(color + string + Colors.ENDC)
    else: print(color + string + Colors.ENDC, end="")


class Field:
    EMPTY = 0
    BOMB = 1

    NO_FOG = 0
    FOGGY = 1
    FOG_MARKED = 2

    def __init__(self, n_row, n_col):
        self.n_row = n_row
        self.n_col = n_col
        self.cell = self.EMPTY * np.ones(shape=(self.n_row, self.n_col))
        self.fog = self.FOGGY * np.ones(shape=(self.n_row, self.n_col))
        self.win = False
        self.dead = False
        self.t_start = 0
        self.cursor_x = 0
        self.cursor_y = 0

    def fog_up(self):
        self.fog = self.FOGGY * np.ones(shape=(self.n_row, self.n_col))

    def defog(self):
        self.fog = self.NO_FOG * np.ones(shape=(self.n_row, self.n_col))

    def randomize(self, p: float):
        temp = np.random.randint(0, 100, (self.n_row, self.n_col))
        self.cell[temp > p * 100] = self.EMPTY
        self.cell[temp <= p * 100] = self.BOMB

    def count_nbors(self, i, j):
        count = 0
        for i_delta in range(-1, 2):
            for j_delta in range(-1, 2):
                if i_delta == 0 and j_delta == 0: continue
                i_ind = i + i_delta
                j_ind = j + j_delta
                if i_ind < 0 or j_ind < 0 or i_ind >= self.n_row or j_ind >= self.n_col: continue
                if self.cell[i_ind][j_ind] == self.BOMB: count += 1
        return count

    def uncover(self, i, j):
        if self.fog[i][j] == self.NO_FOG: return
        if self.fog[i][j] == self.FOG_MARKED: return
        self.fog[i][j] = self.NO_FOG
        if self.cell[i][j] == self.BOMB: return
        if self.count_nbors(i, j) > 0: return

        # also uncover surrounding cells
        for i_delta in range(-1, 2):
            for j_delta in range(-1, 2):
                if i_delta == 0 and j_delta == 0: continue
                i_ind = i + i_delta
                j_ind = j + j_delta
                if i_ind < 0 or j_ind < 0 or i_ind >= self.n_row or j_ind >= self.n_col: continue
                self.uncover(i_ind, j_ind)

    def mark(self, i, j):
        if self.fog[i][j] == self.NO_FOG: return
        if self.fog[i][j] == self.FOG_MARKED:
            self.fog[i][j] = self.FOGGY
        else:
            self.fog[i][j] = self.FOG_MARKED

    def bombs_total(self):
        count = 0
        for i in range(self.n_row):
            for j in range(self.n_col):
                if self.cell[i][j] == self.BOMB:
                    count += 1
        return count

    def bombs_unmarked(self):
        count = 0
        for i in range(self.n_row):
            for j in range(self.n_col):
                if self.cell[i][j] == self.BOMB and self.fog[i][j] != self.FOG_MARKED:
                    count += 1
        return count

    def print_board(self):
        dead = self.check_dead()
        win = self.check_win()

        bomb_color = Colors.GREEN if win else Colors.RED
        axis_color = Colors.DARK_GRAY if win else Colors.YELLOW
        fog_color = Colors.DARK_GRAY
        mark_color = Colors.RED
        nbor_color = Colors.GRAY if win else Colors.BLUE
        print(f"   ", end="")
        for j in range(self.n_col):
            print_col(axis_color, f" {chr(ord('1') + j)} ", False)
        print()
        for i in range(self.n_row):
            print_col(axis_color, f" {chr(ord('a') + i)} ", False)
            for j in range(self.n_col):
                if self.fog[i][j] == self.FOGGY:
                    print_col(fog_color, " # ", False)
                    continue
                if self.fog[i][j] == self.FOG_MARKED:
                    print_col(mark_color, " # ", False)
                    continue
                print(" ", end="")
                if self.cell[i][j] == self.EMPTY:
                    n_bor = self.count_nbors(i, j)
                    if n_bor == 0:
                        print(" ", end="")
                    else:
                        print_col(nbor_color, f"{n_bor}", False)
                elif self.cell[i][j] == self.BOMB:
                    print_col(bomb_color, "*", False)
                print(" ", end="")
            print_col(axis_color, f" {chr(ord('a') + i)} ", False)
            if i == 0:
                if win:
                    print_col(Colors.GREEN, "   Congratulations, you found all bombs!", False)
                elif dead:
                    print_col(Colors.RED, "   You exploded! Try again... :)", False)
                else:
                    print(f"   Bombs left: {self.bombs_unmarked()}/{self.bombs_total()}", end="")
            if i == 1:
                if win or dead:
                    print_col(Colors.GRAY, f"   Time: {self.get_time():.1f} s", False)

            print("")
        print(f"   ", end="")
        for j in range(self.n_col):
            print_col(axis_color, f" {chr(ord('1') + j)} ", False)
        print()

    def check_win(self):
        if self.win: return True
        self.win = True
        for i in range(self.n_row):
            for j in range(self.n_col):
                c = self.cell[i][j]
                f = self.fog[i][j]
                if c == self.BOMB:
                    if f == self.NO_FOG: self.win = False
                elif c == self.EMPTY:
                    if f == self.FOGGY: self.win = False
        return self.win

    def check_dead(self):
        if self.dead: return True
        self.dead = False
        for i in range(self.n_row):
            for j in range(self.n_col):
                c = self.cell[i][j]
                f = self.fog[i][j]
                if c == self.BOMB:
                    if f == self.NO_FOG: self.dead = True
        return self.dead

    def running(self):
        if self.dead: return False
        if self.win: return False
        return True

    def reset_state(self):
        self.dead = False
        self.win = False

    def tic(self):
        self.t_start = time.time()

    def get_time(self):
        return time.time() - self.t_start

    def cursor_reset(self):
        self.cursor_x = 0
        self.cursor_y = 0

    def cursor_move_left(self):
        if self.cursor_x > 0: self.cursor_x -= 1

    def cursor_move_right(self):
        if self.cursor_x < self.n_col - 1: self.cursor_x += 1

    def cursor_move_up(self):
        if self.cursor_y > 0: self.cursor_y -= 1

    def cursor_move_down(self):
        if self.cursor_y < self.n_row - 1: self.cursor_y += 1

    def cursor_uncover(self):
        print(f"uncover")

    def cursor_action(self, cmd):
        if cmd[0] == 'a':   self.cursor_move_left()
        elif cmd[0] == 'd': self.cursor_move_right()
        elif cmd[0] == 'w': self.cursor_move_up()
        elif cmd[0] == 's': self.cursor_move_down()
        elif cmd[0] == ' ': self.cursor_uncover()


def main():
    n_row = 16
    n_col = 16
    percentage = 0.2
    field = Field(n_row, n_col)
    field.randomize(percentage)
    field.fog_up()
    field.cursor_reset()

    while True:
        field.tic()
        while True:
            field.print_board()
            print("Next Move: ", end="")
            cmd = input()
            mark = False
            if cmd[0] == '!':
                mark = True
                cmd = cmd[1:3]
                print(f"mark mode -> cmd='{cmd}'")
            i_cmd = ord(cmd[0]) - ord('a')
            j_cmd = ord(cmd[1]) - ord('1')
            if mark:
                field.mark(i_cmd, j_cmd)
            else:
                field.uncover(i_cmd, j_cmd)

            field.check_dead()
            field.check_win()
            if not field.running():
                break

        if field.check_win(): field.defog()
        field.print_board()

        print_col(Colors.BLUE, "New Game? (y/n) ", False)
        while True:
            cmd = input()
            if cmd[0] == 'n':
                print_col(Colors.YELLOW, "Goodbye!", True)
                exit()
            elif cmd[0] == 'y':
                print_col(Colors.BLUE, "\n\nStarting New Game:", True)
                break
            else:
                print_col(Colors.RED, "Invalid response. New Game? (y/n) ", True)

        field.randomize(percentage)
        field.fog_up()
        field.reset_state()


if __name__ == '__main__':
    main()
