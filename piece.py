#!/usr/bin/env python3
"""Handle Pieces, blocks and beams"""
import logging
import copy
from coords import Coords3D
import sys


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


def block_coord_to_grid5(pos):
    """Change scalar coord of block from [0:2] to [0:4].

    Beams become 1 wide thick.
    """
    if pos == 0:
        return pos
    if pos == 1:
        return pos + 1
    if pos == 2:
        return pos + 2
    assert False, f"Invalid position value {pos}"
    return None


def beam_coord_to_grid5(pos):
    """Change scalar coord of beam from [0:2] to [0:4]

    Beams become 1 wide thick.
    """
    if pos == 0:
        return pos
    if pos == 1:
        return pos
    if pos == 2:
        return pos + 1
    if pos == 3:
        return pos + 2
    assert False, f"Invalid beam pos {pos}"
    return None


def beam_to_grid5(coords3d):
    """Change Beam coords to grid 5 representation."""
    return Coords3D(beam_coord_to_grid5(coords3d.x),
                    beam_coord_to_grid5(coords3d.y),
                    beam_coord_to_grid5(coords3d.z))


class Block:
    """Single Cube Block representation."""

    def __init__(self, pos, grid_5=False):
        assert isinstance(pos, Coords3D)
        self.pos = pos
        self.grid_5 = grid_5
        if not self.is_valid():
            logging.warning("Invalid position %s", self)

    def __repr__(self):
        out = f"{type(self).__name__}(pos={self.pos!r}"
        if self.grid_5:
            out += ", grid_5=True"
        out += ")"
        return out


    def __str__(self):
        return f"block at {self.pos}"

    def to_grid_5(self):
        """Change block representation in a 3x3x3 to 5x5x5."""
        blk = Coords3D(block_coord_to_grid5(self.pos.x),
                       block_coord_to_grid5(self.pos.y),
                       block_coord_to_grid5(self.pos.z))
        return Block(blk, True)

    def is_valid(self):
        """Check wether the block is in a valid position."""
        bb_start = Coords3D(0, 0, 0)
        if not self.grid_5:
            bb_end = Coords3D(2, 2, 2)
        else:
            bb_end = Coords3D(4, 4, 4)
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
        if self.grid_5:
            bb_len = 5
        else:
            bb_len = 3
        return self.pos.get_bb_vect(bb_len)


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

    def to_grid_5(self):
        """Change Beam representation in a 3x3x3 to blocks in a 5x5x5."""
        blocks = []
        start = beam_to_grid5(self.start)
        vect = beam_to_grid5(self.vect)
        for x in range(max(1, vect.x)):
            for y in range(max(1, vect.y)):
                for z in range(max(1, vect.z)):
                    blocks.append(Block(Coords3D(start.x + x, start.y + y, start.z + z), True))
        return blocks


    def is_valid(self):
        """Check whether the beam is in a valid position."""
        bb_start = Coords3D(0, 0, 0)
        bb_end = Coords3D(3, 3, 3)
        return self.start.is_within(bb_start, bb_end) and self.end.is_within(bb_start, bb_end)

    def rot90_x(self):
        """Rotation 90 degrees around x axis."""
        self.start.rot90_x()
        self.end.rot90_x()
        self.vect.rot90_x()

    def rot90_y(self):
        """Rotation 90 degrees around y axis."""
        self.start.rot90_y()
        self.end.rot90_y()
        self.vect.rot90_y()

    def rot90_z(self):
        """Rotation 90 degrees around z axis."""
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


class Piece5:
    """Piece in a 5x5x5 representation."""
    def __init__(self, blocks, beams, name=None):
        assert isinstance(blocks, list)
        assert isinstance(beams, list)

        for blk in blocks:
            assert isinstance(blk, Block)

        for beam in beams:
            assert isinstance(beam, list)
            for beam_blk in beam:
                assert isinstance(beam_blk, Block)

        self.blocks = blocks
        self.beams = beams
        self.name = name
        self.iterator = None

    def __repr__(self):
        return f"{type(self).__name__}(blocks={self.blocks}, beams={self.beams}, name={self.name})"

    def __str__(self):
        out = f"{self.name}\n"
        out += " Blocks:\n"
        for blk in self.blocks:
            out += "  - "
            out += str(blk)
            out += "\n"
        out += " Beams:\n"
        for beam in self.beams:
            out += "  - "
            pad = False
            for blk in beam:
                if pad:
                    out += "    "
                out += f" {blk}\n"
                pad = True
            out += "\n"
        return out

    def is_valid(self):
        """Check wether the current positions of blocks and beams are valid."""
        for blk in self.blocks:
            if not blk.is_valid():
                return False
        for beam in self.beams:
            for blk in beam:
                if not blk.is_valid():
                    return False
        return True

    def collides(self, other):
        """Check wether two pieces collides."""
        for blk in self.blocks:
            for o_blk in other.blocks:
                if blk.collides(o_blk):
                    return True
        beams_blks = [blk for beam in self.beams for blk in beam]
        o_beams_blks = [blk for beam in other.beams for blk in beam]
        for blk_beam in beams_blks:
            for o_blk_beam in o_beams_blks:
                if blk_beam.collides(o_blk_beam):
                    return True
        return False

    def rot90_x(self):
        """Rotation 90 degree around x axis."""
        for blk in self.blocks:
            blk.rot90_x()
        for beam in self.beams:
            for blk in beam:
                blk.rot90_x()

    def rot90_y(self):
        """Rotation 90 degree around y axis."""
        for blk in self.blocks:
            blk.rot90_y()
        for beam in self.beams:
            for blk in beam:
                blk.rot90_y()

    def rot90_z(self):
        """Rotation 90 degree around z axis."""
        for blk in self.blocks:
            blk.rot90_z()
        for beam in self.beams:
            for blk in beam:
                blk.rot90_z()

    def get_bb_vect(self):
        """Get vector to move blocks inside 5x5x5 bounding box."""
        vect = Coords3D(0, 0, 0)
        for blk in self.blocks:
            new_vect = blk.get_bb_vect()
            comb_vect = combine_bb_vects(vect, new_vect)
            vect = comb_vect

        beams_blks = [blk for beam in self.beams for blk in beam]
        for beam in beams_blks:
            new_vect = beam.get_bb_vect()
            comb_vect = combine_bb_vects(vect, new_vect)
            vect = comb_vect
        return vect

    def translate(self, vect):
        """Translate Piece with vector movement."""
        for blk in self.blocks:
            blk.pos.translate(vect)

        for beam in self.beams:
            for blk in beam:
                blk.pos.translate(vect)

    def rotate(self, rot_cnt):
        """Apply requested number of rotations on each axis."""
        for _ in range(rot_cnt[0]):
            self.rot90_x()
        for _ in range(rot_cnt[1]):
            self.rot90_y()
        for _ in range(rot_cnt[2]):
            self.rot90_z()

    def movement(self, trans, rot):
        """Apply rotation and translation."""
        self.rotate(rot)
        self.translate(trans)

    def get_movement_to_start_pos(self):
        """Get vector to move piece as close as possible to the origin."""
        blocks = self.blocks + [blk for beam in self.beams for blk in beam]
        (x, y, z) = (2000, 2000, 2000)
        for blk in blocks:
            x = min(x, blk.pos.x)
            y = min(y, blk.pos.y)
            z = min(z, blk.pos.z)
        return Coords3D(-x, -y, -z)

    def move_start_pos(self):
        """Move Piece as close as possible to the origin."""
        self.translate(self.get_movement_to_start_pos())

    def next_pos(self):
        """Update piece to next possible position."""
        if self.iterator is None:
            logging.debug("Create iterator for %s", self.name)
            self.iterator = iter(PiecePositions(self))
        next_piece = next(self.iterator)
        self.blocks = copy.deepcopy(next_piece.blocks)
        self.beams = copy.deepcopy(next_piece.beams)


class Piece:
    """Collection of Beams and Blocks."""

    def __init__(self, blocks, beams, name=None):
        assert isinstance(blocks, list)
        assert isinstance(beams, list)

        for blk in blocks:
            assert isinstance(blk, Block)

        for beam in beams:
            assert isinstance(beam, Beam)

        self.blocks = blocks
        self.beams = beams
        self.name = name

    def __repr__(self):
        return f"{type(self).__name__}(blocks={self.blocks}, beams={self.beams}, name={self.name})"

    def __str__(self):
        out = f"{self.name}\n"
        out += " Blocks:\n"
        for blk in self.blocks:
            out += "  - "
            out += str(blk)
            out += "\n"
        out += " Beams:\n"
        for beam in self.beams:
            out += "  - "
            out += str(beam)
            out += "\n"
        return out

    def to_grid_5(self):
        """Change piece to grid5"""
        beams = [beam.to_grid_5() for beam in self.beams]
        blocks = [blk.to_grid_5() for blk in self.blocks]
        return Piece5(blocks, beams, self.name)

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
        """Check whether two pieces collides."""
        collision = False
        for blk in self.blocks:
            for o_blk in other.blocks:
                collision = collision or blk.collides(o_blk)
                if collision:
                    return collision
        return collision

    def rot90_x(self):
        """Rotation 90 degrees around x axis."""
        for blk in self.blocks:
            blk.rot90_x()
        for beam in self.beams:
            beam.rot90_x()

    def rot90_y(self):
        """Rotation 90 degrees around y axis."""
        for blk in self.blocks:
            blk.rot90_y()
        for beam in self.beams:
            beam.rot90_y()

    def rot90_z(self):
        """Rotation 90 degrees around z axis."""
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


class PiecePositions:
    """Iterator for Piece Positions."""
    def __init__(self, piece):
        self.piece = copy.deepcopy(piece)
        self.offset = self.piece.get_movement_to_start_pos()
        self.rot_state = (0, 0, 0)
        self.trans_state = Coords3D(0, 0, 0)

    def __iter__(self):
        self.rot_state = (0, 0, 0)
        self.trans_state = Coords3D(0, 0, 0)
        return self

    def __str__(self):
        return f"Next rot {self.rot_state}, next trans {self.trans_state}"

    def search_next(self):
        """Search next rotation/translation state."""
        tmp = copy.deepcopy(self.piece)
        next_trans = self.trans_state
        next_rot = self.rot_state
        next_offset = self.offset

        # X translation
        next_trans = next_trans.add(Coords3D(1, 0, 0))
        tmp.movement(next_trans + next_offset, next_rot)
        if tmp.is_valid():
            return (next_offset, next_trans, next_rot)

        # Y translation
        tmp = copy.deepcopy(self.piece)
        next_trans.x = 0
        next_trans = next_trans.add(Coords3D(0, 1, 0))
        tmp.movement(next_trans + next_offset, next_rot)
        if tmp.is_valid():
            return (next_offset, next_trans, next_rot)

        # Z translation
        tmp = copy.deepcopy(self.piece)
        next_trans.y = 0
        next_trans = next_trans.add(Coords3D(0, 0, 1))
        tmp.movement(next_trans + next_offset, next_rot)
        if tmp.is_valid():
            return (next_offset, next_trans, next_rot)

        # X rotation
        tmp = copy.deepcopy(self.piece)
        next_trans.z = 0
        next_rot = (next_rot[0] + 1, next_rot[1], next_rot[2])
        tmp.rotate(next_rot)
        next_offset = tmp.get_movement_to_start_pos()
        tmp.translate(next_offset)
        if tmp.is_valid() and next_rot[0] < 4:
            return (next_offset, next_trans, next_rot)

        # Y rotation
        tmp = copy.deepcopy(self.piece)
        next_rot = (0, next_rot[1] + 1, next_rot[2])
        tmp.rotate(next_rot)
        next_offset = tmp.get_movement_to_start_pos()
        tmp.translate(next_offset)
        if tmp.is_valid() and next_rot[1] < 4:
            return (next_offset, next_trans, next_rot)

        # Z rotation
        tmp = copy.deepcopy(self.piece)
        next_rot = (next_rot[0], 0, next_rot[2] + 1)
        tmp.rotate(next_rot)
        next_offset = tmp.get_movement_to_start_pos()
        tmp.translate(next_offset)
        if tmp.is_valid() and next_rot[2] < 4:
            return (next_offset, next_trans, next_rot)

        return (None, None, None)

    def __next__(self):
        if self.trans_state is None or self.rot_state is None:
            raise StopIteration
        logging.info("%s apply rotation %s, offset %s trans %s",
                     self.piece.name, self.rot_state, self.offset, self.trans_state)
        piece = copy.deepcopy(self.piece)
        # Apply rotation and translation on piece, and update rotation and translation for next
        # iteration if rotation and translation are finished, throw StopIteration
        piece.rotate(self.rot_state)
        piece.translate(self.offset)
        piece.translate(self.trans_state)
        (self.offset, self.trans_state, self.rot_state) = self.search_next()
        return piece


def get_pieces():
    """Return list of pieces in cube puzzle."""
    pieces = []
    piece1 = Piece([Block(Coords3D(1, 0, 0)), Block(Coords3D(1, 0, 1)), Block(Coords3D(2, 0, 1))],
                   [Beam(Coords3D(0, 0, 1), Coords3D(3, 1, 0)),
                    Beam(Coords3D(1, 1, 0), Coords3D(1, 0, 3))],
                   "P1")
    pieces.append(piece1)

    piece2 = Piece([Block(Coords3D(0, 0, 0)),
                    Block(Coords3D(0, 0, 1)),
                    Block(Coords3D(2, 0, 0)),
                    Block(Coords3D(2, 0, 1)),
                   ],
                   [Beam(Coords3D(0, 0, 1), Coords3D(3, 1, 0)),
                    Beam(Coords3D(1, 0, 1), Coords3D(0, 1, 1)),
                    Beam(Coords3D(0, 1, 0), Coords3D(1, 0, 3)),
                   ],
                   "P2")
    pieces.append(piece2)

    piece3 = Piece([Block(Coords3D(1, 0, 0)),
                    Block(Coords3D(2, 1, 0)),
                    Block(Coords3D(0, 0, 2)),
                    Block(Coords3D(1, 0, 2)),
                   ],
                   [Beam(Coords3D(1, 0, 0), Coords3D(0, 1, 3)),
                    Beam(Coords3D(0, 1, 0), Coords3D(3, 0, 1)),
                   ],
                   "P3")
    pieces.append(piece3)

    piece4 = Piece([Block(Coords3D(1, 0, 0)),
                    Block(Coords3D(0, 0, 2)),
                   ],
                   [Beam(Coords3D(1, 0, 0), Coords3D(0, 1, 3)),
                    Beam(Coords3D(0, 1, 2), Coords3D(3, 0, 1)),
                   ],
                   "P4")
    pieces.append(piece4)

    piece5 = Piece([Block(Coords3D(0, 0, 0)),
                    Block(Coords3D(1, 0, 0)),
                    Block(Coords3D(2, 1, 0)),
                    Block(Coords3D(1, 0, 2)),
                   ],
                   [Beam(Coords3D(1, 0, 0), Coords3D(0, 1, 3)),
                    Beam(Coords3D(0, 1, 0), Coords3D(3, 0, 1)),
                   ],
                   "P5")
    pieces.append(piece5)

    piece6 = Piece([Block(Coords3D(0, 1, 0)),
                    Block(Coords3D(2, 1, 0)),
                    Block(Coords3D(0, 0, 1)),
                   ],
                   [Beam(Coords3D(0, 1, 0), Coords3D(3, 0, 1)),
                    Beam(Coords3D(0, 0, 1), Coords3D(1, 3, 0)),
                   ],
                   "P6")
    pieces.append(piece6)

    piece7 = Piece([Block(Coords3D(0, 0, 0)),
                    Block(Coords3D(2, 0, 0)),
                    Block(Coords3D(2, 0, 1)),
                    Block(Coords3D(2, 1, 2)),
                   ],
                   [Beam(Coords3D(0, 0, 1), Coords3D(3, 1, 0)),
                    Beam(Coords3D(2, 0, 1), Coords3D(0, 1, 1)),
                    Beam(Coords3D(2, 1, 0), Coords3D(1, 0, 3)),
                   ],
                   "P7")
    pieces.append(piece7)

    piece8 = Piece([Block(Coords3D(0, 0, 0)),
                    Block(Coords3D(0, 1, 0)),
                   ],
                   [Beam(Coords3D(1, 0, 0), Coords3D(0, 3, 1)),
                    Beam(Coords3D(0, 1, 0), Coords3D(1, 0, 3)),
                    Beam(Coords3D(0, 1, 1), Coords3D(3, 1, 0)),
                   ],
                   "P8")
    pieces.append(piece8)
    pieces5 = [p.to_grid_5() for p in pieces]
    return pieces5

def get_pieces5():
    """Get list of Pieces5"""
    p1 = Piece5(blocks=[Block(pos=Coords3D(x=2, y=0, z=0), grid_5=True),
                        Block(pos=Coords3D(x=2, y=0, z=2), grid_5=True),
                        Block(pos=Coords3D(x=4, y=0, z=2), grid_5=True)],
                beams=[[Block(pos=Coords3D(x=0, y=0, z=1), grid_5=True),
                        Block(pos=Coords3D(x=1, y=0, z=1), grid_5=True),
                        Block(pos=Coords3D(x=2, y=0, z=1), grid_5=True),
                        Block(pos=Coords3D(x=3, y=0, z=1), grid_5=True),
                        Block(pos=Coords3D(x=4, y=0, z=1), grid_5=True)],
                       [Block(pos=Coords3D(x=2, y=1, z=0), grid_5=True),
                        Block(pos=Coords3D(x=2, y=1, z=1), grid_5=True),
                        Block(pos=Coords3D(x=2, y=1, z=2), grid_5=True),
                        Block(pos=Coords3D(x=2, y=1, z=3), grid_5=True),
                        Block(pos=Coords3D(x=2, y=1, z=4), grid_5=True)]],
               name="P1")
    p2 = Piece5(blocks=[Block(pos=Coords3D(x=0, y=0, z=0), grid_5=True),
                        Block(pos=Coords3D(x=0, y=0, z=2), grid_5=True),
                        Block(pos=Coords3D(x=4, y=0, z=0), grid_5=True),
                        Block(pos=Coords3D(x=4, y=0, z=2), grid_5=True)],
                beams=[[Block(pos=Coords3D(x=0, y=0, z=1), grid_5=True),
                        Block(pos=Coords3D(x=1, y=0, z=1), grid_5=True),
                        Block(pos=Coords3D(x=2, y=0, z=1), grid_5=True),
                        Block(pos=Coords3D(x=3, y=0, z=1), grid_5=True),
                        Block(pos=Coords3D(x=4, y=0, z=1), grid_5=True)],
                       [Block(pos=Coords3D(x=1, y=0, z=1), grid_5=True)],
                       [Block(pos=Coords3D(x=0, y=1, z=0), grid_5=True),
                        Block(pos=Coords3D(x=0, y=1, z=1), grid_5=True),
                        Block(pos=Coords3D(x=0, y=1, z=2), grid_5=True),
                        Block(pos=Coords3D(x=0, y=1, z=3), grid_5=True),
                        Block(pos=Coords3D(x=0, y=1, z=4), grid_5=True)]],
                name="P2")

    p3 = Piece5(blocks=[Block(pos=Coords3D(x=2, y=0, z=0), grid_5=True),
                        Block(pos=Coords3D(x=4, y=2, z=0), grid_5=True),
                        Block(pos=Coords3D(x=0, y=0, z=4), grid_5=True),
                        Block(pos=Coords3D(x=2, y=0, z=4), grid_5=True)],
                beams=[[Block(pos=Coords3D(x=1, y=0, z=0), grid_5=True),
                        Block(pos=Coords3D(x=1, y=0, z=1), grid_5=True),
                        Block(pos=Coords3D(x=1, y=0, z=2), grid_5=True),
                        Block(pos=Coords3D(x=1, y=0, z=3), grid_5=True),
                        Block(pos=Coords3D(x=1, y=0, z=4), grid_5=True)],
                       [Block(pos=Coords3D(x=0, y=1, z=0), grid_5=True),
                        Block(pos=Coords3D(x=1, y=1, z=0), grid_5=True),
                        Block(pos=Coords3D(x=2, y=1, z=0), grid_5=True),
                        Block(pos=Coords3D(x=3, y=1, z=0), grid_5=True),
                        Block(pos=Coords3D(x=4, y=1, z=0), grid_5=True)]],
                name="P3")
    p4 = Piece5(blocks=[Block(pos=Coords3D(x=2, y=0, z=0), grid_5=True),
                        Block(pos=Coords3D(x=0, y=0, z=4), grid_5=True)],
                beams=[[Block(pos=Coords3D(x=1, y=0, z=0), grid_5=True),
                        Block(pos=Coords3D(x=1, y=0, z=1), grid_5=True),
                        Block(pos=Coords3D(x=1, y=0, z=2), grid_5=True),
                        Block(pos=Coords3D(x=1, y=0, z=3), grid_5=True),
                        Block(pos=Coords3D(x=1, y=0, z=4), grid_5=True)],
                       [Block(pos=Coords3D(x=0, y=1, z=4), grid_5=True),
                        Block(pos=Coords3D(x=1, y=1, z=4), grid_5=True),
                        Block(pos=Coords3D(x=2, y=1, z=4), grid_5=True),
                        Block(pos=Coords3D(x=3, y=1, z=4), grid_5=True),
                        Block(pos=Coords3D(x=4, y=1, z=4), grid_5=True)]],
                name="P4")
    p5 = Piece5(blocks=[Block(pos=Coords3D(x=0, y=0, z=0), grid_5=True),
                        Block(pos=Coords3D(x=2, y=0, z=0), grid_5=True),
                        Block(pos=Coords3D(x=4, y=2, z=0), grid_5=True),
                        Block(pos=Coords3D(x=2, y=0, z=4), grid_5=True)],
                beams=[[Block(pos=Coords3D(x=1, y=0, z=0), grid_5=True),
                        Block(pos=Coords3D(x=1, y=0, z=1), grid_5=True),
                        Block(pos=Coords3D(x=1, y=0, z=2), grid_5=True),
                        Block(pos=Coords3D(x=1, y=0, z=3), grid_5=True),
                        Block(pos=Coords3D(x=1, y=0, z=4), grid_5=True)],
                       [Block(pos=Coords3D(x=0, y=1, z=0), grid_5=True),
                        Block(pos=Coords3D(x=1, y=1, z=0), grid_5=True),
                        Block(pos=Coords3D(x=2, y=1, z=0), grid_5=True),
                        Block(pos=Coords3D(x=3, y=1, z=0), grid_5=True),
                        Block(pos=Coords3D(x=4, y=1, z=0), grid_5=True)]],
                name="P5")
    p6 = Piece5(blocks=[Block(pos=Coords3D(x=0, y=2, z=0), grid_5=True),
                        Block(pos=Coords3D(x=4, y=2, z=0), grid_5=True),
                        Block(pos=Coords3D(x=0, y=0, z=2), grid_5=True)],
                beams=[[Block(pos=Coords3D(x=0, y=1, z=0), grid_5=True),
                        Block(pos=Coords3D(x=1, y=1, z=0), grid_5=True),
                        Block(pos=Coords3D(x=2, y=1, z=0), grid_5=True),
                        Block(pos=Coords3D(x=3, y=1, z=0), grid_5=True),
                        Block(pos=Coords3D(x=4, y=1, z=0), grid_5=True)],
                       [Block(pos=Coords3D(x=0, y=0, z=1), grid_5=True),
                        Block(pos=Coords3D(x=0, y=1, z=1), grid_5=True),
                        Block(pos=Coords3D(x=0, y=2, z=1), grid_5=True),
                        Block(pos=Coords3D(x=0, y=3, z=1), grid_5=True),
                        Block(pos=Coords3D(x=0, y=4, z=1), grid_5=True)]],
                name="P6")
    p7 = Piece5(blocks=[Block(pos=Coords3D(x=0, y=0, z=0), grid_5=True),
                        Block(pos=Coords3D(x=4, y=0, z=0), grid_5=True),
                        Block(pos=Coords3D(x=4, y=0, z=2), grid_5=True),
                        Block(pos=Coords3D(x=4, y=2, z=4), grid_5=True)],
                beams=[[Block(pos=Coords3D(x=0, y=0, z=1), grid_5=True),
                        Block(pos=Coords3D(x=1, y=0, z=1), grid_5=True),
                        Block(pos=Coords3D(x=2, y=0, z=1), grid_5=True),
                        Block(pos=Coords3D(x=3, y=0, z=1), grid_5=True),
                        Block(pos=Coords3D(x=4, y=0, z=1), grid_5=True)],
                       [Block(pos=Coords3D(x=4, y=0, z=1), grid_5=True)],
                       [Block(pos=Coords3D(x=4, y=1, z=0), grid_5=True),
                        Block(pos=Coords3D(x=4, y=1, z=1), grid_5=True),
                        Block(pos=Coords3D(x=4, y=1, z=2), grid_5=True),
                        Block(pos=Coords3D(x=4, y=1, z=3), grid_5=True),
                        Block(pos=Coords3D(x=4, y=1, z=4), grid_5=True)]],
                name="P7")
    p8 = Piece5(blocks=[Block(pos=Coords3D(x=0, y=0, z=0), grid_5=True),
                        Block(pos=Coords3D(x=0, y=2, z=0), grid_5=True)],
                beams=[[Block(pos=Coords3D(x=1, y=0, z=0), grid_5=True),
                        Block(pos=Coords3D(x=1, y=1, z=0), grid_5=True),
                        Block(pos=Coords3D(x=1, y=2, z=0), grid_5=True),
                        Block(pos=Coords3D(x=1, y=3, z=0), grid_5=True),
                        Block(pos=Coords3D(x=1, y=4, z=0), grid_5=True)],
                       [Block(pos=Coords3D(x=0, y=1, z=0), grid_5=True),
                        Block(pos=Coords3D(x=0, y=1, z=1), grid_5=True),
                        Block(pos=Coords3D(x=0, y=1, z=2), grid_5=True),
                        Block(pos=Coords3D(x=0, y=1, z=3), grid_5=True),
                        Block(pos=Coords3D(x=0, y=1, z=4), grid_5=True)],
                       [Block(pos=Coords3D(x=0, y=2, z=1), grid_5=True),
                        Block(pos=Coords3D(x=1, y=2, z=1), grid_5=True),
                        Block(pos=Coords3D(x=2, y=2, z=1), grid_5=True),
                        Block(pos=Coords3D(x=3, y=2, z=1), grid_5=True),
                        Block(pos=Coords3D(x=4, y=2, z=1), grid_5=True)]],
                name="P8")
    return [p1, p2, p3, p4, p5, p6, p7, p8]


def main():
    """Main function."""
    logging.basicConfig(level=logging.INFO)
    pieces5 = get_pieces()
    i = 0
    for p_pos in iter(PiecePositions(pieces5[0])):
        i = i + 1
        print(p_pos)
    print(i)
    print(pieces5[0])
    while True:
        pieces5[0].next_pos()
        print(pieces5[0])

    sys.exit(0)
    for piece in pieces5:
        print(piece)
        print(f"{piece!r}")

    #for piece in pieces5:
    #    print("origin")
    #    print(piece)
    #    print("rotate")
    #    piece.rot90_x()
    #    print(piece)
    #    print("move to start pos")
    #    piece.move_start_pos()
    #    print(piece)

    #print(pieces5[0])
    #pieces5[0].next_pos()
    #print(pieces5[0])
    #pieces5[0].next_pos()
    #print(pieces5[0])
    #print("=============")
    #for piece_pos in iter(PiecePositions(pieces5[0])):
    #    print(piece_pos)




if __name__ == "__main__":
    main()
