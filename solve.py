#!/usr/bin/env python3
"""
puzzle = []
add piece to puzzle
if collision, translate/rotate last piece
if all positions exhausted remove piece n-1 and translate/rotate that piece
"""

import logging
import piece

def piece_collides_with_others(one, others):
    """Check if a piece collides with list of other pieces (not colliding with each others)"""
    for other_piece in others:
        if other_piece.collides(one):
            return True
    return False


def dump_state(filename, puzzle, unused, comment=None):
    """Dump puzzle state"""
    logging.debug(f"Dump to {filename}")
    with open(filename, 'w') as fd:
        fd.write("#!/usr/bin/env python3\n")
        fd.write("from piece import *")
        if comment is not None:
            fd.write(f"# {comment}\n\n")
        fd.write("# Pieces inside puzzle\n")
        fd.write("puzzle = []\n")
        for piece_puzzle in puzzle:
            fd.write(f"puzzle.append({piece_puzzle!r})\n")
        fd.write("# Unused pieces\n")
        fd.write("unused = []\n")
        for piece_unused in unused:
            fd.write(f"unused.append({piece_unused!r})\n")


def add_piece(puzzle, unused_pieces):
    """Add a piece from unused to the puzzle if possible
    Return True if a piece was added, False otherwise.
    """
    new_piece = unused_pieces.pop()
    logging.debug("Try to add %s", new_piece.name)
    while piece_collides_with_others(new_piece, puzzle):
        try:
            new_piece.next_pos()
        except StopIteration:
            unused_pieces.append(new_piece)
            return False

    logging.debug("Add %s in position %s", new_piece.name, new_piece.iterator)
    logging.debug("Position %s", new_piece)
    puzzle.append(new_piece)
    return True


def backtrack(puzzle, unused_pieces):
    """Backtrack on pieces."""
    rm_piece = puzzle.pop()
    logging.info("Backtrack on %s", rm_piece.name)
    try:
        rm_piece.next_pos()
        logging.info("Re-store backtracked %s to heap in position %s",
                     rm_piece.name, rm_piece.iterator)
        unused_pieces.append(rm_piece)
    except StopIteration:
        rm_piece.move_start_pos()
        rm_piece.iterator = None
        logging.info("Re-store backtracked %s to heap in original position", rm_piece.name)
        unused_pieces.append(rm_piece)
        backtrack(puzzle, unused_pieces)


def solve_puzzle():
    """Solve cube puzzle."""
    unused_pieces = piece.get_pieces5()
    puzzle = []

    i = 0
    while len(unused_pieces) > 0:
        logging.info("Puzzle: %d pieces, unused: %d pieces", len(puzzle), len(unused_pieces))
        if not add_piece(puzzle, unused_pieces):
            logging.info("Backtrack with %d pieces set and %d left",
                         len(puzzle), len(unused_pieces))
            backtrack(puzzle, unused_pieces)
        dump_state(f"state_{i:03d}_{len(puzzle)}_{len(unused_pieces)}.py", puzzle, unused_pieces)
        i = i + 1


    print("done")
    for p in puzzle:
        print(p)

    #print("Unused Pieces:")
    #for p in unused_pieces:
    #    print(p)

def main():
    """Entry point"""
    solve_puzzle()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
