import itertools
import random
from itertools import product


class Minesweeper:
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        # Inicializa todo el tablero con sus respectivos espacios vacios
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Añaden las minas randomicamente en cada uno de los espacios en blanco
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    # Función que permite imprimir la representación del tablero
    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        # Es una forma de imprimir la representación del tablero
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    # Comprueba si una determinada celda es una mina
    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    # Es una función que trata de buscar las minas cercanas referente a una casilla
    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        # Recorrer todas las celdas referente a una fila o columna
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                # Ignora a la propia celda
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                # Realizar el conteo de la celda, apra ver si es mia o esta dentro de los limites
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        """
        COmprueba si todas la minas han sido marcadas
        """
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """
    """
    Incorporación de las sentencias dentro de la base del conocimiento
    """
    _no = 0

    def __init__(self, cells, count):
        self.cells = set(cells) # Se incorpora dentro de un conjunto
        self.count = count
        self.no = Sentence._no # Incorporar uan nueva sentencia
        Sentence._no += 1 # Aumenta el contador del número de sentencias

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"n.{self.no}: {self.cells} = {self.count}"

    def __repr__(self):
        return f"n.{self.no}: {self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()
        # raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # raise NotImplementedError
        if self.count == 0:
            if len(self.cells) != 0:
                print(f"{self} => SAFE: {self.cells}")
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # print('mark_mine')
        # 1. Check if cell is one of the cells included in the sentence
        # 2. If cell is in the sentence, update the sentence so that
        #    cell is no longer in the sentence, but still
        if cell not in self.cells:
            return

        self.cells.remove(cell)
        self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell not in self.cells:
            return

        self.cells.remove(cell)


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def cross_check(self):
        """
        Checks all the sentences using the subset inference
        """
        kn_bef = self.knowledge.copy()
        for i in range(0, len(kn_bef) - 1):
            for j in range(i + 1, len(kn_bef)):
                sent1 = kn_bef[i]
                sent2 = kn_bef[j]
                if (sent1.cells and sent2.cells):
                    if sent1.cells.issubset(sent2.cells):
                        new_sent = Sentence(
                            sent2.cells - sent1.cells,
                            sent2.count - sent1.count
                        )
                        if new_sent not in self.knowledge:
                            self.knowledge.append(new_sent)

    def infer(self):
        """
        Updates the stats using updated knowledge
        """
        for sent in self.knowledge:
            for cell in sent.known_safes().copy():
                self.mark_safe(cell)
            for cell in sent.known_mines().copy():
                self.mark_mine(cell)

    # Algorithm by etuardu from StackOverflow
    def neighbours(self, cell):
        size = 8
        for c in product(*(range(n - 1, n + 2) for n in cell)):
            if c != cell and all(0 <= n < size for n in c):
                yield c

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)

        self.mark_safe(cell)

        cells = set()

        for c in self.neighbours(cell):
            if c not in self.safes:
                cells.add(c)

        sent = Sentence(cells, count)

        self.knowledge.append(sent)

        self.infer()
        self.cross_check()
        self.infer()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        if len(self.mines) == 8:
            return None
        for cell in self.safes:
            if cell not in self.moves_made and cell not in self.mines:
                return cell
        return None

    def make_random_move(self):
        # print('make_random_move')
        # print(f"Mines: {self.mines}")
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        if len(self.mines) == 8:
            return None
        possible_moves = []
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made:
                    possible_moves.append((i, j))
        while len(possible_moves) != 0:
            index = random.randrange(len(possible_moves))
            if possible_moves[index] not in self.mines:
                return possible_moves[index]
            possible_moves.pop(index)
        return None
