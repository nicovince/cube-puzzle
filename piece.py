#!/usr/bin/env python3
import logging
from coords import Coords3D

class Block:
    def __init__(self, pos):
        assert isinstance(pos, Coords3D)
        self.pos = pos
        if not self.is_valid():
            logging.warning(f"Invalid position {self}")


    def __repr__(self):
        return f"{type(self).__name__}(pos={self.pos!r})"

    def __str__(self):
        return f"block at {self.pos}"

    def is_valid(self):
        """Check wether the block is in a valid position."""
        bb_start = Coords3D(0, 0, 0)
        bb_end = Coords3D(2, 2, 2)
        return self.pos.is_within(bb_start, bb_end)

class Bar:
    def __init__(self, start, vect):
        assert isinstance(start, Coords3D)
        self.start = start
        self.end = start.add(vect)
        self.vect = vect
        if not self.is_valid():
            logging.warning(f"Invalid bar {self}")

    def is_valid(self):
        bb_start = Coords3D(0, 0, 0)
        bb_end = Coords3D(3, 3, 3)
        return (self.start.is_within(bb_start, bb_end) and self.end.is_within(bb_start, bb_end))

    def __str__(self):
        return f"start: {self.start} vect:{self.vect}"

    def __repr__(self):
        return f"{type(self).__name__}(start={self.start!r}, vect={self.vect!r})"

class Piece:
    def __init__(self, blocks, bars):
        assert isinstance(blocks, list)
        assert isinstance(bars, list)

        for b in blocks:
            assert isinstance(b, Block)

        for b in bars:
            assert isinstance(b, Bar)

        self.blocks = blocks
        self.bars = bars

    def __repr__(self):
        return f"{type(self).__name__}(blocks={self.blocks}, bars={self.bars})"

    def __str__(self):
        s = "Blocks:\n"
        for b in self.blocks:
            s += " - "
            s += str(b)
            s += "\n"
        s += "Bars:\n"
        for b in self.bars:
            s += " - "
            s += str(b)
            s += "\n"
        return s


    def is_valid(self):
        """Check wether the current positions of blocks and bars are valid."""
        pass


def main():
    p1 = Piece([Block(Coords3D(1, 0, 0)), Block(Coords3D(1, 0, 1)), Block(Coords3D(2, 0, 1))],
               [Bar(Coords3D(0, 0, 1), Coords3D(3, 1, 0)),
                Bar(Coords3D(1, 1, 0), Coords3D(1, 0, 3))])
    print(p1)
    print(p1.blocks[0])

if __name__ == "__main__":
    main()
