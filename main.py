import random
import tkinter as tk
import os, sys
from tkinter import font
import time
from cryptography.fernet import Fernet

class Sudoku:
    """
    Sudoku functions class
    """
    def __init__(self) -> None:
        pass

    def is_valid(self, board: list, number: int, r: int, c: int) -> bool:
        """
        Checks if given number isn't in row, column and 3x3 square
        """
        L1, L2, L3 = [board[r][i] for i in range(9) if i != c], [board[i][c] for i in range(9) if i != r], [board[i][j] for i in range(r//3*3, r//3*3+3) for j in range(c//3*3, c//3*3+3) if i != r and j != c]
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
        random.shuffle(nums)
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
        board_before = [i[:] for i in board]
        places = [[i, j] for i in range(9) for j in range(9)]
        Difficulty_list = [25, 35, 45, 55]
        for i in range(Difficulty_list[level]):
            k = random.choice(places)
            board[k[0]][k[1]] = 0
            places.remove(k)
        return board, board_before

class App:
    """
    Main Sudoku App class
    """
    def __init__(self) -> None:
        # aditional data
        # themes list (0 - bg, 1 - borders, 2 - grid bg, 3 - cells bg, 
        # 4 - active cells bg, 5 - invalid cells bg, 6 - similar cells bg,
        # 7 - font color, 8 - edited cells font color)
        self.themes_list = [["#363636", "#15C1B0", "#181B1B", "#555555", "#0BFFE8", "#D14513", "#10BAAA", "#000000", "#043732"]]
        self.sudoku = Sudoku()
        # main variables (dimensions etc.)
        self.flag_menu = False
        self.current_theme = 0
        self.width, self.height = 600, 800
        self.grid_size = 400
        self.border_width = 10
        # list for current block
        self.current_coords = [-1, -1]
        # matrix for current cell colors
        self.cells_colors = [[3 for i in range(9)] for j in range(9)]
        # initializing the app
        self.master = tk.Tk()
        self.master.title("Sudoku")
        self.master.geometry(f"{self.width}x{self.height}")
        self.master.resizable(False, False)
        self.canvas = tk.Canvas(self.master, height=self.height, width=self.width, bd=0, highlightthickness=0, bg="#0F2435")
        self.canvas.place(x=0, y=0)
        # define three boards (current, initial one and correctly filled one)
        self.board = [[0 for i in range(9)] for j in range(9)]
        self.board_first = [[0 for i in range(9)] for j in range(9)]
        self.board_filled = [[0 for i in range(9)] for j in range(9)]
        # checks if file save.txt exists;
        # if no, create one
        if not os.path.isfile(os.path.join(sys.path[0], "save.txt")):
            file = open(os.path.join(sys.path[0], "save.txt"), "w")
            file.close()
        # checks if file save.txt contains game save; 
        # if yes, read game status from it, 
        # if no, sets menu_flag to true to open main menu later
        file = open(os.path.join(sys.path[0], "save.txt"), "r")
        L = [line.strip() for line in file.readlines()]
        file.close()
        if len(L) > 0:
            key2 = bytes(L[0], "UTF-8")
            fernet2 = Fernet(key2)
            save_current = fernet2.decrypt(bytes(L[1], "UTF-8")).decode()
            save_first = fernet2.decrypt(bytes(L[2], "UTF-8")).decode()
            save_filled = fernet2.decrypt(bytes(L[3], "UTF-8")).decode()
            for i in range(len(save_current)):
                self.board[i//9][i%9] = int(save_current[i])
                self.board_first[i//9][i%9] = int(save_first[i])
                self.board_filled[i//9][i%9] = int(save_filled[i])
        else:
            self.flag_menu = True
        
        # create the background
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill=self.themes_list[self.current_theme][0], outline="")
        # create the borders
        self.canvas.create_rectangle(0, 0, self.border_width, self.height, fill=self.themes_list[self.current_theme][1], outline="")
        self.canvas.create_rectangle(self.width-self.border_width, 0, self.width, self.height, fill=self.themes_list[self.current_theme][1], outline="")
        self.canvas.create_rectangle(self.border_width, 0, self.width-self.border_width, self.border_width, fill=self.themes_list[self.current_theme][1], outline="")
        self.canvas.create_rectangle(self.border_width, self.height-self.border_width, self.width-self.border_width, self.height, fill=self.themes_list[self.current_theme][1], outline="")
        # create the grid background and cells and binding them to function
        self.canvas.create_rectangle(100, 200, 100+self.grid_size, 200+self.grid_size, fill=self.themes_list[self.current_theme][2], width=3)
        link = lambda x, y: (lambda p: self.block_clicked(x, y))
        block_size = 44
        x_delay, y_delay = 0, 0
        for i in range(9):
            for j in range(9):
                if i>5:
                    y_delay = 4
                elif i>2:
                    y_delay = 2
                else:
                    y_delay = 0
                if j>5:
                    x_delay = 4
                elif j>2:
                    x_delay = 2
                else:
                    x_delay = 0
                font_color = 7 if self.board_first[i][j] != 0 else 8
                self.canvas.create_rectangle(100+j*block_size+x_delay, 200+i*block_size+y_delay, 
                                             100+j*block_size+block_size+x_delay, 200+i*block_size+block_size+y_delay, 
                                             fill=self.themes_list[self.current_theme][3], tags=(f"block{i}_{j}"))
                self.canvas.create_text(100+j*block_size+block_size//2+x_delay, 200+i*block_size+block_size//2+y_delay,
                                        anchor='center', justify='center', font=font.Font(family='Helvetica', size=24),
                                        state='disabled', fill=self.themes_list[self.current_theme][font_color], tags=f"block{i}_{j}text")
                self.canvas.tag_bind(f"block{i}_{j}", "<Button-1>", link(i, j))
        button_positions = [120, 240, 360, 480]
        button_pos_y = 670
        button_size = [80, 60]
        # create buttons
        self.canvas.create_rectangle(button_positions[0]-button_size[0]//2, button_pos_y-button_size[1]//2, 
                                     button_positions[0]+button_size[0]//2, button_pos_y+button_size[1]//2, 
                                     fill=self.themes_list[self.current_theme][1], width=3, tags=("undo_btn"))
        
        self.canvas.create_rectangle(button_positions[1]-button_size[0]//2, button_pos_y-button_size[1]//2, 
                                     button_positions[1]+button_size[0]//2, button_pos_y+button_size[1]//2, 
                                     fill=self.themes_list[self.current_theme][1], width=3, tags=("erase_btn"))
        
        self.canvas.create_rectangle(button_positions[2]-button_size[0]//2, button_pos_y-button_size[1]//2, 
                                     button_positions[2]+button_size[0]//2, button_pos_y+button_size[1]//2, 
                                     fill=self.themes_list[self.current_theme][1], width=3, tags=("hint_btn"))
        
        self.canvas.create_rectangle(button_positions[3]-button_size[0]//2, button_pos_y-button_size[1]//2, 
                                     button_positions[3]+button_size[0]//2, button_pos_y+button_size[1]//2, 
                                     fill=self.themes_list[self.current_theme][1], width=3, tags=("restart_btn"))
        # bind button rectangles to methods
        self.canvas.tag_bind("undo_btn", "<Button-1>", self.undo_move)
        self.canvas.tag_bind("erase_btn", "<Button-1>", self.erase)
        self.canvas.tag_bind("hint_btn", "<Button-1>", self.hint_move)
        self.canvas.tag_bind("restart_btn", "<Button-1>", self.restart)
        # update cells with board numbers
        self.update_board()
        # bind keyboard numbers with method
        link2 = lambda xp: (lambda p: self.number_pressed(xp))
        for i in range(1, 10):
            self.master.bind(str(i), link2(i))
        # init menu if save.txt doesn't contain game save
        if self.flag_menu:
            self.init_menu()
        self.master.mainloop()

    

    def undo_move(self, event) -> None:
        pass

    def hint_move(self, event) -> None:
        """
        Fills random one cell in current board with valid number from initial one
        """
        empty = [[i, j] for i in range(9) for j in range(9) if self.board[i][j] == 0]
        if len(empty) > 0:
            hinted_one = random.choice(empty)
            self.board[hinted_one[0]][hinted_one[1]] = self.board_filled[hinted_one[0]][hinted_one[1]]
            self.current_coords = hinted_one.copy()
            self.find_all_same(self.current_coords[0], self.current_coords[1])
            self.update_board()
            self.save_data()

    def restart(self, event) -> None:
        """
        Copying cells from initial board to current one
        """
        self.board = [i[:] for i in self.board_first]
        self.clear_board()
        self.current_coords = [-1, -1]
        self.update_board()
        self.save_data()
    
    def erase(self, event) -> None:
        """
        Erases given cell if it isn't filled in initial board
        """
        if self.board_first[self.current_coords[0]][self.current_coords[1]] == 0:
            self.board[self.current_coords[0]][self.current_coords[1]] = 0
            self.clear_board()
            self.cells_colors[self.current_coords[0]][self.current_coords[1]] = 4
            self.update_board()
            self.save_data()



    def block_clicked(self, x: int, y: int) -> None:
        """
        Command connected with all cells
        """
        self.current_coords[0], self.current_coords[1] = x, y
        self.find_all_same(x, y)

    def number_pressed(self, number: int) -> None:
        if self.current_coords!=[-1, -1] and self.board[self.current_coords[0]][self.current_coords[1]]==0:
            self.board[self.current_coords[0]][self.current_coords[1]] = number
            if self.sudoku.is_valid(self.board, number, self.current_coords[0], self.current_coords[1]):
                self.find_all_same(self.current_coords[0], self.current_coords[1])
            else:
                self.cells_colors[self.current_coords[0]][self.current_coords[1]] = 5
            self.canvas.itemconfig(f"block{self.current_coords[0]}_{self.current_coords[1]}text", fill=self.themes_list[self.current_theme][8])
            self.update_board()
            self.save_data()
    
    def find_all_same(self, x: int, y: int) -> None:
        """
        Colors given cell in color ,,4'' and all the cells with same value in color ,,6''
        """
        self.clear_board()
        if self.cells_colors[x][y] != 5:
            self.cells_colors[x][y] = 4
        if self.board[x][y]!=0:
            for i in range(9):
                for j in range(9):
                    if x!=i and y!=j and self.cells_colors[i][j] != 5 and self.board[i][j] == self.board[x][y]:
                        self.cells_colors[i][j] = 6
        self.update_board()

    def clear_board(self) -> None:
        """
        Sets all cells colors to normal except for invalid ones
        """
        for i in range(9):
            for j in range(9):
                if self.cells_colors[i][j] != 5:
                    self.cells_colors[i][j] = 3

    def update_board(self) -> None:
        """
        Updates numbers and colors of all cells if they are different
        """
        for i in range(9):
            for j in range(9):
                if self.canvas.itemcget(f"block{i}_{j}", 'fill') != self.themes_list[self.current_theme][self.cells_colors[i][j]]:
                    self.canvas.itemconfig(f"block{i}_{j}", fill=self.themes_list[self.current_theme][self.cells_colors[i][j]])
                n = "" if self.board[i][j] == 0 else str(self.board[i][j])
                self.canvas.itemconfig(f"block{i}_{j}text", text=n)

    def init_menu(self) -> None:
        # create the background
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill=self.themes_list[self.current_theme][0], outline="", tags=("start_panel"))
        # create the borders
        self.canvas.create_rectangle(0, 0, self.border_width, self.height, 
                                     fill=self.themes_list[self.current_theme][1], 
                                     outline="", tags=("start_panel"))
        self.canvas.create_rectangle(self.width-self.border_width, 0, self.width, self.height, 
                                     fill=self.themes_list[self.current_theme][1], 
                                     outline="", tags=("start_panel"))
        self.canvas.create_rectangle(self.border_width, 0, self.width-self.border_width, self.border_width, 
                                     fill=self.themes_list[self.current_theme][1], 
                                     outline="", tags=("start_panel"))
        self.canvas.create_rectangle(self.border_width, self.height-self.border_width, 
                                     self.width-self.border_width, self.height, 
                                     fill=self.themes_list[self.current_theme][1], 
                                     outline="", tags=("start_panel"))
        # create buttons
        self.canvas.create_rectangle(self.width//2-100, self.height//2-60, 
                                     self.width//2+100, self.height//2+60,
                                     fill=self.themes_list[self.current_theme][1],
                                     width=3, tags=("start_panel", "start_play_btn"))
        self.canvas.create_rectangle(self.width//2-60, self.height-80,
                                     self.width//2+60, self.height-40,
                                     fill=self.themes_list[self.current_theme][1],
                                     width=3, tags=("start_panel", "start_exit_btn"))
        self.canvas.create_text(self.width//2, self.height//2, text="Play", 
                                anchor='center', justify='center', 
                                font=font.Font(family='Helvetica', size=36),
                                state='disabled', tags=("start_panel"))
        self.canvas.create_text(self.width//2, self.height-60, text="Exit", 
                                anchor='center', justify='center', 
                                font=font.Font(family='Helvetica', size=24),
                                state='disabled', tags=("start_panel"))
        # bind buttons



    def save_data(self) -> None:
        """
        Saving encrypted game status to save.txt
        """
        key = Fernet.generate_key()
        file = open(os.path.join(sys.path[0], "save.txt"), "w")
        file.write(str(key, "UTF-8")+"\n")
        fernet = Fernet(key)
        save_current = ""
        for i in range(9):
            for j in range(9):
                save_current+=str(self.board[i][j])
        save_first = ""
        for i in range(9):
            for j in range(9):
                save_first+=str(self.board_first[i][j])
        save_filled = ""
        for i in range(9):
            for j in range(9):
                save_filled+=str(self.board_filled[i][j])
        file.write(str(fernet.encrypt(save_current.encode()), "UTF-8")+"\n")
        file.write(str(fernet.encrypt(save_first.encode()), "UTF-8")+"\n")
        file.write(str(fernet.encrypt(save_filled.encode()), "UTF-8")+"\n")
        file.close()
        

    def app_close(self) -> None:
        self.save_data()
        self.master.destroy()

        

if __name__ == "__main__":
    app = App()




