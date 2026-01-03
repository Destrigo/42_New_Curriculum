from config import Config
from maze_generator import MazeGenerator
from maze_types import Dir
import mlx  # type: ignore[import-untyped]


CELL_SIZE = 30
PADDING = 10
TEXT_Y_OFFSET = 15


class Visualizator():
    """Interactive maze visualization using MiniLibX graphics library.

    Provides real-time maze viewing with regeneration, path toggling, and
    color palette switching. Uses MLX for lightweight graphics without
    heavy dependencies like pygame. Includes minimum window size to ensure
    UI text remains readable on tiny mazes.
    """
    def __init__(self, config: Config) -> None:
        """Initializes visualization window and generates initial maze.

        Window size is clamped to minimum dimensions to ensure the control
        text (press 1-4) remains visible even for very small mazes. Image
        buffer is accessed directly for performance on large mazes.
        """
        self.config = config
        self.generator = MazeGenerator(config)
        self.grid = self.generator.grid
        self.output_path = self.config.output_file

        self.show_path = False
        # color palette for change color key3
        self.palette_index = 0
        self.palettes = [
            {"wall": 0x000000, "path": 0x00FF00, "bg": 0xFFFFFF},
            {"wall": 0x00FFFF, "path": 0xFFFF00, "bg": 0x000020},
            {"wall": 0xFFAA00, "path": 0x00AAFF, "bg": 0x101010},
        ]
        # init screen, if too small fixes sizes
        size_x_screen = self.config.width if self.config.width >= 15 else 16
        size_y_screen = self.config.height if self.config.height >= 15 else 12
        self.mlx_obj = mlx.Mlx()
        self.mlx = self.mlx_obj.mlx_init()
        self.win = self.mlx_obj.mlx_new_window(
            self.mlx,
            size_x_screen * CELL_SIZE + PADDING * 2,
            size_y_screen * CELL_SIZE + PADDING * 2 + 100,
            "A-Maze-ing"
        )
        self.img = self.mlx_obj.mlx_new_image(
            self.mlx,
            self.config.width * CELL_SIZE + PADDING * 2,
            self.config.height * CELL_SIZE + PADDING * 2
        )
        (self.img_data, self.bpp, self.line_size, _) = \
            self.mlx_obj.mlx_get_data_addr(self.img)
        self.mlx_obj.mlx_key_hook(self.win, self.on_key, None)
        self.mlx_obj.mlx_expose_hook(self.win, self.on_expose, None)

    def start(self) -> None:
        """Draws initial maze and starts MLX event loop.

        Event loop is blocking - control returns only when user quits.
        Initial draw ensures maze is visible before user interaction.
        """
        self.draw_maze()
        self.mlx_obj.mlx_loop(self.mlx)

    def on_expose(self, _: int) -> None:
        """Redraws image when window is exposed or uncovered.

        MLX expose events trigger when the window becomes visible after
        being hidden. Re-putting the image ensures the maze remains
        visible without maintaining a separate redraw queue.
        """
        self.mlx_obj.mlx_put_image_to_window(
            self.mlx,
            self.win,
            self.img,
            0,
            0
        )

    def fill_cell(self, x: int, y: int, color: int) -> None:
        """Fills cell interior with color, leaving 2px border for walls.

        The +2 offset and -2 size create a border where walls are drawn,
        preventing cell fills from overwriting wall pixels. This separation
        makes entry/exit/path colors clearly distinct from maze structure.
        """
        px = int(PADDING + x * CELL_SIZE) + 2
        py = int(PADDING + y * CELL_SIZE) + 2
        for dy in range(CELL_SIZE - 2):
            for dx in range(CELL_SIZE - 2):
                self.img_pixel_put(px + dx, py + dy, color)

    def draw_maze(self) -> None:
        """Renders complete maze view with walls, optional path, and controls.

        Clears background, draws all cell walls, optionally overlays solution
        path, then draws control text. Single call updates entire display,
        ensuring atomic visual updates when toggling path or changing palettes.
        """
        self.clear_image()
        color = self.palettes[self.palette_index]["wall"]
        for y in range(self.config.height):
            for x in range(self.config.width):
                self.draw_cell(x, y, color)
        if self.show_path:
            self.draw_path()
        x = 10
        y = self.config.height * CELL_SIZE + PADDING * 2
        color = 0xFFFFFF  # white

        self.draw_text_on_image(x, y + TEXT_Y_OFFSET,
                                "Press 1 - Regenerate maze", color)
        self.draw_text_on_image(x, y + TEXT_Y_OFFSET * 2,
                                "Press 2 - Show/Hide path", color)
        self.draw_text_on_image(x, y + TEXT_Y_OFFSET * 3,
                                "Press 3 - Change color palette", color)
        self.draw_text_on_image(x, y + TEXT_Y_OFFSET * 4,
                                "Press 4 - Quit", color)
        self.mlx_obj.mlx_put_image_to_window(
            self.mlx,
            self.win,
            self.img,
            0,
            0
        )

    def clear_image(self) -> None:
        """Fills entire image buffer with background color.

        Full clear (including text area) ensures no artifacts remain when
        switching palettes or regenerating mazes with different sizes.
        """
        bg = self.palettes[self.palette_index]["bg"]
        w = self.config.width * CELL_SIZE + PADDING * 2
        h_maze = self.config.height * CELL_SIZE + PADDING * 2 + 100

        for y in range(h_maze):
            for x in range(w):
                self.img_pixel_put(x, y, bg)

    def draw_text_on_image(self, x: int, y: int,
                           text: str, color: int) -> None:
        """Draws text with background rectangle for readability.

        Background ensures text remains visible regardless of palette
        colors. Without it, wall colors could make text unreadable when
        they match the underlying background in certain palettes.
        """
        # Draw a background rectangle behind text
        bg = self.palettes[self.palette_index]["bg"]
        text_width = len(text) * 8  # approx. 8 pixels per char
        text_height = TEXT_Y_OFFSET
        for dy in range(text_height):
            for dx in range(text_width):
                self.img_pixel_put(x + dx, y + dy, bg)
        # Draw the string on top
        self.mlx_obj.mlx_string_put(self.mlx, self.win, x, y, color, text)

    def win_pixel_put(self, x: int, y: int, color: int) -> None:
        """Put a pixel directly on the window (not on the image)."""
        # Check bounds
        if x < 0 or y < 0:
            return
        if x >= self.config.width * CELL_SIZE + PADDING * 2:
            return
        if y >= self.config.height * CELL_SIZE + PADDING * 2 + 100:
            return

        self.mlx_obj.mlx_pixel_put(self.mlx, self.win, x, y, color)

    def img_pixel_put(self, x: int, y: int, color: int) -> None:
        """Directly manipulates image buffer for performance.

        Bypasses MLX's higher-level pixel functions to avoid per-pixel
        function call overhead. Essential for smooth rendering when drawing
        thousands of pixels in large mazes (a 50x50 maze draws 75,000+ pixels
        for walls alone). Manual RGB byte packing handles different bit depths.
        """
        if x < 0 or y < 0:
            return
        if x >= self.config.width * CELL_SIZE + PADDING * 2:
            return
        if y >= self.config.height * CELL_SIZE + PADDING * 2:
            return

        offset = y * self.line_size + x * (self.bpp // 8)

        self.img_data[offset + 0] = color & 0xFF
        self.img_data[offset + 1] = (color >> 8) & 0xFF
        self.img_data[offset + 2] = (color >> 16) & 0xFF
        if self.bpp == 32:
            self.img_data[offset + 3] = 0xFF

    def draw_cell(self, x: int, y: int, color: int) -> None:
        """Draws cell walls and fills special cells (entry/exit/42 pattern).

        Entry gets light green, exit light red, fully-walled cells (42 pattern)
        get magenta. These colors provide visual landmarks independent of the
        current palette, helping users orient themselves in the maze.
        """
        cell = self.grid[y][x]
        px = PADDING + x * CELL_SIZE
        py = PADDING + y * CELL_SIZE

        # fill entry
        entry_x, entry_y = self.config.entry
        self.fill_cell(entry_x, entry_y, 0xCCFFCC)
        # Fill exit cell with light red
        exit_x, exit_y = self.config.exit
        self.fill_cell(exit_x, exit_y, 0xFFCCCC)
        # fill 42
        if (
            (cell & Dir.NORTH)
            and (cell & Dir.SOUTH)
            and (cell & Dir.EAST)
            and (cell & Dir.WEST)
        ):
            self.fill_cell(x, y, 0xFF00FF)
        if cell & Dir.NORTH:
            self.hline(px, py, CELL_SIZE, color)
        if cell & Dir.SOUTH:
            self.hline(px, py + CELL_SIZE, CELL_SIZE, color)
        if cell & Dir.WEST:
            self.vline(px, py, CELL_SIZE, color)
        if cell & Dir.EAST:
            self.vline(px + CELL_SIZE, py, CELL_SIZE, color)

    def hline(self, x: int, y: int, length: int, color: int) -> None:
        """Draws horizontal wall line using direct pixel manipulation."""
        for i in range(length):
            self.img_pixel_put(x + i, y, color)

    def vline(self, x: int, y: int, length: int, color: int) -> None:
        """Draws vertical wall line using direct pixel manipulation."""
        for i in range(length):
            self.img_pixel_put(x, y + i, color)

    def on_key(self, keycode: int, _: int) -> None:
        """Handles keyboard input for maze controls.

        Keys 1-4 provide core functionality: regenerate (testing different
        seeds), toggle solution (verify solvability), change palette (visual
        preference), and quit. Numeric keys were chosen for simplicity and
        clear on-screen labeling.
        """
        if keycode == 49:  # key number 1
            self.grid = self.generator.algo.generate()
            self.draw_maze()
            self.mlx_obj.mlx_put_image_to_window(self.mlx,
                                                 self.win, self.img, 0, 0)

        elif keycode == 50:  # key number 2
            self.show_path = not self.show_path
            self.draw_maze()
            self.mlx_obj.mlx_put_image_to_window(self.mlx,
                                                 self.win, self.img, 0, 0)

        elif keycode == 51:  # key number 3
            self.palette_index = (self.palette_index + 1) % len(self.palettes)
            self.draw_maze()
            self.mlx_obj.mlx_put_image_to_window(self.mlx,
                                                 self.win, self.img, 0, 0)

        elif keycode == 52:  # key number 4
            self.mlx_obj.mlx_loop_exit(self.mlx)

    def draw_path(self) -> None:
        """Reads solution path from output file and visualizes it.

        Reads from file instead of using solver directly to verify the
        output file format is correct. This catches bugs in the output
        writer that might not be caught if solver was called directly.
        Simulates movement through maze by updating (x, y) coordinates.
        """
        try:
            with open(self.output_path, "r") as f:
                lines = [line.strip() for line in f if line.strip()]
        except OSError:
            raise OSError
        # path is last line of file
        path = (lines[-1])[:-1]

        color = self.palettes[self.palette_index]["path"]
        (x, y) = self.config.entry
        for step in path:
            if step == 'N':
                y -= 1
            elif step == 'S':
                y += 1
            elif step == 'E':
                x += 1
            elif step == 'W':
                x -= 1
            self.fill_cell(x, y, color)
