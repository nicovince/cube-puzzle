#!/usr/bin/env python3
"""Handle Pieces, blocks and beams"""
import logging
from coords import Coords3D


def combine_bb_vects(old, new):
    """Combine two vector to move blocks into bounding box."""
    old_coords = [old.x, old.y, old.z]
    new_coords = [new.x, new.y, new.z]
    comb = []
    for old_coord, new_coord in zip(old_coords, new_coords):
        if old_coord == 0:
            comb.append(new_coord)
        elif old_coord < 0:
            assert new_coord <= 0
            comb.append(min(old_coord, new_coord))
        elif old_coord > 0:
            assert new_coord >= 0
            comb.append(max(old_coord, new_coord))
    return Coords3D(comb[0], comb[1], comb[2])


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

    def collides(self, other):
        """Check wether two blocks collides"""
        return self.pos == other.pos

    def rot90_x(self):
        """Rotation 90 degree around x axis."""
        self.pos.rot90_x()

    def rot90_y(self):
        """Rotation 90 degree around y axis."""
        self.pos.rot90_y()

    def rot90_z(self):
        """Rotation 90 degree around z axis."""
        self.pos.rot90_z()

    def get_bb_vect(self):
        """Get vector to move block inside 3x3x3 bounding box."""
        return self.pos.get_bb_vect()


class Beam:
    """Beam holding Block together."""

    def __init__(self, start, vect):
        assert isinstance(start, Coords3D)
        assert isinstance(vect, Coords3D)
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

    def rot90_x(self):
        """Rotation 90 degree around x axis."""
        self.start.rot90_x()
        self.end.rot90_x()
        self.vect.rot90_x()

    def rot90_y(self):
        """Rotation 90 degree around y axis."""
        self.start.rot90_y()
        self.end.rot90_y()
        self.vect.rot90_y()

    def rot90_z(self):
        """Rotation 90 degree around z axis."""
        self.start.rot90_z()
        self.end.rot90_z()
        self.vect.rot90_z()

    def get_bb_vect(self):
        """Get vector to move beam inside 3x3x3 bounding box."""
        v_start = self.start.get_bb_vect(4)
        v_end = self.end.get_bb_vect(4)
        return combine_bb_vects(v_start, v_end)

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

    def collides(self, other):
        """Check wether two pieces collides."""
        collision = False
        for blk in self.blocks:
            for o_blk in other.blocks:
                collision = collision or blk.collides(o_blk)
                if collision:
                    return collision
        return collision

    def rot90_x(self):
        """Rotation 90 degree around x axis."""
        for blk in self.blocks:
            blk.rot90_x()
        for beam in self.beams:
            beam.rot90_x()

    def rot90_y(self):
        """Rotation 90 degree around y axis."""
        for blk in self.blocks:
            blk.rot90_y()
        for beam in self.beams:
            beam.rot90_y()

    def rot90_z(self):
        """Rotation 90 degree around z axis."""
        for blk in self.blocks:
            blk.rot90_z()
        for beam in self.beams:
            beam.rot90_z()

    def get_bb_vect(self):
        """Get vector to move blocks inside 3x3x3 bounding box."""
        vect = Coords3D(0, 0, 0)
        for blk in self.blocks:
            new_vect = blk.get_bb_vect()
            comb_vect = combine_bb_vects(vect, new_vect)
            vect = comb_vect

        for beam in self.beams:
            new_vect = beam.get_bb_vect()
            comb_vect = combine_bb_vects(vect, new_vect)
            vect = comb_vect
        return vect


def get_pieces():
    """Return list of pieces in cube puzzle."""
    pieces = []
    piece1 = Piece([Block(Coords3D(1, 0, 0)), Block(Coords3D(1, 0, 1)), Block(Coords3D(2, 0, 1))],
                   [Beam(Coords3D(0, 0, 1), Coords3D(3, 1, 0)),
                    Beam(Coords3D(1, 1, 0), Coords3D(1, 0, 3))])
    pieces.append(piece1)

    piece2 = Piece([Block(Coords3D(0, 0, 0)),
                    Block(Coords3D(0, 0, 1)),
                    Block(Coords3D(2, 0, 0)),
                    Block(Coords3D(2, 0, 1)),
                   ],
                   [Beam(Coords3D(0, 0, 1), Coords3D(3, 1, 0)),
                    Beam(Coords3D(1, 0, 1), Coords3D(0, 1, 1)),
                    Beam(Coords3D(0, 1, 0), Coords3D(1, 0, 3)),
                   ])
    pieces.append(piece2)

    piece3 = Piece([Block(Coords3D(1, 0, 0)),
                    Block(Coords3D(2, 1, 0)),
                    Block(Coords3D(0, 0, 2)),
                    Block(Coords3D(1, 0, 2)),
                   ],
                   [Beam(Coords3D(1, 0, 0), Coords3D(0, 1, 3)),
                    Beam(Coords3D(0, 1, 0), Coords3D(3, 0, 1)),
                   ])
    pieces.append(piece3)

    piece4 = Piece([Block(Coords3D(1, 0, 0)),
                    Block(Coords3D(0, 0, 2)),
                   ],
                   [Beam(Coords3D(1, 0, 0), Coords3D(0, 1, 3)),
                    Beam(Coords3D(0, 1, 2), Coords3D(3, 0, 1)),
                   ])
    pieces.append(piece4)

    piece5 = Piece([Block(Coords3D(0, 0, 0)),
                    Block(Coords3D(1, 0, 0)),
                    Block(Coords3D(2, 1, 0)),
                    Block(Coords3D(1, 0, 2)),
                   ],
                   [Beam(Coords3D(1, 0, 0), Coords3D(0, 1, 3)),
                    Beam(Coords3D(0, 1, 1), Coords3D(3, 0, 1)),
                   ])
    pieces.append(piece5)

    piece6 = Piece([Block(Coords3D(0, 1, 0)),
                    Block(Coords3D(2, 1, 0)),
                    Block(Coords3D(0, 0, 1)),
                   ],
                   [Beam(Coords3D(0, 1, 0), Coords3D(3, 0, 1)),
                    Beam(Coords3D(0, 0, 1), Coords3D(1, 3, 0)),
                   ])
    pieces.append(piece6)

    piece7 = Piece([Block(Coords3D(0, 0, 0)),
                    Block(Coords3D(2, 0, 0)),
                    Block(Coords3D(2, 0, 1)),
                    Block(Coords3D(2, 1, 2)),
                   ],
                   [Beam(Coords3D(0, 0, 1), Coords3D(3, 1, 0)),
                    Beam(Coords3D(2, 0, 1), Coords3D(0, 1, 1)),
                    Beam(Coords3D(2, 1, 0), Coords3D(1, 0, 3)),
                   ])
    pieces.append(piece7)

    piece8 = Piece([Block(Coords3D(0, 0, 0)),
                    Block(Coords3D(0, 1, 0)),
                   ],
                   [Beam(Coords3D(1, 0, 0), Coords3D(0, 3, 1)),
                    Beam(Coords3D(0, 1, 0), Coords3D(1, 0, 3)),
                    Beam(Coords3D(0, 1, 1), Coords3D(3, 1, 0)),
                   ])
    pieces.append(piece8)
    return pieces


def main():
    """Main function."""
    pieces = get_pieces()
    for piece in pieces:
        print(piece)

    print(f"{pieces[1]} and {pieces[2]} collides: {pieces[0].collides(pieces[1])}")

    print(f"{pieces[1]} rot90_x:")
    pieces[1].rot90_x()
    print(f"{pieces[1]}")
    print(f"vector to move piece into 3x3x3: {pieces[1].get_bb_vect()}")


if __name__ == "__main__":
    main()
