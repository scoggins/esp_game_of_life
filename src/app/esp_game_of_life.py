#!/usr/bin/env micropython
# main.py
import time
import random
import machine
from machine import Timer, Pin
import neopixel
import micropython

LED_PIN = machine.Pin(4, Pin.OUT)
MATRIX_SIZE = 16

class Matrix:
    def __init__(self, size=MATRIX_SIZE):
        self._size = size
        self._matrix = neopixel.NeoPixel(LED_PIN, size*size)
        self.all_on()
        time.sleep(1)
        self.all_off()

    def all_off(self):
        for idx in range(0, self._size*self._size):
            self._matrix[idx] = (0, 0, 0)
        self._matrix.write()

    def all_on(self):
        for idx in range(0, self._size*self._size):
            self._matrix[idx] = (10, 10, 10)
        self._matrix.write()


    def test_pattern(self):
        for row in range(self._size):
            for column in range(self._size):
                # We need to flip odd
                if row % 2:
                    idx = (row * self._size) + (self._size - 1 - column)
                else:
                    idx = (row * self._size) + column
                self._matrix[idx] = (10, 10, 10)
                self._matrix.write()
                time.sleep(0.1)

    def update_matrix(self, matrix, state_func):
        size = len(matrix)
        for row in range(size):
            for column in range(size):
                # We need to flip odd
                if row % 2:
                    idx = (row * self._size) + (self._size - 1 - column)
                else:
                    idx = (row * self._size) + column
                self._matrix[idx] = getattr(matrix[row][column], state_func)()
        self._matrix.write()


class Cell:
    def __init__(self):
        self._alive = False
        self._born = 0
        self._colour = (0, 0, 0)

    def is_alive(self):
        return self._alive

    def set_alive(self):
        self._alive = True
        self._born = time.time()
        self._colour = (random.getrandbits(4), random.getrandbits(4), random.getrandbits(4))

    def set_dead(self):
        self._alive = False
        self._born = 0
        self._colour = (0, 0, 0)

    def age(self):
        return time.time()-self._born

    def led_state(self):
        return self._colour

    def state(self):
        if self._alive:
            return "*"
        return "0"

class Board:
    def __init__(self, size=MATRIX_SIZE):
        self._size = size
        # Create a board using nexted arrays.
        self._board =  [[Cell() for column in range(size)] for row in range(size)]
        self.generate_board()

    def generate_board(self):
        for row in self._board:
            for cell in row:
                # 25% chance to be alive
                if random.getrandbits(2) == 1:
                    cell.set_alive()

    def get_neighbours_alive(self, row, column):
        neighbours_alive = 0

        # Check Neighbours
        for n_row in range(row-1, row+2):
            for n_column in range(column-1, column+2):
                # If ourside board, it's wrap it around.
                if n_row >= self._size:
                    n_row = n_row - self._size
                if n_column >= self._size:
                    n_column = n_column  - self._size

                # If it's us, skip.
                if n_row == row and n_column == column:
                    continue

                if self._board[n_row][n_column].is_alive():
                    neighbours_alive += 1

        return neighbours_alive

    def update_board(self):
        born = []
        died = []
        total_alive = 0

        for row in range(0, self._size):
            for column in range(0, self._size):
                neighbours_alive = self.get_neighbours_alive(row, column)

                # Work out what we need to do:
                cell = self._board[row][column]

                if cell.is_alive():
                    if (neighbours_alive < 2) or  (neighbours_alive > 3):
                        died.append(cell)
                    else:
                        total_alive += 1
                else:
                    if neighbours_alive == 2:
                        born.append(cell)

        # Process the changes:
        for cell in born:
            cell.set_alive()
        for cell in died:
            cell.set_dead()
        print("Update: %d born, %d died, %d alive" % (len(born), len(died), total_alive))

    def get_matrix(self):
        return self._board

    def dump_board(self):
        print("\n"*24)
        for row in self._board:
            print(" ".join([cell.state() for cell in row]))


class App:
    def __init__(self, config):
        self.board = Board()
        self.matrix = Matrix()
        self.config = config
        self.led_timer = Timer(0)
        self.led_timer_callback_ref = self.led_timer_callback

    def start(self):
        self.led_timer.init(period=1000, mode=Timer.PERIODIC, callback=self.led_timer_callback_ref)

    def stop(self):
        self.led_timer.deinit()

    def led_timer_callback(self):
        print("Timer trigger")
        #micropython.schedule(self.update_loop, None)

    def update_loop(self):
        self.matrix.update_matrix(self.board.get_matrix(), "led_state")
        self.board.update_board()
