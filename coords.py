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
