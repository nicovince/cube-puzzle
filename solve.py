#!/usr/bin/env python3
"""
puzzle = []
add piece to puzzle
if collision, translate/rotate last piece
if all positions exhausted remove piece n-1 and translate/rotate that piece
"""

import argparse
import logging
import time
import cProfile
import copy
import numpy as np
import piece
from coords import Coords3D

solve_grid_dim = 25

def piece_collides_with_others(one, others):
    """Check if a piece collides with list of other pieces (not colliding with each others)"""
    for other_piece in others:
        if other_piece.collides(one):
            return True
    return False


def np_check_collision(pce, puzzle):
    """Compute numpy representation and check collision with the rest of the puzzle."""
    pce.compute_np(solve_grid_dim)
    for p in puzzle:
        p.compute_np(solve_grid_dim)
    return piece_collides_with_others(pce, puzzle)


def dump_state(filename, puzzle, unused, comment=None):
    """Dump puzzle state"""
    logging.debug("Dump to %s", filename)
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


def get_str_state(puzzle, unused):
    """Get string to reprensent state of puzzle and unused pieces."""
    state = ""
    for p in puzzle:
        state += f"{p.name} "
        if p.iterator is None:
            state += "X"
        else:
            state += f"{p.iterator.current_position} "

    state += "["
    for p in unused:
        state += f"{p.name} "
    state += "]"
    return state


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
            new_piece.reset()
            unused_pieces.append(new_piece)
            return False

    logging.debug("Add %s in position %s", new_piece.name, new_piece.iterator)
    logging.debug("Position %s", new_piece)
    puzzle.append(new_piece)
    return True


def backtrack(puzzle, unused_pieces):
    """Backtrack on pieces."""
    rm_piece = puzzle.pop()
    try:
        rm_piece.next_pos()
        logging.debug("Re-store backtracked %s to heap in position %s",
                      rm_piece.name, rm_piece.iterator)
        unused_pieces.append(rm_piece)
    except StopIteration:
        rm_piece.reset()
        logging.info("Re-store backtracked %s to heap in original position", rm_piece.name)
        unused_pieces.append(rm_piece)
        backtrack(puzzle, unused_pieces)


def mount_puzzle():
    """Mount cube puzzle."""
    unused_pieces = piece.get_pieces5()
    puzzle = []

    i = 0
    n_pieces = 1000
    last_ts = time.time()
    start_ts = last_ts
    while len(unused_pieces) > 0:
        logging.debug("state %d Puzzle: %d pieces, unused: %d pieces",
                      i, len(puzzle), len(unused_pieces))
        if not add_piece(puzzle, unused_pieces):
            logging.debug("Backtrack on %s with %d pieces set and %d left",
                          puzzle[-1].name, len(puzzle), len(unused_pieces))
            backtrack(puzzle, unused_pieces)
        #dump_state(f"state_{i:03d}_{len(puzzle)}_{len(unused_pieces)}.py", puzzle, unused_pieces)
        #print(get_str_state(puzzle, unused_pieces))
        i = i + 1
        if i % n_pieces == 0:
            now_ts = time.time()
            logging.info("Processed %d states in %ds, total processed %d in %ds",
                         n_pieces, now_ts - last_ts, i, now_ts - start_ts)
            last_ts = now_ts

    print("done")
    for p in puzzle:
        print(p)
        print(f"{p!r}")


def move_puzzle_piece(puzzle, piece):
    """Move piece of puzzle without causing collision.

    puzze: list of pieces forming the current puzzle state
    piece: member of puzzle this function will try to translate.

    Return Movement vector
    """
    p_idx = puzzle.index(piece)
    # Remove piece of puzzle temporary to check collision with the rest
    puzzle.remove(piece)
    movements = [Coords3D(1, 0, 0), Coords3D(0, 1, 0), Coords3D(0, 0, 1),
                 Coords3D(-1, 0, 0), Coords3D(0, -1, 0), Coords3D(0, 0, -1)]
    bb_start = Coords3D(0, 0, 0)
    bb_end = Coords3D(solve_grid_dim - 1, solve_grid_dim - 1, solve_grid_dim - 1)
    last_trans = piece.get_last_trans()
    if last_trans is not None:
        logging.debug("%s last trans %s, remove %s for possible movements",
                      piece.name, last_trans, -last_trans.get_direction())
        movements.remove(-last_trans.get_direction())

    trans = None
    for m in movements:
        trans = m
        trans_cnt = 0
        piece.translate(m)
        while piece.is_within(bb_start, bb_end) and not np_check_collision(piece, puzzle):
            trans_cnt += 1
            piece.translate(m)
        # Revert last translation as it caused the piece to collide or move out of the bounding box
        piece.translate(-m)
        if trans_cnt != 0:
            break
    puzzle.insert(p_idx, piece)
    return trans, trans_cnt


def try_remove_piece(puzzle, pieces_out, puzzle_bb_np):
    """Try to remove pieces from puzzle which are out of the puzzle bounding box."""

    for p in puzzle:
        blks_union = p.np_blbe & puzzle_bb_np
        if np.amax(blks_union) == 0:
            print(f"{p.name} is out of puzzle")
            pieces_out.append(p)
            rm_piece = p
            puzzle.remove(p)
            return True
    return False



def unmount_puzzle_step(puzzle, pieces_out, puzzle_bb_np):
    """Move a piece of the puzzle."""
    trans = None
    piece_moved = None
    null_trans = Coords3D(0, 0, 0)
    for p in puzzle:
        logging.debug("%s trans history: %s", p.name, p.umount_trans_history)
        while True:
            unit_dir, trans_cnt = move_puzzle_piece(puzzle, p)
            trans = unit_dir * trans_cnt
            if trans == null_trans:
                logging.debug("%s could not be moved", p.name)
                trans = None
                break
            logging.info("Moved %s %s", p.name, trans)
            p.add_trans_history(trans)
            if trans is not None:
                piece_moved = p
                break
        logging.debug("Processed %s", p.name)
        if trans is not None:
            break
    if trans is None:
        logging.info("Could not move anything, Archive translation history.")
        for p in puzzle:
            p.archive_history()
    return unit_dir, trans_cnt, piece_moved

def umount_puzzle():
    """Remove pieces of puzzle without collision."""
    puzzle = piece.get_result()
    shift = int((solve_grid_dim - 5) / 2)
    # Move pieces away from origin so they stay in positive coords when being
    # translated to get out of the mounted puzzle.
    for p in puzzle:
        p.translate(Coords3D(shift, shift, shift))
        p.compute_np(solve_grid_dim)

    puzzle_bb_np = np.zeros((solve_grid_dim, solve_grid_dim, solve_grid_dim), dtype=int)
    for x in range(shift, shift + 5):
        for y in range(shift, shift + 5):
            for z in range(shift, shift + 5):
                puzzle_bb_np[x, y, z] = 1

    pieces_out = []
    steps = []
    while len(puzzle) > 1:
        unit_dir, trans_cnt, piece_moved = unmount_puzzle_step(puzzle, pieces_out, puzzle_bb_np)
        piece_moved.translate(-unit_dir * trans_cnt)
        for _ in range(trans_cnt):
            piece_moved.translate(unit_dir)
            steps.append(copy.deepcopy(puzzle))
        if try_remove_piece(puzzle, pieces_out, puzzle_bb_np):
            steps.append(copy.deepcopy(puzzle))

    print("Et voila !")
    return steps


def solve_puzzle(action):
    """Solve Puzzle.

    action: mount or umount
    """
    if action == "mount":
        mount_puzzle()
    else:
        umount_puzzle()


def main():
    """Entry point"""
    parser = argparse.ArgumentParser(prog="solve", description="Solve Cube Puzzle")
    parser.add_argument("--action", default="umount", choices=["mount", "umount"],
                        help="Solving action to perform.")
    parser.add_argument("--loglevel",
                        default='warning',
                        help='Provide logging level. Example --loglevel debug, default=warning')
    parser.add_argument("--cprof",
                        default=False,
                        action="store_true",
                        help="Enable cProfile")
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel.upper())

    if args.cprof:
        cProfile.run(f"solve_puzzle({args.action})")
    else:
        solve_puzzle(args.action)

if __name__ == "__main__":
    main()
