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
        self.THEMES_LIST = [["#363636", "#15C1B0", "#181B1B", "#555555", "#0BFFE8", "#D14513", "#10BAAA", "#000000", "#043732"]]
        self.sudoku = Sudoku()
        # define constants
        self.WIDTH, self.HEIGHT = 600, 800
        self.GRID_SIZE = 400
        self.BORDER_WIDTH = 10
        # define variables (dimensions etc.)
        self.flag_notes = True
        self.flag_pause = False
        self.flag_menu = True
        self.current_theme = 0
        # list for current block
        self.coords = [-1, -1]
        # matrix for current cell colors
        self.cells_colors = [[3 for i in range(9)] for j in range(9)]
        # matrix for notes
        self.notes_board = [[[] for i in range(9)] for j in range(9)]
        # initializing the app
        self.master = tk.Tk()
        self.master.title("Sudoku")
        self.master.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.master.resizable(False, False)
        self.master.protocol("WM_DELETE_WINDOW", self.app_close)
        self.canvas = tk.Canvas(self.master, height=self.HEIGHT, width=self.WIDTH, bd=0, highlightthickness=0, bg="#0F2435")
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
            save_notes = fernet2.decrypt(bytes(L[4], "UTF-8")).decode()
            for i in range(len(save_current)):
                self.board[i//9][i%9] = int(save_current[i])
                self.board_first[i//9][i%9] = int(save_first[i])
                self.board_filled[i//9][i%9] = int(save_filled[i])
            self.notes_board = [[[[int(j) for j in i] for i in save_notes.split("-")][k*9+m] for m in range(9)] for k in range(9)]
        # create the background
        self.canvas.create_rectangle(0, 0, self.WIDTH, self.HEIGHT, fill=self.THEMES_LIST[self.current_theme][0], outline="")
        # create the borders
        self.canvas.create_rectangle(0, 0, self.BORDER_WIDTH, self.HEIGHT, fill=self.THEMES_LIST[self.current_theme][1], outline="")
        self.canvas.create_rectangle(self.WIDTH-self.BORDER_WIDTH, 0, self.WIDTH, self.HEIGHT, fill=self.THEMES_LIST[self.current_theme][1], outline="")
        self.canvas.create_rectangle(self.BORDER_WIDTH, 0, self.WIDTH-self.BORDER_WIDTH, self.BORDER_WIDTH, fill=self.THEMES_LIST[self.current_theme][1], outline="")
        self.canvas.create_rectangle(self.BORDER_WIDTH, self.HEIGHT-self.BORDER_WIDTH, self.WIDTH-self.BORDER_WIDTH, self.HEIGHT, fill=self.THEMES_LIST[self.current_theme][1], outline="")
        # create the grid background and cells and binding them to function
        self.canvas.create_rectangle(100, 200, 100+self.GRID_SIZE, 200+self.GRID_SIZE, fill=self.THEMES_LIST[self.current_theme][2], width=3)
        link = lambda x, y: (lambda p: self.block_clicked(x, y))
        self.block_size = 44
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
                self.canvas.create_rectangle(100+j*self.block_size+x_delay, 200+i*self.block_size+y_delay, 
                                             100+j*self.block_size+self.block_size+x_delay, 200+i*self.block_size+self.block_size+y_delay, 
                                             fill=self.THEMES_LIST[self.current_theme][3], tags=(f"block{i}_{j}"))
                self.canvas.create_text(100+j*self.block_size+self.block_size//2+x_delay, 200+i*self.block_size+self.block_size//2+y_delay,
                                        anchor='center', justify='center', font=font.Font(family='Helvetica', size=24),
                                        state='disabled', fill=self.THEMES_LIST[self.current_theme][font_color], tags=f"block{i}_{j}text")
                self.canvas.tag_bind(f"block{i}_{j}", "<Button-1>", link(i, j))
        button_pos_y = 660
        button_size = [80, 60]
        button_tags = ["notes_btn", "erase_btn", "hint_btn", "restart_btn"]
        buttons_unicodes = ["\u270E", "\u2716", "\U0001F4A1", "\u2B6F"]
        # create buttons
        for i in range(len(button_tags)):
            self.canvas.create_rectangle(self.WIDTH//(len(button_tags)+1)*(i+1)-button_size[0]//2, button_pos_y-button_size[1]//2, 
                                     self.WIDTH//(len(button_tags)+1)*(i+1)+button_size[0]//2, button_pos_y+button_size[1]//2, 
                                     fill=self.THEMES_LIST[self.current_theme][1], width=3, tags=(button_tags[i]))
            self.canvas.create_text(self.WIDTH//(len(button_tags)+1)*(i+1), button_pos_y, 
                                    anchor='center', justify='center', state='disabled',
                                    font=font.Font(family='Helvetica', size=24),
                                    text=buttons_unicodes[i])
        
        # bind button rectangles to methods
        def denied() -> None:
            self.canvas.delete("accept")
            self.flag_pause = False
        def accept(f: callable) -> None:
            denied()
            f()
        def restart_accept() -> None:
            if not self.flag_pause:
                self.flag_pause = True
                self.canvas.create_rectangle(self.WIDTH//2-200, self.HEIGHT//2-100,
                                            self.WIDTH//2+200, self.HEIGHT//2+100,
                                            fill=self.THEMES_LIST[self.current_theme][0], width=3, 
                                            tags=("accept"))
                self.canvas.create_text(self.WIDTH//2, self.HEIGHT//2-60,
                                        anchor='center', justify='center', state='disabled',
                                        font=font.Font(family='Helvetica', size=32),
                                        text="Restart game?", tags=("accept"))
                self.canvas.create_rectangle(self.WIDTH//2-100, self.HEIGHT//2,
                                            self.WIDTH//2-20, self.HEIGHT//2+60,
                                            fill=self.THEMES_LIST[self.current_theme][1], width=3, 
                                            tags=("accept", "accept_yes_restart"))
                self.canvas.create_rectangle(self.WIDTH//2+20, self.HEIGHT//2,
                                            self.WIDTH//2+100, self.HEIGHT//2+60,
                                            fill=self.THEMES_LIST[self.current_theme][1], width=3, 
                                            tags=("accept", "accept_no_restart"))
                self.canvas.create_text(self.WIDTH//2-60, self.HEIGHT//2+30,
                                        anchor='center', justify='center', state='disabled',
                                        font=font.Font(family='Helvetica', size=24),
                                        text="Yes", tags=("accept"))
                self.canvas.create_text(self.WIDTH//2+60, self.HEIGHT//2+30,
                                        anchor='center', justify='center', state='disabled',
                                        font=font.Font(family='Helvetica', size=24),
                                        text="No", tags=("accept"))
                self.canvas.tag_bind("accept_yes_restart", "<Button-1>", lambda event: accept(self.restart))
                self.canvas.tag_bind("accept_no_restart", "<Button-1>", lambda event: denied())
            
        self.canvas.tag_bind("notes_btn", "<Button-1>", lambda event: self.notes())
        self.canvas.tag_bind("erase_btn", "<Button-1>", lambda event: self.erase())
        self.canvas.tag_bind("hint_btn", "<Button-1>", lambda event: self.hint_move())
        self.canvas.tag_bind("restart_btn", "<Button-1>", lambda event: restart_accept())
        # create exit button
        def back_to_menu() -> None:
            self.canvas.delete("accept")
            self.flag_menu = True
            self.flag_pause = False
            self.save_data()
            self.move_menu(20)
        def exit_accept() -> None:
            if not self.flag_pause:
                self.flag_pause = True
                self.canvas.create_rectangle(self.WIDTH//2-200, self.HEIGHT//2-100,
                                            self.WIDTH//2+200, self.HEIGHT//2+100,
                                            fill=self.THEMES_LIST[self.current_theme][0], width=3, 
                                            tags=("accept"))
                self.canvas.create_text(self.WIDTH//2, self.HEIGHT//2-60,
                                        anchor='center', justify='center', state='disabled',
                                        font=font.Font(family='Helvetica', size=32),
                                        text="Go to menu?", tags=("accept"))
                self.canvas.create_rectangle(self.WIDTH//2-100, self.HEIGHT//2,
                                            self.WIDTH//2-20, self.HEIGHT//2+60,
                                            fill=self.THEMES_LIST[self.current_theme][1], width=3, 
                                            tags=("accept", "accept_yes_exit"))
                self.canvas.create_rectangle(self.WIDTH//2+20, self.HEIGHT//2,
                                            self.WIDTH//2+100, self.HEIGHT//2+60,
                                            fill=self.THEMES_LIST[self.current_theme][1], width=3, 
                                            tags=("accept", "accept_no_exit"))
                self.canvas.create_text(self.WIDTH//2-60, self.HEIGHT//2+30,
                                        anchor='center', justify='center', state='disabled',
                                        font=font.Font(family='Helvetica', size=24),
                                        text="Yes", tags=("accept"))
                self.canvas.create_text(self.WIDTH//2+60, self.HEIGHT//2+30,
                                        anchor='center', justify='center', state='disabled',
                                        font=font.Font(family='Helvetica', size=24),
                                        text="No", tags=("accept"))
                self.canvas.tag_bind("accept_yes_exit", "<Button-1>", lambda event: back_to_menu())
                self.canvas.tag_bind("accept_no_exit", "<Button-1>", lambda event: denied())
        
        self.canvas.create_rectangle(20, 20, 60, 60,
                                     fill=self.THEMES_LIST[self.current_theme][1], width=3,
                                     tags=("exit"))
        self.canvas.create_text(40, 40, anchor='center', justify='center', 
                                font=font.Font(family='Helvetica', size=36), state='disabled',
                                text="\u21E6")
        self.canvas.tag_bind("exit", "<Button-1>", lambda event: exit_accept())
        # create number buttons
        link = lambda n: (lambda p: self.number_pressed(n))
        for i in range(9):
            self.canvas.create_rectangle(self.WIDTH//10*(i+1)-20, 720, self.WIDTH//10*(i+1)+20, 760,
                                         fill=self.THEMES_LIST[self.current_theme][1], width=3, 
                                         tags=(f"btn_number_{i+1}"))
            self.canvas.create_text(self.WIDTH//10*(i+1), 740,
                                    anchor='center', justify='center', state='disabled',
                                    font=font.Font(family='Helvetica', size=24),
                                    text=str(i+1))
            self.canvas.tag_bind(f"btn_number_{i+1}", "<Button-1>", link(i+1))
        # update cells with board numbers
        self.update_board()
        # bind keyboard numbers with method
        link2 = lambda xp: (lambda p: self.number_pressed(xp))
        for i in range(1, 10):
            self.master.bind(str(i), link2(i))
        self.init_menu()
        self.master.mainloop()
    


    def notes(self) -> None:
        """
        Switches the notes mode
        """
        if not self.flag_menu and not self.flag_pause:
            n = 8 if self.flag_notes else 1
            self.flag_notes = not self.flag_notes
            self.canvas.itemconfig("notes_btn", fill=self.THEMES_LIST[self.current_theme][n])

    def hint_move(self) -> None:
        """
        Fills random one cell in current board with valid number from initial one
        """
        if not self.flag_menu and not self.flag_pause:
            empty = [[i, j] for i in range(9) for j in range(9) if self.board[i][j] == 0]
            if len(empty) > 0:
                hinted_one = random.choice(empty)
                self.board[hinted_one[0]][hinted_one[1]] = self.board_filled[hinted_one[0]][hinted_one[1]]
                self.coords = hinted_one.copy()
                self.find_all_same(self.coords[0], self.coords[1])
                self.update_board()
                self.save_data()

    def restart(self) -> None:
        """
        Copying cells from initial board to current one
        """
        if not self.flag_menu and not self.flag_pause:
            self.board = [i[:] for i in self.board_first]
            self.clear_board()
            self.coords = [-1, -1]
            self.update_board()
            self.save_data()
    
    def erase(self) -> None:
        """
        Erases given cell if it isn't filled in initial board
        """
        if not self.flag_menu and not self.flag_pause:
            self.notes_board[self.coords[0]][self.coords[1]].clear()
            for i in range(1, 10):
                self.canvas.delete(f"block{self.coords[0]}_{self.coords[1]}notes{i}")
            if self.board_first[self.coords[0]][self.coords[1]] == 0:
                self.board[self.coords[0]][self.coords[1]] = 0
                self.clear_board()
                self.cells_colors[self.coords[0]][self.coords[1]] = 4
                self.update_board()
                self.save_data()

    def block_clicked(self, x: int, y: int) -> None:
        """
        Method connected with all cells
        """
        if not self.flag_menu and not self.flag_pause:
            self.coords[0], self.coords[1] = x, y
            self.find_all_same(x, y)

    def number_pressed(self, number: int) -> None:
        """
        Method connected with number keys and number buttons
        """
        if not self.flag_menu and not self.flag_pause and self.coords!=[-1, -1] and self.board[self.coords[0]][self.coords[1]]==0:
            if self.flag_notes:
                if number in self.notes_board[self.coords[0]][self.coords[1]]:
                    self.notes_board[self.coords[0]][self.coords[1]].remove(number)
                    for i in range(1, 10):
                        self.canvas.delete(f"block{self.coords[0]}_{self.coords[1]}notes{i}")
                    for i in range(len(self.notes_board[self.coords[0]][self.coords[1]])):
                        self.canvas.create_text(
                        self.canvas.coords(f"block{self.coords[0]}_{self.coords[1]}")[0]+i%3*self.block_size//3,
                        self.canvas.coords(f"block{self.coords[0]}_{self.coords[1]}")[1]+i//3*self.block_size//3,
                        text=str(self.notes_board[self.coords[0]][self.coords[1]][i]), 
                        font=font.Font(family='Helvetica', size=10), state='disabled', anchor='nw', justify='left', 
                        tags=(f"block{self.coords[0]}_{self.coords[1]}notes{self.notes_board[self.coords[0]][self.coords[1]][i]}"))
                else:
                    self.notes_board[self.coords[0]][self.coords[1]].append(number)
                    self.canvas.create_text(
                    self.canvas.coords(f"block{self.coords[0]}_{self.coords[1]}")[0]+(
                    len(self.notes_board[self.coords[0]][self.coords[1]])-1)%3*self.block_size//3,
                    self.canvas.coords(f"block{self.coords[0]}_{self.coords[1]}")[1]+(
                    len(self.notes_board[self.coords[0]][self.coords[1]])-1)//3*self.block_size//3,
                    text=str(number), font=font.Font(family='Helvetica', size=10), state='disabled',
                    anchor='nw', justify='left', tags=(f"block{self.coords[0]}_{self.coords[1]}notes{number}"))
            else:
                self.notes_board[self.coords[0]][self.coords[1]].clear()
                for i in range(1, 10):
                    self.canvas.delete(f"block{self.coords[0]}_{self.coords[1]}notes{i}")
                self.board[self.coords[0]][self.coords[1]] = number
                if self.sudoku.is_valid(self.board, number, self.coords[0], self.coords[1]):
                    self.find_all_same(self.coords[0], self.coords[1])
                else:
                    self.cells_colors[self.coords[0]][self.coords[1]] = 5
                self.canvas.itemconfig(f"block{self.coords[0]}_{self.coords[1]}text", fill=self.THEMES_LIST[self.current_theme][8])
                self.update_board()
                self.save_data()
                self.win_check()
    
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

    def win_check(self) -> None:
        """
        Check if game is won
        """
        l2, l3 = [[self.board[i][j] for i in range(9)]
                  for j in range(9)], [[self.board[i+k*3][j+m*3] 
                    for i in range(3) for j in range(3)] 
                  for k in range(3) for m in range(3)]
        for i in range(9):
            for j in range(1, 10):
                if self.board[i].count(j)!=1 or l2[i].count(j)!=1 or l3[i].count(j)!=1:
                    return
        self.flag_pause = True
        self.flag_menu = True
        file = open(os.path.join(sys.path[0], "save.txt"), "w")
        file.close()
        self.canvas.create_rectangle(self.WIDTH//2-200, self.HEIGHT//2-100,
                                    self.WIDTH//2+200, self.HEIGHT//2+100,
                                    fill=self.THEMES_LIST[self.current_theme][0], width=3, 
                                    tags=("win_panel"))
        self.canvas.create_text(self.WIDTH//2, self.HEIGHT//2-60,
                                anchor='center', justify='center', state='disabled',
                                font=font.Font(family='Helvetica', size=32),
                                text="You won!", tags=("win_panel"))
        self.canvas.create_rectangle(self.WIDTH//2-100, self.HEIGHT//2-10,
                                     self.WIDTH//2+100, self.HEIGHT//2+50,
                                     fill=self.THEMES_LIST[self.current_theme][1], width=3, 
                                     tags=("win_panel", "win_menu_btn"))
        self.canvas.create_text(self.WIDTH//2, self.HEIGHT//2+20,
                                anchor='center', justify='center', state='disabled',
                                font=font.Font(family='Helvetica', size=24),
                                text="Go to menu", tags=("win_panel"))
        def back_to_menu() -> None:
            self.canvas.delete("win_panel")
            self.flag_menu = True
            self.flag_pause = False
            self.move_menu(20)
        self.canvas.tag_bind("win_menu_btn", "<Button-1>", lambda event: back_to_menu())
        

    def update_board(self) -> None:
        """
        Updates numbers and colors of all cells if they are different
        """
        for i in range(9):
            for j in range(9):
                if self.canvas.itemcget(f"block{i}_{j}", 'fill') != self.THEMES_LIST[self.current_theme][self.cells_colors[i][j]]:
                    self.canvas.itemconfig(f"block{i}_{j}", fill=self.THEMES_LIST[self.current_theme][self.cells_colors[i][j]])
                n = "" if self.board[i][j] == 0 else str(self.board[i][j])
                self.canvas.itemconfig(f"block{i}_{j}text", text=n)

    def new_game(self, difficulty: int = 3) -> None:
        """
        Starts new game with given difficulty
        """
        # generate and save initial game status
        self.board, self.board_filled = self.sudoku.generate_sudoku(difficulty)
        self.board_first = [i[:] for i in self.board]
        self.save_data()
        for i in range(9):
            for j in range(9):
                font_color = 7 if self.board_first[i][j] != 0 else 8
                self.canvas.itemconfig(f"block{i}_{j}text", fill=self.THEMES_LIST[self.current_theme][font_color])
        self.update_board()
        # make menu go up slowly
        self.move_menu(-20)
        self.flag_menu = False
        self.flag_notes = True
        self.notes()

    def resume_game(self) -> None:
        self.move_menu(-20)
        for i in range(9):
            for j in range(9):
                for k in range(len(self.notes_board[i][j])):
                    self.canvas.create_text(
                    self.canvas.coords(f"block{i}_{j}")[0]+k%3*self.block_size//3,
                    self.canvas.coords(f"block{i}_{j}")[1]+k//3*self.block_size//3,
                    text=str(self.notes_board[i][j][k]), font=font.Font(family='Helvetica', size=10), 
                    state='disabled', anchor='nw', justify='left', 
                    tags=(f"block{i}_{j}notes{self.notes_board[i][j][k]}"))
        self.flag_menu = False
        self.flag_notes = True
        self.notes()

    def choose_difficulty(self) -> None:
        """
        Method to create difficulty choose screen
        """
        # create the background
        self.canvas.create_rectangle(0, 0, self.WIDTH, self.HEIGHT, 
                                     fill=self.THEMES_LIST[self.current_theme][0], 
                                     outline="", tags=("diff_panel"))
        # create the borders
        self.canvas.create_rectangle(0, 0, self.BORDER_WIDTH, self.HEIGHT, 
                                     fill=self.THEMES_LIST[self.current_theme][1], 
                                     outline="", tags=("diff_panel"))
        self.canvas.create_rectangle(self.WIDTH-self.BORDER_WIDTH, 0, self.WIDTH, self.HEIGHT, 
                                     fill=self.THEMES_LIST[self.current_theme][1], 
                                     outline="", tags=("diff_panel"))
        self.canvas.create_rectangle(self.BORDER_WIDTH, 0, self.WIDTH-self.BORDER_WIDTH, self.BORDER_WIDTH, 
                                     fill=self.THEMES_LIST[self.current_theme][1], 
                                     outline="", tags=("diff_panel"))
        self.canvas.create_rectangle(self.BORDER_WIDTH, self.HEIGHT-self.BORDER_WIDTH, 
                                     self.WIDTH-self.BORDER_WIDTH, self.HEIGHT, 
                                     fill=self.THEMES_LIST[self.current_theme][1], 
                                     outline="", tags=("diff_panel"))
        # create resume game button if game save is in save.txt
        file = open(os.path.join(sys.path[0], "save.txt"), "r")
        L = [line.strip() for line in file.readlines()]
        file.close()
        if len(L) > 0:
            self.canvas.create_rectangle(self.WIDTH//2-150, 80, self.WIDTH//2+150, 160,
                                         fill=self.THEMES_LIST[self.current_theme][1], width=3,
                                         tags=("resume_game_btn", "diff_panel"))
            self.canvas.create_text(self.WIDTH//2, 120, anchor='center', justify='center', 
                                    font=font.Font(family='Helvetica', size=32), state='disabled',
                                    text="Resume game", tags=("diff_panel"))
            self.canvas.tag_bind("resume_game_btn", "<Button-1>", lambda event: self.resume_game())
        # create difficulty buttons
        self.canvas.create_text(self.WIDTH//2, 260, anchor='center', justify='center', 
                                font=font.Font(family='Helvetica', size=40),
                                text="Start new game", tags=("diff_panel"))
        link = lambda x: (lambda p: self.new_game(x))
        buttons_texts = ["Easy", "Medium", "Hard", "Expert"]
        for i in range(4):
            self.canvas.create_rectangle(self.WIDTH//2-100, 320+i*100, self.WIDTH//2+100, 400+i*100,
                                         fill=self.THEMES_LIST[self.current_theme][1], width=3, 
                                         tags=("diff_panel", f"diff_btn_{i}"))
            self.canvas.create_text(self.WIDTH//2, 360+i*100, anchor='center', justify='center', 
                                    font=font.Font(family='Helvetica', size=32), state='disabled',
                                    text=buttons_texts[i], tags=("diff_panel"))
            self.canvas.tag_bind(f"diff_btn_{i}", "<Button-1>", link(i))
        # create back button
        def back_to_menu() -> None:
            self.canvas.delete("diff_panel")
        self.canvas.create_rectangle(20, self.HEIGHT-60, 60, self.HEIGHT-20,
                                     fill=self.THEMES_LIST[self.current_theme][1], width=3,
                                     tags=("diff_panel", "diff_btn_exit"))
        self.canvas.create_text(40, self.HEIGHT-40, anchor='center', justify='center', 
                                font=font.Font(family='Helvetica', size=36), state='disabled',
                                text="\u21E6", tags=("diff_panel"))
        self.canvas.tag_bind("diff_btn_exit", "<Button-1>", lambda event: back_to_menu())

    def init_menu(self) -> None:
        """
        Method to create main menu
        """
        # create the background
        self.canvas.create_rectangle(0, 0, self.WIDTH, self.HEIGHT, 
                                     fill=self.THEMES_LIST[self.current_theme][0], 
                                     outline="", tags=("start_panel"))
        # create the borders
        self.canvas.create_rectangle(0, 0, self.BORDER_WIDTH, self.HEIGHT, 
                                     fill=self.THEMES_LIST[self.current_theme][1], 
                                     outline="", tags=("start_panel"))
        self.canvas.create_rectangle(self.WIDTH-self.BORDER_WIDTH, 0, self.WIDTH, self.HEIGHT, 
                                     fill=self.THEMES_LIST[self.current_theme][1], 
                                     outline="", tags=("start_panel"))
        self.canvas.create_rectangle(self.BORDER_WIDTH, 0, self.WIDTH-self.BORDER_WIDTH, self.BORDER_WIDTH, 
                                     fill=self.THEMES_LIST[self.current_theme][1], 
                                     outline="", tags=("start_panel"))
        self.canvas.create_rectangle(self.BORDER_WIDTH, self.HEIGHT-self.BORDER_WIDTH, 
                                     self.WIDTH-self.BORDER_WIDTH, self.HEIGHT, 
                                     fill=self.THEMES_LIST[self.current_theme][1], 
                                     outline="", tags=("start_panel"))
        # create buttons
        self.canvas.create_rectangle(self.WIDTH//2-100, self.HEIGHT//2-60, 
                                     self.WIDTH//2+100, self.HEIGHT//2+60,
                                     fill=self.THEMES_LIST[self.current_theme][1],
                                     width=3, tags=("start_panel", "start_play_btn"))
        self.canvas.create_rectangle(self.WIDTH//2-60, self.HEIGHT-80,
                                     self.WIDTH//2+60, self.HEIGHT-40,
                                     fill=self.THEMES_LIST[self.current_theme][1],
                                     width=3, tags=("start_panel", "start_exit_btn"))
        self.canvas.create_text(self.WIDTH//2, self.HEIGHT//2, text="Play", 
                                anchor='center', justify='center', 
                                font=font.Font(family='Helvetica', size=36),
                                state='disabled', tags=("start_panel"))
        self.canvas.create_text(self.WIDTH//2, self.HEIGHT-60, text="Exit", 
                                anchor='center', justify='center', 
                                font=font.Font(family='Helvetica', size=24),
                                state='disabled', tags=("start_panel"))
        # bind buttons
        self.canvas.tag_bind("start_exit_btn", "<Button-1>", lambda event: self.app_close())
        self.canvas.tag_bind("start_play_btn", "<Button-1>", lambda event: self.choose_difficulty())

    def move_menu(self, dir: int) -> None:
        flags = [False, False]
        if len(self.canvas.find_withtag("start_panel"))>0:
            flags[0] = True
        if len(self.canvas.find_withtag("diff_panel"))>0:
            flags[1] = True
        for i in range(self.HEIGHT//20):
            if flags[0]: self.canvas.move("start_panel", 0, dir)
            if flags[1]: self.canvas.move("diff_panel", 0, dir)
            self.canvas.update()
            time.sleep(0.001)
        self.canvas.delete("diff_panel")

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
        save_notes = "-".join(["".join([str(j) for j in i]) for i in [self.notes_board[k][m] for k in range(len(self.notes_board)) for m in range(len(self.notes_board[k]))]])
        file.write(str(fernet.encrypt(save_current.encode()), "UTF-8")+"\n")
        file.write(str(fernet.encrypt(save_first.encode()), "UTF-8")+"\n")
        file.write(str(fernet.encrypt(save_filled.encode()), "UTF-8")+"\n")
        file.write(str(fernet.encrypt(save_notes.encode()), "UTF-8")+"\n")
        file.close()
        

    def app_close(self) -> None:
        """
        Method to close the app
        """
        if not self.flag_menu:
            self.save_data()
        self.master.quit()

        
if __name__ == "__main__":
    app = App()

