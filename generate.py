import sys

from crossword import Variable, Crossword
from collections import deque

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("_", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        # set of inconsistent values
        inconsistent = set()

        for variable in self.crossword.variables:
            var_length = variable.length

            # if length does not match, mark as inconsistent
            for word in self.domains[variable]:
                if len(word) != var_length:
                    inconsistent.add(word)
            
            # remove all inconsistencies from domain
            for word in inconsistent:
                self.domains[variable].remove(word)
            
            # clear inconsistencies
            inconsistent.clear()

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        # set of inconsistent values
        inconsistent = set()
        overlaps = self.crossword.overlaps[x, y]
        revised = False

        for xword in self.domains[x]:
            flag = 0

            # if possible value exists, flag
            for yword in self.domains[y]:
                if xword[overlaps[0]] == yword[overlaps[1]]:
                    flag = 1
                    break
            
            # if no possible value for y exists, revise
            if flag == 0:
                inconsistent.add(xword)
                revised = True

        # removing inconsistent words from x, if any
        for word in inconsistent:
            self.domains[x].remove(word)

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = deque()

        # adding all arcs to queue, if arcs = None
        if arcs is None:
            for x in self.crossword.variables:
                for y in self.crossword.neighbors(x):
                    queue.append((x, y))

        # adding given arcs to queue, otherwise
        else:
            for arc in arcs:
                queue.append(arc)

        while queue:
            arc = queue.popleft()

            # revise arc and modify queue
            if self.revise(arc[0], arc[1]):

                # if removed all values from x after revision
                if len(self.domains[x]) == 0:
                    return False

                # modifying queue
                for z in self.crossword.neighbors(arc[0]):
                    if z == y: continue
                    queue.append((z, arc[0]))
            
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable not in assignment.keys():
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        
        # checking unique values
        values = list(assignment.values())
        for value in values:
            if values.count(value) > 1:
                return False
        
        # checking lengths
        for variable in list(assignment.keys()):
            if variable.length != len(assignment[variable]):
                return False
        
        # checking conflicts
        for variable in list(assignment.keys()):

            neighbors = self.crossword.neighbors(variable)
            
            for neighbor in neighbors:
                if neighbor not in list(assignment.keys()): 
                    continue

                overlaps = self.crossword.overlaps[variable, neighbor]
                if assignment[variable][overlaps[0]] != assignment[neighbor][overlaps[1]]:
                    return False
                
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # dictionary mapping domains to n
        domain = {}
        for word in self.domains[var]:
            domain[word] = 0
    
        # calculating n for each domain value
        neighbors = self.crossword.neighbors(var)
        for word in self.domains[var]:
            for neighbor in neighbors:
                overlaps = self.crossword.overlaps[var, neighbor]
                for neighbor_word in self.domains[neighbor]:                  
                    if word[overlaps[0]] == neighbor_word[overlaps[1]]:
                        continue
                    domain[word] += 1

        # sorted dictionary 
        ordered_domain = {k:v for k, v in sorted(domain.items(), key=lambda item: item[1])}
        return list(ordered_domain.keys())

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
       
        # dictionary to store remaining domain values for each variable
        remaining_vals = {}
        for variable in self.crossword.variables:
            if variable in list(assignment.keys()):
                continue
            remaining_vals[variable] = len(self.domains[variable])

        # minimum remaining value
        mrv = min(remaining_vals.items(), key=lambda item: item[1])[1]

        # dictionary to store degrees of all mrv variables
        degrees = {}
        for k, v in remaining_vals.items():
            if v == mrv:
                degrees[k] = len(self.crossword.neighbors(k))

        # returning variable w/ max degree
        variable = max(degrees.items(), key=lambda item: item[1])[0]
        return variable

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        variable = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(variable, assignment):

            assignment[variable] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None: return result
            del assignment[variable]

        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
