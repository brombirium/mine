import numpy as np


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

    def print_board(self, win=False):
        bomb_color = Colors.GREEN if win else Colors.RED
        count_color = Colors.DARK_GRAY if win else Colors.YELLOW
        fog_color = Colors.DARK_GRAY
        mark_color = Colors.RED
        nbor_color = Colors.BLUE
        print(f"   ", end="")
        for j in range(self.n_col):
            print_col(count_color, f" {chr(ord('a') + j)} ", False)
        print()
        for i in range(self.n_row):
            print_col(count_color, f" {chr(ord('A') + i)} ", False)
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
            print_col(count_color, f" {chr(ord('A') + i)} ", False)
            print("")
        print(f"   ", end="")
        for j in range(self.n_col):
            print_col(count_color, f" {chr(ord('a') + j)} ", False)
        print()

    def check_win(self):
        win = True
        for i in range(self.n_row):
            for j in range(self.n_col):
                c = self.cell[i][j]
                f = self.fog[i][j]
                if c == self.BOMB:
                    if f == self.NO_FOG: win = False
                elif c == self.EMPTY:
                    if f == self.FOGGY: win = False
        return win

    def check_dead(self):
        for i in range(self.n_row):
            for j in range(self.n_col):
                c = self.cell[i][j]
                f = self.fog[i][j]
                if c == self.BOMB:
                    if f == self.NO_FOG: return True
        return False


def main():
    n_row = 10
    n_col = 12
    field = Field(n_row, n_col)
    field.randomize(0.15)
    field.fog_up()

    running = True
    win = False
    while running:
        field.print_board()
        print("Next Move: ", end="")
        cmd = input()
        mark = False
        if cmd[0] == '!':
            mark = True
            cmd = cmd[1:3]
            print(f"mark mode -> cmd='{cmd}'")
        i_cmd = ord(cmd[0]) - ord('A')
        j_cmd = ord(cmd[1]) - ord('a')
        if mark:
            field.mark(i_cmd, j_cmd)
        else:
            field.uncover(i_cmd, j_cmd)
        dead = field.check_dead()
        if dead:
            print_col(Colors.RED, "You exploded! Try again... :)", True)
            running = False
        win = field.check_win()
        if win:
            print_col(Colors.GREEN, "You have won! All non-bombs are uncovered. Congratulations!", True)
            running = False

    if win: field.defog()
    field.print_board(win)


if __name__ == '__main__':
    main()
