#!/usr/bin/env python3
"""Handle Pieces, blocks and beams"""
import logging
import copy
import sys
import numpy as np
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
        self.compute_np()
        if not self.is_valid():
            logging.warning("Invalid position %s", self)

    def __repr__(self):
        out = f"{type(self).__name__}(pos={self.pos!r}"
        out += ")"
        return out


    def __str__(self):
        return f"block at {self.pos}"

    def is_valid(self):
        """Check wether the block is in a valid position."""
        bb_start = Coords3D(0, 0, 0)
        bb_end = Coords3D(4, 4, 4)
        return self.is_within(bb_start, bb_end)

    def is_within(self, start, end):
        """Check piece is inside bounding box."""
        return self.pos.is_within(start, end)

    def is_odd(self):
        """True when x,y,z are even"""
        return (self.pos.x % 2) and (self.pos.y % 2) and (self.pos.z % 2)

    def collides(self, other):
        """Check wether two blocks collides"""
        blks_union = self.np_pos & other.np_pos
        return not np.amax(blks_union) == 0

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
        bb_len = 5
        return self.pos.get_bb_vect(bb_len)

    def compute_np(self, dim=5):
        """Compute numpy array to represent piece and check collision."""
        self.np_pos = np.zeros((dim, dim, dim), dtype=int)
        self.np_pos[self.pos.x, self.pos.y, self.pos.z] = 1


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
        self.np_blbe = None
        self.umount_trans_history = []
        self.trans_hist_archive = []
        self.compute_np()

    def __repr__(self):
        repr_str = f"{type(self).__name__}(blocks={self.blocks}, "
        repr_str += f"beams={self.beams}, name='{self.name}')"
        return repr_str

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
                out += f" beam-{blk}\n"
                pad = True
            out += "\n"
        return out

    def add_trans_history(self, trans):
        self.umount_trans_history.append(trans)

    def get_last_trans(self):
        if len(self.umount_trans_history):
            return self.umount_trans_history[-1]
        return None

    def archive_history(self):
        self.trans_hist_archive.append(copy.deepcopy(self.umount_trans_history))
        self.umount_trans_history.clear()

    def is_valid(self):
        """Check wether the current positions of blocks and beams are valid."""
        for blk in self.blocks:
            if not blk.is_valid() or blk.is_odd():
                return False

        for beam in self.beams:
            for blk in beam:
                if not blk.is_valid():
                    return False
        return True

    def is_within(self, start, end):
        """Check wether piece is inside bounding box."""
        for blk in self.blocks:
            if not blk.is_within(start, end):
                return False
        for beam in self.beams:
            for blk in beam:
                if not blk.is_within(start, end):
                    return False
        return True


    def collides(self, other):
        """Check wether two pieces collides."""
        blks_union = self.np_blbe & other.np_blbe
        return not np.amax(blks_union) == 0

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
        offset = Coords3D(-x, -y, -z)
        coord_blk0 = copy.deepcopy(self.blocks[0].pos)
        fix_offset = Coords3D(0, 0, 0)
        new_blk0 = coord_blk0 + offset
        if new_blk0.x % 2:
            fix_offset.x = 1
        if new_blk0.y % 2:
            fix_offset.y = 1
        if new_blk0.z % 2:
            fix_offset.z = 1
        return offset + fix_offset

    def move_start_pos(self):
        """Move Piece as close as possible to the origin."""
        self.translate(self.get_movement_to_start_pos())

    def reset(self):
        """Reset positions iterator."""
        assert self.iterator is not None
        self.iterator.reset()
        self.next_pos()

    def next_pos(self):
        """Update piece to next possible position."""
        if self.iterator is None:
            logging.info("Create iterator for %s", self.name)
            self.iterator = iter(PiecePositions(self))
        next_piece = next(self.iterator)
        self.blocks = next_piece.blocks
        self.beams = next_piece.beams
        self.np_blbe = next_piece.np_blbe

    def compute_np(self, dim=5):
        """Compute numpy array to rerpesent piece and check collision."""
        self.np_blbe = np.zeros((dim, dim, dim), dtype=int)
        for blk in self.blocks:
            blk.compute_np(dim)
            self.np_blbe += blk.np_pos
        for beam in self.beams:
            for blk in beam:
                blk.compute_np(dim)
                self.np_blbe += blk.np_pos


class PiecePositions:
    """Iterator for Piece Positions."""
    def __init__(self, piece):
        logging.debug("%s PiecePositions Constructor", piece.name)
        self.piece = copy.deepcopy(piece)
        movement = (self.piece.get_movement_to_start_pos(), Coords3D(0, 0, 0), (0, 0, 0))
        movements = [movement]
        while movement is not None:
            (offset, trans, rot) = movement
            movement = self.search_next(offset, trans, rot)
            if movement is None:
                break
            movements.append(movement)
        self.positions = []
        for m in movements:
            p = copy.deepcopy(self.piece)
            p.movement(m[0] + m[1], m[2])
            p.compute_np()
            self.positions.append(p)
        self.current_position = 0

    def __iter__(self):
        self.current_position = 0
        return self

    def __str__(self):
        return f"movement {self.current_position}"

    def reset(self):
        """Reset iterator."""
        self.current_position = 0

    def search_next(self, offset, trans, rot):
        """Search next rotation/translation state."""
        tmp = copy.deepcopy(self.piece)
        next_offset = offset
        next_trans = trans
        next_rot = rot

        # X translation
        next_trans = next_trans.add(Coords3D(2, 0, 0))
        tmp.movement(next_trans + next_offset, next_rot)
        if tmp.is_valid():
            return (next_offset, next_trans, next_rot)

        # Y translation
        tmp = copy.deepcopy(self.piece)
        next_trans.x = 0
        next_trans = next_trans.add(Coords3D(0, 2, 0))
        tmp.movement(next_trans + next_offset, next_rot)
        if tmp.is_valid():
            return (next_offset, next_trans, next_rot)

        # Z translation
        tmp = copy.deepcopy(self.piece)
        next_trans.y = 0
        next_trans = next_trans.add(Coords3D(0, 0, 2))
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

        return None

    def __next__(self):
        if self.current_position >= len(self.positions):
            raise StopIteration
        self.current_position = self.current_position + 1
        return self.positions[self.current_position - 1]


def get_pieces5():
    """Get list of Pieces5"""
    p0 = Piece5(blocks=[Block(pos=Coords3D(x=2, y=0, z=0)),
                        Block(pos=Coords3D(x=2, y=0, z=2)),
                        Block(pos=Coords3D(x=4, y=0, z=2))],
                beams=[[Block(pos=Coords3D(x=0, y=0, z=1)),
                        Block(pos=Coords3D(x=1, y=0, z=1)),
                        Block(pos=Coords3D(x=2, y=0, z=1)),
                        Block(pos=Coords3D(x=3, y=0, z=1)),
                        Block(pos=Coords3D(x=4, y=0, z=1))],
                       [Block(pos=Coords3D(x=2, y=1, z=0)),
                        Block(pos=Coords3D(x=2, y=1, z=1)),
                        Block(pos=Coords3D(x=2, y=1, z=2)),
                        Block(pos=Coords3D(x=2, y=1, z=3)),
                        Block(pos=Coords3D(x=2, y=1, z=4))]],
                name="P0")
    p1 = Piece5(blocks=[Block(pos=Coords3D(x=0, y=0, z=0)),
                        Block(pos=Coords3D(x=0, y=0, z=2)),
                        Block(pos=Coords3D(x=4, y=0, z=0)),
                        Block(pos=Coords3D(x=4, y=0, z=2))],
                beams=[[Block(pos=Coords3D(x=0, y=0, z=1)),
                        Block(pos=Coords3D(x=1, y=0, z=1)),
                        Block(pos=Coords3D(x=2, y=0, z=1)),
                        Block(pos=Coords3D(x=3, y=0, z=1)),
                        Block(pos=Coords3D(x=4, y=0, z=1))],
                       [Block(pos=Coords3D(x=1, y=0, z=2))],
                       [Block(pos=Coords3D(x=0, y=1, z=0)),
                        Block(pos=Coords3D(x=0, y=1, z=1)),
                        Block(pos=Coords3D(x=0, y=1, z=2)),
                        Block(pos=Coords3D(x=0, y=1, z=3)),
                        Block(pos=Coords3D(x=0, y=1, z=4))]],
                name="P1")

    p2 = Piece5(blocks=[Block(pos=Coords3D(x=2, y=0, z=0)),
                        Block(pos=Coords3D(x=4, y=2, z=0)),
                        Block(pos=Coords3D(x=0, y=0, z=4)),
                        Block(pos=Coords3D(x=2, y=0, z=4))],
                beams=[[Block(pos=Coords3D(x=1, y=0, z=0)),
                        Block(pos=Coords3D(x=1, y=0, z=1)),
                        Block(pos=Coords3D(x=1, y=0, z=2)),
                        Block(pos=Coords3D(x=1, y=0, z=3)),
                        Block(pos=Coords3D(x=1, y=0, z=4))],
                       [Block(pos=Coords3D(x=0, y=1, z=0)),
                        Block(pos=Coords3D(x=1, y=1, z=0)),
                        Block(pos=Coords3D(x=2, y=1, z=0)),
                        Block(pos=Coords3D(x=3, y=1, z=0)),
                        Block(pos=Coords3D(x=4, y=1, z=0))]],
                name="P2")
    p3 = Piece5(blocks=[Block(pos=Coords3D(x=2, y=0, z=0)),
                        Block(pos=Coords3D(x=0, y=0, z=4))],
                beams=[[Block(pos=Coords3D(x=1, y=0, z=0)),
                        Block(pos=Coords3D(x=1, y=0, z=1)),
                        Block(pos=Coords3D(x=1, y=0, z=2)),
                        Block(pos=Coords3D(x=1, y=0, z=3)),
                        Block(pos=Coords3D(x=1, y=0, z=4))],
                       [Block(pos=Coords3D(x=0, y=1, z=4)),
                        Block(pos=Coords3D(x=1, y=1, z=4)),
                        Block(pos=Coords3D(x=2, y=1, z=4)),
                        Block(pos=Coords3D(x=3, y=1, z=4)),
                        Block(pos=Coords3D(x=4, y=1, z=4))]],
                name="P3")
    p4 = Piece5(blocks=[Block(pos=Coords3D(x=0, y=0, z=0)),
                        Block(pos=Coords3D(x=2, y=0, z=0)),
                        Block(pos=Coords3D(x=4, y=2, z=0)),
                        Block(pos=Coords3D(x=2, y=0, z=4))],
                beams=[[Block(pos=Coords3D(x=1, y=0, z=0)),
                        Block(pos=Coords3D(x=1, y=0, z=1)),
                        Block(pos=Coords3D(x=1, y=0, z=2)),
                        Block(pos=Coords3D(x=1, y=0, z=3)),
                        Block(pos=Coords3D(x=1, y=0, z=4))],
                       [Block(pos=Coords3D(x=0, y=1, z=0)),
                        Block(pos=Coords3D(x=1, y=1, z=0)),
                        Block(pos=Coords3D(x=2, y=1, z=0)),
                        Block(pos=Coords3D(x=3, y=1, z=0)),
                        Block(pos=Coords3D(x=4, y=1, z=0))]],
                name="P4")
    p5 = Piece5(blocks=[Block(pos=Coords3D(x=0, y=2, z=0)),
                        Block(pos=Coords3D(x=4, y=2, z=0)),
                        Block(pos=Coords3D(x=0, y=0, z=2))],
                beams=[[Block(pos=Coords3D(x=0, y=1, z=0)),
                        Block(pos=Coords3D(x=1, y=1, z=0)),
                        Block(pos=Coords3D(x=2, y=1, z=0)),
                        Block(pos=Coords3D(x=3, y=1, z=0)),
                        Block(pos=Coords3D(x=4, y=1, z=0))],
                       [Block(pos=Coords3D(x=0, y=0, z=1)),
                        Block(pos=Coords3D(x=0, y=1, z=1)),
                        Block(pos=Coords3D(x=0, y=2, z=1)),
                        Block(pos=Coords3D(x=0, y=3, z=1)),
                        Block(pos=Coords3D(x=0, y=4, z=1))]],
                name="P5")
    p6 = Piece5(blocks=[Block(pos=Coords3D(x=0, y=0, z=0)),
                        Block(pos=Coords3D(x=4, y=0, z=0)),
                        Block(pos=Coords3D(x=4, y=0, z=2)),
                        Block(pos=Coords3D(x=4, y=2, z=4))],
                beams=[[Block(pos=Coords3D(x=0, y=0, z=1)),
                        Block(pos=Coords3D(x=1, y=0, z=1)),
                        Block(pos=Coords3D(x=2, y=0, z=1)),
                        Block(pos=Coords3D(x=3, y=0, z=1)),
                        Block(pos=Coords3D(x=4, y=0, z=1))],
                       [Block(pos=Coords3D(x=3, y=0, z=2))],
                       [Block(pos=Coords3D(x=4, y=1, z=0)),
                        Block(pos=Coords3D(x=4, y=1, z=1)),
                        Block(pos=Coords3D(x=4, y=1, z=2)),
                        Block(pos=Coords3D(x=4, y=1, z=3)),
                        Block(pos=Coords3D(x=4, y=1, z=4))]],
                name="P6")
    p7 = Piece5(blocks=[Block(pos=Coords3D(x=0, y=0, z=0)),
                        Block(pos=Coords3D(x=0, y=2, z=0))],
                beams=[[Block(pos=Coords3D(x=1, y=0, z=0)),
                        Block(pos=Coords3D(x=1, y=1, z=0)),
                        Block(pos=Coords3D(x=1, y=2, z=0)),
                        Block(pos=Coords3D(x=1, y=3, z=0)),
                        Block(pos=Coords3D(x=1, y=4, z=0))],
                       [Block(pos=Coords3D(x=0, y=1, z=0)),
                        Block(pos=Coords3D(x=0, y=1, z=1)),
                        Block(pos=Coords3D(x=0, y=1, z=2)),
                        Block(pos=Coords3D(x=0, y=1, z=3)),
                        Block(pos=Coords3D(x=0, y=1, z=4))],
                       [Block(pos=Coords3D(x=0, y=2, z=1)),
                        Block(pos=Coords3D(x=1, y=2, z=1)),
                        Block(pos=Coords3D(x=2, y=2, z=1)),
                        Block(pos=Coords3D(x=3, y=2, z=1)),
                        Block(pos=Coords3D(x=4, y=2, z=1))]],
                name="P7")
    return [p0, p1, p2, p3, p4, p5, p6, p7]


def get_result():
    """Get pieces of puzzle in their final position."""
    p7 = Piece5(blocks=[Block(pos=Coords3D(x=0, y=0, z=0)),
                        Block(pos=Coords3D(x=0, y=2, z=0))],
                beams=[[Block(pos=Coords3D(x=1, y=0, z=0)),
                        Block(pos=Coords3D(x=1, y=1, z=0)),
                        Block(pos=Coords3D(x=1, y=2, z=0)),
                        Block(pos=Coords3D(x=1, y=3, z=0)),
                        Block(pos=Coords3D(x=1, y=4, z=0))],
                       [Block(pos=Coords3D(x=0, y=1, z=0)),
                        Block(pos=Coords3D(x=0, y=1, z=1)),
                        Block(pos=Coords3D(x=0, y=1, z=2)),
                        Block(pos=Coords3D(x=0, y=1, z=3)),
                        Block(pos=Coords3D(x=0, y=1, z=4))],
                       [Block(pos=Coords3D(x=0, y=2, z=1)),
                        Block(pos=Coords3D(x=1, y=2, z=1)),
                        Block(pos=Coords3D(x=2, y=2, z=1)),
                        Block(pos=Coords3D(x=3, y=2, z=1)),
                        Block(pos=Coords3D(x=4, y=2, z=1))]],
                name='P7')
    p6 = Piece5(blocks=[Block(pos=Coords3D(x=4, y=4, z=0)),
                        Block(pos=Coords3D(x=4, y=0, z=0)),
                        Block(pos=Coords3D(x=2, y=0, z=0)),
                        Block(pos=Coords3D(x=0, y=0, z=2))],
                beams=[[Block(pos=Coords3D(x=3, y=4, z=0)),
                        Block(pos=Coords3D(x=3, y=3, z=0)),
                        Block(pos=Coords3D(x=3, y=2, z=0)),
                        Block(pos=Coords3D(x=3, y=1, z=0)),
                        Block(pos=Coords3D(x=3, y=0, z=0))],
                       [Block(pos=Coords3D(x=2, y=1, z=0))],
                       [Block(pos=Coords3D(x=4, y=0, z=1)),
                        Block(pos=Coords3D(x=3, y=0, z=1)),
                        Block(pos=Coords3D(x=2, y=0, z=1)),
                        Block(pos=Coords3D(x=1, y=0, z=1)),
                        Block(pos=Coords3D(x=0, y=0, z=1))]],
                name='P6')
    p5 = Piece5(blocks=[Block(pos=Coords3D(x=2, y=4, z=2)),
                        Block(pos=Coords3D(x=2, y=0, z=2)),
                        Block(pos=Coords3D(x=0, y=4, z=4))],
                beams=[[Block(pos=Coords3D(x=1, y=4, z=2)),
                        Block(pos=Coords3D(x=1, y=3, z=2)),
                        Block(pos=Coords3D(x=1, y=2, z=2)),
                        Block(pos=Coords3D(x=1, y=1, z=2)),
                        Block(pos=Coords3D(x=1, y=0, z=2))],
                       [Block(pos=Coords3D(x=0, y=4, z=3)),
                        Block(pos=Coords3D(x=1, y=4, z=3)),
                        Block(pos=Coords3D(x=2, y=4, z=3)),
                        Block(pos=Coords3D(x=3, y=4, z=3)),
                        Block(pos=Coords3D(x=4, y=4, z=3))]],
                name='P5')
    p4 = Piece5(blocks=[Block(pos=Coords3D(x=0, y=4, z=0)),
                        Block(pos=Coords3D(x=0, y=4, z=2)),
                        Block(pos=Coords3D(x=0, y=2, z=4)),
                        Block(pos=Coords3D(x=4, y=4, z=2))],
                beams=[[Block(pos=Coords3D(x=0, y=4, z=1)),
                        Block(pos=Coords3D(x=1, y=4, z=1)),
                        Block(pos=Coords3D(x=2, y=4, z=1)),
                        Block(pos=Coords3D(x=3, y=4, z=1)),
                        Block(pos=Coords3D(x=4, y=4, z=1))],
                       [Block(pos=Coords3D(x=0, y=3, z=0)),
                        Block(pos=Coords3D(x=0, y=3, z=1)),
                        Block(pos=Coords3D(x=0, y=3, z=2)),
                        Block(pos=Coords3D(x=0, y=3, z=3)),
                        Block(pos=Coords3D(x=0, y=3, z=4))]],
                name='P4')
    p3 = Piece5(blocks=[Block(pos=Coords3D(x=0, y=2, z=2)),
                        Block(pos=Coords3D(x=4, y=2, z=4))],
                beams=[[Block(pos=Coords3D(x=0, y=2, z=3)),
                        Block(pos=Coords3D(x=1, y=2, z=3)),
                        Block(pos=Coords3D(x=2, y=2, z=3)),
                        Block(pos=Coords3D(x=3, y=2, z=3)),
                        Block(pos=Coords3D(x=4, y=2, z=3))],
                       [Block(pos=Coords3D(x=4, y=3, z=4)),
                        Block(pos=Coords3D(x=4, y=3, z=3)),
                        Block(pos=Coords3D(x=4, y=3, z=2)),
                        Block(pos=Coords3D(x=4, y=3, z=1)),
                        Block(pos=Coords3D(x=4, y=3, z=0))]],
                name='P3')
    p2 = Piece5(blocks=[Block(pos=Coords3D(x=2, y=2, z=4)),
                        Block(pos=Coords3D(x=0, y=0, z=4)),
                        Block(pos=Coords3D(x=2, y=4, z=0)),
                        Block(pos=Coords3D(x=2, y=2, z=0))],
                beams=[[Block(pos=Coords3D(x=2, y=3, z=4)),
                        Block(pos=Coords3D(x=2, y=3, z=3)),
                        Block(pos=Coords3D(x=2, y=3, z=2)),
                        Block(pos=Coords3D(x=2, y=3, z=1)),
                        Block(pos=Coords3D(x=2, y=3, z=0))],
                       [Block(pos=Coords3D(x=1, y=4, z=4)),
                        Block(pos=Coords3D(x=1, y=3, z=4)),
                        Block(pos=Coords3D(x=1, y=2, z=4)),
                        Block(pos=Coords3D(x=1, y=1, z=4)),
                        Block(pos=Coords3D(x=1, y=0, z=4))]],
                name='P2')
    p1 = Piece5(blocks=[Block(pos=Coords3D(x=4, y=0, z=4)),
                        Block(pos=Coords3D(x=2, y=0, z=4)),
                        Block(pos=Coords3D(x=4, y=4, z=4)),
                        Block(pos=Coords3D(x=2, y=4, z=4))],
                beams=[[Block(pos=Coords3D(x=3, y=0, z=4)),
                        Block(pos=Coords3D(x=3, y=1, z=4)),
                        Block(pos=Coords3D(x=3, y=2, z=4)),
                        Block(pos=Coords3D(x=3, y=3, z=4)),
                        Block(pos=Coords3D(x=3, y=4, z=4))],
                       [Block(pos=Coords3D(x=2, y=1, z=4))],
                       [Block(pos=Coords3D(x=4, y=0, z=3)),
                        Block(pos=Coords3D(x=3, y=0, z=3)),
                        Block(pos=Coords3D(x=2, y=0, z=3)),
                        Block(pos=Coords3D(x=1, y=0, z=3)),
                        Block(pos=Coords3D(x=0, y=0, z=3))]],
                name='P1')
    p0 = Piece5(blocks=[Block(pos=Coords3D(x=4, y=0, z=2)),
                        Block(pos=Coords3D(x=4, y=2, z=2)),
                        Block(pos=Coords3D(x=4, y=2, z=0))],
                beams=[[Block(pos=Coords3D(x=4, y=1, z=4)),
                        Block(pos=Coords3D(x=4, y=1, z=3)),
                        Block(pos=Coords3D(x=4, y=1, z=2)),
                        Block(pos=Coords3D(x=4, y=1, z=1)),
                        Block(pos=Coords3D(x=4, y=1, z=0))],
                       [Block(pos=Coords3D(x=3, y=0, z=2)),
                        Block(pos=Coords3D(x=3, y=1, z=2)),
                        Block(pos=Coords3D(x=3, y=2, z=2)),
                        Block(pos=Coords3D(x=3, y=3, z=2)),
                        Block(pos=Coords3D(x=3, y=4, z=2))]],
                name='P0')
    return [p0, p1, p2, p3, p4, p5, p6, p7]




def main():
    """Main function."""
    logging.basicConfig(level=logging.INFO)

    sys.exit(0)


if __name__ == "__main__":
    main()
