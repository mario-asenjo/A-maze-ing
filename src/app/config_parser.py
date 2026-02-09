import os
from typing import TypedDict, Tuple, Set


class Config(TypedDict):
    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    output_file: str
    perfect: bool


def parse_config(path: str) -> Config:
    """
    Parse the maze configuration file.

    Raises:
        ValueError: If mandatory keys are missing or values are invalid.
        FileNotFoundError: If the config file does not exist.
    """
    raw_data: dict[str, str] = {}
    mandatory_keys: Set[str] = {
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}

    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                raise ValueError(f"Invalid format at line {line_num}: {line}")
            key, value = line.split('=', 1)
            raw_data[key.strip()] = value.strip()

        missing = mandatory_keys - set(raw_data)
        if missing:
            raise ValueError(
                f"Missing configuration keyrs: {', '.join(missing)}")

        try:
            width = int(raw_data["WIDTH"])
            height = int(raw_data["HEIGHT"])

            if width <= 0 or height <= 0:
                raise ValueError("WIDTH and HEIGHT must be positive integers.")

            def parse_coord(key: str) -> Tuple[int, int]:
                """Convert exit/entry into tuples"""
                val = raw_data[key]
                try:
                    parts = val.split(',')
                    if len(parts) != 2:
                        raise ValueError
                    return (int(parts[0]), int(parts[1]))
                except ValueError:
                    raise ValueError(f"Invalid format for {key}: '{val}' (Expected x,y)")

            entry = parse_coord("ENTRY")
            exit_coord = parse_coord("EXIT")

            perfect_str = raw_data["PERFECT"].lower()
            if perfect_str != ("true", "false"):
                raise ValueError("PERFECT needs to be 'true' or 'false'.")
            if perfect_str == "true":
                perfect = True
            else:
                perfect = False

            return {
                        "width": width,
                        "height": height,
                        "entry": entry,
                        "exit": exit_coord,
                        "output_file": raw_data["OUTPUT_FILE"],
                        "perfect": perfect
                    }

        except ValueError as e:
            raise ValueError(f"Configuration validation failed: {e}")