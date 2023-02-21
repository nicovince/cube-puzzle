#!/usr/bin/env python3
"""Handle Pieces, blocks and beams"""
import logging
from coords import Coords3D

class Block:
    """Single Cube Block representation."""
    def __init__(self, pos):
        assert isinstance(pos, Coords3D)
        self.pos = pos
        if not self.is_valid():
            logging.warning("Invalid position %s", self)


    def __repr__(self):
        return f"{type(self).__name__}(pos={self.pos!r})"

    def __str__(self):
        return f"block at {self.pos}"

    def is_valid(self):
        """Check wether the block is in a valid position."""
        bb_start = Coords3D(0, 0, 0)
        bb_end = Coords3D(2, 2, 2)
        return self.pos.is_within(bb_start, bb_end)

class Beam:
    """Beam holding Block together."""
    def __init__(self, start, vect):
        assert isinstance(start, Coords3D)
        self.start = start
        self.end = start.add(vect)
        self.vect = vect
        if not self.is_valid():
            logging.warning("Invalid beam %s", self)

    def is_valid(self):
        """Check wether the beam is in a valid position."""
        bb_start = Coords3D(0, 0, 0)
        bb_end = Coords3D(3, 3, 3)
        return self.start.is_within(bb_start, bb_end) and self.end.is_within(bb_start, bb_end)

    def __str__(self):
        return f"start: {self.start} vect:{self.vect}"

    def __repr__(self):
        return f"{type(self).__name__}(start={self.start!r}, vect={self.vect!r})"

class Piece:
    """Collection of Beams and Blocks."""
    def __init__(self, blocks, beams):
        assert isinstance(blocks, list)
        assert isinstance(beams, list)

        for blk in blocks:
            assert isinstance(blk, Block)

        for beam in beams:
            assert isinstance(beam, Beam)

        self.blocks = blocks
        self.beams = beams

    def __repr__(self):
        return f"{type(self).__name__}(blocks={self.blocks}, beams={self.beams})"

    def __str__(self):
        out = "Blocks:\n"
        for blk in self.blocks:
            out += " - "
            out += str(blk)
            out += "\n"
        out += "Beams:\n"
        for beam in self.beams:
            out += " - "
            out += str(beam)
            out += "\n"
        return out


    def is_valid(self):
        """Check wether the current positions of blocks and beams are valid."""
        out = True
        for blk in self.blocks:
            out = out and blk.is_valid()
            if not out:
                return out
        for beam in self.beams:
            out = out and beam.is_valid()
            if not out:
                return out
        return out


def main():
    """Main function."""
    piece1 = Piece([Block(Coords3D(1, 0, 0)), Block(Coords3D(1, 0, 1)), Block(Coords3D(2, 0, 1))],
                   [Beam(Coords3D(0, 0, 1), Coords3D(3, 1, 0)),
                    Beam(Coords3D(1, 1, 0), Coords3D(1, 0, 3))])
    print(piece1)
    print(piece1.blocks[0])

if __name__ == "__main__":
    main()
