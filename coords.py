"""Handle coordinates."""


class Coords3D:
    """Handle 3D coordinates."""

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


    def add(self, other):
        """Adds two instance of Coords3D together.

        Usually this is used to add two vectors, or a position and a vector.
        """
        assert isinstance(other, type(self))
        return Coords3D(self.x + other.x, self.y + other.y, self.z + other.z)

    __add__ = add

    def __mul__(self, other):
        """Multiply coord with scalar."""
        return Coords3D(self.x * other, self.y * other, self.z * other)

    def __neg__(self):
        """Return negative coord (opposite relative to (0, 0, 0))."""
        return Coords3D(-self.x, -self.y, -self.z)

    def is_within(self, start, end):
        """Check wether a coordinate is inside a bounding box (inclusive)."""
        return (((self.x >= start.x) and (self.x <= end.x))
                and ((self.y >= start.y) and (self.y <= end.y))
                and ((self.z >= start.z) and (self.z <= end.z)))

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

    def __repr__(self):
        return f"{type(self).__name__}(x={self.x}, y={self.y}, z={self.z})"

    def __eq__(self, other):
        assert isinstance(other, type(self))
        return self.x == other.x and self.y == other.y and self.z == other.z

    def get_direction(self):
        """Return unary vector direction, must be along an axis !"""
        if self.x > 0:
            dir_x = 1
        elif self.x < 0:
            dir_x = -1
        else:
            dir_x = 0
        if self.y > 0:
            assert dir_x == 0
            dir_y = 1
        elif self.y < 0:
            assert dir_x == 0
            dir_y = -1
        else:
            dir_y = 0
        if self.z > 0:
            assert dir_x == 0
            assert dir_y == 0
            dir_z = 1
        elif self.z < 0:
            dir_z = -1
            assert dir_x == 0
            assert dir_y == 0
        else:
            dir_z = 0
        return Coords3D(dir_x, dir_y, dir_z)

    def rot90_x(self):
        """Rotation 90 degree around x axis."""
        x = self.x
        y = self.y
        z = self.z
        self.x = x
        self.y = -z
        self.z = y

    def rot90_y(self):
        """Rotation 90 degree around y axis."""
        x = self.x
        y = self.y
        z = self.z
        self.x = z
        self.y = y
        self.z = -x

    def rot90_z(self):
        """Rotation 90 degree around z axis."""
        x = self.x
        y = self.y
        z = self.z
        self.x = -y
        self.y = x
        self.z = z

    def translate(self, vect):
        """Translation from vect."""
        assert isinstance(vect, type(self))
        self.x += vect.x
        self.y += vect.y
        self.z += vect.z

    def get_bb_vect(self, bb_len=3):
        """Return vector to move coord inside square bounding box of side bb_len."""
        coords = [self.x, self.y, self.z]
        vect = []
        for scalar in coords:
            if scalar < 0:
                vect.append(-scalar)
            elif scalar >= bb_len:
                vect.append(bb_len - scalar)
            else:
                vect.append(0)
        return Coords3D(vect[0], vect[1], vect[2])
