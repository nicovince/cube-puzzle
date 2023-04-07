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
    print(f"Try to add {new_piece.name}")
    while piece_collides_with_others(new_piece, puzzle):
        print(f"Tested pos {new_piece}")
        try:
            new_piece.next_pos()
        except StopIteration:
            unused_pieces.append(new_piece)
            return False

    print(f"Add {new_piece.name}")
    print(f"Position {new_piece}")
    puzzle.append(new_piece)
    return True


def solve_puzzle():
    """Solve cube puzzle."""
    unused_pieces = piece.get_pieces()
    puzzle = []

    while len(unused_pieces) > 0:
        if not add_piece(puzzle, unused_pieces):
            print("TODO backtrack !")
            break

    print("done")
    #for p in puzzle:
    #    print(p)

    #print("Unused Pieces:")
    #for p in unused_pieces:
    #    print(p)

def main():
    """Entry point"""
    solve_puzzle()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
