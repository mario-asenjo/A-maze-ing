from __future__ import annotations

from mazegen.patterns import compute_pattern_closed_cells


def print_pattern(width: int, height: int) -> None:
    closed = compute_pattern_closed_cells(width, height)
    if closed is None:
        print(f"{width}x{height}: pattern does NOT fit")
        return

    for y in range(height):
        row = []
        for x in range(width):
            row.append("#" if (x, y) in closed else ".")
        print("".join(row))


if __name__ == "__main__":
    print("10x7")
    print_pattern(10, 7)
    print("\n7x5")
    print_pattern(7, 5)
    print("\n12x9")
    print_pattern(12, 9)
