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
    except StopIteration:
        rm_piece.move_start_pos()
        backtrack(puzzle, unused_pieces)
    finally:
        logging.info("Re-store backtracked %s to heap", rm_piece.name)
        unused_pieces.append(rm_piece)


def solve_puzzle():
    """Solve cube puzzle."""
    unused_pieces = piece.get_pieces5()
    puzzle = []

    while len(unused_pieces) > 0:
        logging.info("Puzzle: %d pieces, unused: %d pieces", len(puzzle), len(unused_pieces))
        if not add_piece(puzzle, unused_pieces):
            logging.info("Backtrack with %d pieces set and %d left", len(puzzle), len(unused_pieces))
            backtrack(puzzle, unused_pieces)


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
