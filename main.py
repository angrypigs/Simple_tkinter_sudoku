import random
import tkinter as tk

class Sudoku:
    """
    Sudoku functions class
    """
    def __init__(self) -> None:
        self.random = __import__('random')

    def is_valid(self, board: list, number: int, r: int, c: int) -> bool:
        """
        Checks if given number isn't in row, column and 3x3 square
        """
        L1, L2, L3 = board[r], [board[i][c] for i in range(9)], [board[i][j] for i in range(r//3*3, r//3*3+3) for j in range(c//3*3, c//3*3+3)]
        return False if number in L1 or number in L2 or number in L3 else True

    def find_empty_cell(self, board: list):
        """
        Returns a row and column of an empty cell if it finds one
        """
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    return row, col
        return None

    def generate_template(self, board: list) -> None:
        empty = self.find_empty_cell(board)
        if not empty:
            return True
        row, col = empty
        nums = [i for i in range(1, 10)]
        self.random.shuffle(nums)
        for i in nums:
            if self.is_valid(board, i, row, col):
                board[row][col] = i
                if self.generate_template(board):
                    return True
                board[row][col] = 0
        return False

    def generate_sudoku(self, level: int = 0) -> list:
        """
        Generates a valid sudoku board
        """
        board = [[0 for i in range(9)] for j in range(9)]
        self.generate_template(board)
        places = [[i, j] for i in range(9) for j in range(9)]
        Difficulty_list = [25, 35, 45, 55]
        for i in range(Difficulty_list[level]):
            k = self.random.choice(places)
            board[k[0]][k[1]] = 0
            places.remove(k)
        return board
        


class App:
    """
    Main Sudoku App class
    """
    def __init__(self) -> None:
        self.themes_list = [["#363636", "#15C1B0", "#181B1B", "#000000", "#555555"]]
        self.width, self.height = 600, 800
        self.grid_size = 400
        border_width = 10
        self.master = tk.Tk()
        self.master.title("Sudoku")
        self.master.geometry(f"{self.width}x{self.height}")
        self.master.resizable(False, False)
        self.canvas = tk.Canvas(self.master, height=self.height, width=self.width, bd=0, highlightthickness=0, bg="#0F2435")
        self.canvas.place(x=0, y=0)
        # create the background
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill=self.themes_list[0][0], outline="")
        # create the borders
        self.canvas.create_rectangle(0, 0, border_width, self.height, fill=self.themes_list[0][1], outline="")
        self.canvas.create_rectangle(self.width-border_width, 0, self.width, self.height, fill=self.themes_list[0][1], outline="")
        self.canvas.create_rectangle(border_width, 0, self.width-border_width, border_width, fill=self.themes_list[0][1], outline="")
        self.canvas.create_rectangle(border_width, self.height-border_width, self.width-border_width, self.height, fill=self.themes_list[0][1], outline="")
        self.canvas.create_rectangle(100, 300, 100+self.grid_size, 300+self.grid_size, fill=self.themes_list[0][2], width=3)
        link = lambda x, y: (lambda p: self.block_clicked(x, y))
        block_size = 44
        x_delay, y_delay = 0, 0
        for i in range(9):
            for j in range(9):
                if i%3==0:
                    y_delay += 2
                if j%3==0:
                    x_delay += 2
                self.canvas.create_rectangle(100+j*block_size+x_delay, 300+i*block_size+y_delay, 100+j*block_size+block_size+x_delay, 300+i*block_size+block_size+y_delay, fill=self.themes_list[0][4], tags=(f"block{i}_{j}"))
                self.canvas.tag_bind(f"block{i}_{j}", "<Button-1>", link(i, j))


        self.master.mainloop()

    def block_clicked(self, x: int, y: int) -> None:
        print(x, y)


if __name__ == "__main__":
    app = App()




