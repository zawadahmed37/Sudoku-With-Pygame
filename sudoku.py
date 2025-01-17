from math import ceil, sqrt
import math
import random
import re
import pygame
import csv

pygame.font.init()

WIN_WIDTH = 900
BOX_WIDTH = 100
CELL_COUNT = 81
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_WIDTH))
pygame.display.set_caption('Sudoku')

WHITE = (245, 245, 245)
BLACK = (10, 10, 10)
GREEN = (0, 100, 0)
RED = (245, 0, 0)

FONT = pygame.font.Font(pygame.font.get_default_font(), 50)

LINE_THICKNESS = 2

WIN.fill(WHITE)

RUNNING = True


class Cell:
    def __init__(self, x, y, width, total_rows):
        self.width = width
        self.total_rows = total_rows
        self.x = int(x * 100)
        self.y = int(y * 100)
        self.number = ''
        self.pre_added = False
        self.text_color = BLACK

    def write_num(self):
        num = FONT.render(self.number, True, self.text_color)
        WIN.blit(num, (self.x + 37, self.y + 20))

    def erase_num(self):
        pygame.draw.rect(WIN, WHITE, (self.x + 7, self.y + 7,
                         self.width - 14, self.width - 14))

    def alert_player(self):
        pygame.draw.rect(WIN, RED, (self.x + 5, self.y + 5,
                         self.width - 10, self.width - 10), 2)

    def remove_alert(self):
        pygame.draw.rect(WIN, WHITE, (self.x + 5, self.y + 5,
                         self.width - 10, self.width - 10), 2)


def make_grid(cell_count, box_width):
    grid = []
    total_rows = int(sqrt(cell_count))
    gap = box_width
    for i in range(cell_count):
        cell = Cell(i % total_rows, math.floor(
            i / total_rows), gap, total_rows)
        grid.append(cell)
    fill_clue_cells(grid)

    return grid


def make_groups():
    groups = []
    start = 0
    end = 3
    while len(groups) < 9:
        indices = []
        for j in range(start, end):
            indices.append(j)
            indices.append(j + 9)
            indices.append(j + 9*2)
        groups.append(indices)
        if end != 9 and end != 36:
            start = start + 3
            end = end + 3
        else:
            start = start + 21
            end = end + 21


def generate_rand_cell_indices():
    file = open('test.csv')
    csv_reader = csv.reader(file)
    rows = []
    for row in csv_reader:
        rows.append(row[0])

    cell_indices = rows[1:]

    return cell_indices


def fill_clue_cells(grid):
    grid = grid
    random_number = random.randint(0, 9)
    cell_indices = generate_rand_cell_indices()[random_number]
    for count, i in enumerate(cell_indices):
        cell = grid[count]
        if i != "0":
            cell.number = i
        if i != "0":
            cell.pre_added = True
        cell.text_color = BLACK
        cell.write_num()


def get_row_and_column(values):
    x, y = values
    column = math.floor(x / 100)
    row = math.floor(y / 100)

    return(row, column)


def get_clicked_index(pos):
    row, column = get_row_and_column(pos)

    return(column + row * 9)


def draw_grid_borders(win, total_rows, box_width, win_width):
    row_gap = box_width
    for i in range(total_rows):
        pygame.draw.line(win, BLACK, (0, i * row_gap),
                         (win_width, i * row_gap), LINE_THICKNESS)
        for j in range(total_rows):
            pygame.draw.line(win, BLACK, (j * row_gap, 0),
                             (j * row_gap, win_width), LINE_THICKNESS)

    for i in range(total_rows//3):
        pygame.draw.line(win, BLACK, (0, i * row_gap * 3),
                         (win_width, i * row_gap * 3), LINE_THICKNESS * 2)
        for j in range(total_rows):
            pygame.draw.line(win, BLACK, (j * row_gap * 3, 0),
                             (j * row_gap * 3, win_width), LINE_THICKNESS * 2)


# checks if the number is already in the same column
def check_column(cell, grid_index, grid):
    duplicate_exists = False
    index = grid_index
    number = cell.number
    grid = grid
    column = []
    original = grid_index
    while index-9 >= 0:
        column.append(index-9)
        index = index-9
    while index+9 <= 80:
        column.append(index+9)
        index = index+9
    column = list(dict.fromkeys(column))
    if original in column:
        column.remove(original)
    for i in column:
        if grid[i].number == number:
            duplicate_exists = True
            break
    return duplicate_exists


# checks if the number is already in the same row
def check_row(cell, grid_index, grid):
    duplicate_exists = False
    index = grid_index
    number = cell.number
    grid = grid
    row = []
    original = grid_index
    while index % 9 != 0:
        row.append(index-1)
        index = index-1
    while (index+1) % 9 != 0:
        row.append(index+1)
        index = index+1
    row = list(dict.fromkeys(row))
    print(row)
    if original in row:
        row.remove(original)
    for i in row:
        if grid[i].number == number:
            duplicate_exists = True
            break
    return duplicate_exists


def draw_window():
    pygame.display.update()


def main(state):
    grid = make_grid(CELL_COUNT, BOX_WIDTH)
    draw_grid_borders(WIN, int(sqrt(CELL_COUNT)), BOX_WIDTH, WIN_WIDTH)
    typing = False
    cell = None
    grid_index = None
    prev_cell = None
    draw_window()
    make_groups()
    while state:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state = False

            if pygame.mouse.get_pressed()[0]:
                if prev_cell and not prev_cell.pre_added:
                    cell = prev_cell
                    cell.remove_alert()
                typing = True
                pos = pygame.mouse.get_pos()
                grid_index = get_clicked_index(pos)
                cell = grid[grid_index]
                if not cell.pre_added:
                    cell.alert_player()
                draw_window()
                prev_cell = cell

            if typing and not cell.pre_added and event.type == pygame.KEYDOWN:
                player_input = pygame.key.name(event.key)
                input_num = re.findall(r'\d+', player_input)
                if input_num:
                    cell.erase_num()
                    cell.number = str(input_num[0])
                    duplicate_in_column = check_column(cell, grid_index, grid)
                    duplicate_in_row = check_row(cell, grid_index, grid)
                    if duplicate_in_column or duplicate_in_row:
                        cell.text_color = RED
                    else:
                        cell.text_color = GREEN
                    cell.write_num()
                elif event.key == pygame.K_BACKSPACE:
                    cell.erase_num()

                draw_window()


main(RUNNING)
