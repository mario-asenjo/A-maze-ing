import ctypes
import os
from typing import Any, Optional


class MLXWrapper:
    """
    Professional ctypes wrapper for MiniLibX on Linux.
    Ensures zero tracebacks by validating library loading.
    """
    def __init__(self, lib_path: str = "./minilibx/libmlx.so") -> None:
        if not os.path.exists(lib_path):
            raise RuntimeError(f"MLX binary not found at {lib_path}")

        self.lib = ctypes.CDLL(lib_path)

        # Define Return/Arg types for strict validation
        self.lib.mlx_init.restype = ctypes.c_void_p

        self.lib.mlx_new_window.argtypes = [
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_char_p
        ]
        self.lib.mlx_new_window.restype = ctypes.c_void_p

        self.lib.mlx_clear_window.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.lib.mlx_clear_window.restype = ctypes.c_int

        self.lib.mlx_destroy_window.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p]

        self.lib.mlx_destroy_display.argtypes = [ctypes.c_void_p]

        # mlx_key_hook(void *win_ptr, int (*funct_ptr)(), void *param)
        self.lib.mlx_key_hook.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
        ]
        self.lib.mlx_key_hook.restype = ctypes.c_int

        self.lib.mlx_hook.argtypes = [
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
            ctypes.c_void_p, ctypes.c_void_p]
        self.lib.mlx_hook.restype = ctypes.c_int

        self.lib.mlx_loop.argtypes = [ctypes.c_void_p]
        self.lib.mlx_loop.restype = ctypes.c_int
        self.lib.mlx_pixel_put.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.lib.mlx_pixel_put.restype = ctypes.c_int

        self.lib.mlx_string_put.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_char_p]
        self.lib.mlx_string_put.restype = ctypes.c_int

    def init(self) -> Optional[Any]:
        """Initialize the MLX connection."""
        return self.lib.mlx_init()

    def new_window(
        self, mlx_ptr: Any, width: int, height: int, title: str
    ) -> Any:
        """Create a new graphical window."""
        # title.encode is required for c_char_p
        return self.lib.mlx_new_window(
            mlx_ptr, width, height, title.encode('utf-8')
        )
