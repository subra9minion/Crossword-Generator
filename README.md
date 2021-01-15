# Crossword-Generator

The Crossword-Generator generates a crossword puzzle given a list of words to choose from and the structure desired. It is modeled as a **constraint satisfaction problem**.

## Installation

1. Ensure you have Python (3.3 or greater) installed.
1. Download this folder into your system.
1. Run ```pip3 install Pillow``` in your terminal.

## Usage
Crossword-Generator requires two files to generate a puzzle:
1. **A structure file** that defines the structure of the puzzle. ```_``` is used to represent blank cells (which should be filled in) and ```#``` is used to represent cells that won't be filled in.
2. **A words file** that defines a list of words (one on each line) to use for the vocabulary of the puzzle.

Three examples of each of these files can be found in the ```data``` directory of the project. 
Once the files are ready, run ```python generate.py structure_file words_file output.png```. 
The puzzle is saved onto the ```output.png``` file.

## Sample
```python generate.py data/structure1.txt data/words1.txt output.png```

<img src="https://github.com/subra9minion/Crossword-Generator/blob/master/data/sample.png" width="65%" />

## License
This project was made under CS50's Introduction to Artificial Intelligence, a course of study by HarvardX. <br>
The course is licensed under a [Creative Commons License](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode).
