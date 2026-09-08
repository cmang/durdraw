# Durdraw Plugin
# Type: Transform Movie
# Name: Sixel Preview

import sys
import os
import curses
import select

# Durdraw plugin format version
durdraw_plugin_version = 1

durdraw_plugin = {
    "name": "Sixel Preview",
    "author": "",
    "version": 1,
    "provides": ["transform_movie"],
    "type": "menu_item",
    "shortcut": "p",
    "location": "Menu",
    "desc": "Renders current frame as a pixel-accurate Sixel thumbnail (~1 char = 1 pixel). Like VGA preview in Pablodraw/Moebius."
}

opts = {
    'scale': 2,   # Pixel width per character cell. Height is scale*2 to match terminal char aspect ratio.
}

# --- xterm-256 color index to RGB (0-255) ---

def color_index_to_rgb(idx):
    """Convert Durdraw color index to (r, g, b) 0-255.

    Durdraw's first 16 colors follow the TheDraw/Aciddraw/Pablodraw/VGA
    convention (same order as CGA/EGA hardware):
      0  Black         1  Blue          2  Green         3  Cyan
      4  Red           5  Magenta       6  Brown         7  Light Grey
      8  Dark Grey     9  Light Blue   10  Light Green  11  Light Cyan
     12  Light Red    13  Light Magenta 14  Yellow       15  White
    Colors 16+ follow the standard xterm-256 palette.
    """
    if idx < 0:
        return (0, 0, 0)
    if idx < 16:
        # VGA hardware palette (same values used by DOS ANSI art editors)
        vga = [
            (0,   0,   0  ),  #  0 Black
            (0,   0,   170),  #  1 Blue
            (0,   170, 0  ),  #  2 Green
            (0,   170, 170),  #  3 Cyan
            (170, 0,   0  ),  #  4 Red
            (170, 0,   170),  #  5 Magenta / Purple
            (170, 85,  0  ),  #  6 Brown
            (170, 170, 170),  #  7 Light Grey
            (85,  85,  85 ),  #  8 Dark Grey
            (85,  85,  255),  #  9 Light Blue
            (85,  255, 85 ),  # 10 Light Green
            (85,  255, 255),  # 11 Light Cyan
            (255, 85,  85 ),  # 12 Light Red
            (255, 85,  255),  # 13 Light Magenta
            (255, 255, 85 ),  # 14 Yellow
            (255, 255, 255),  # 15 White
        ]
        return vga[idx]
    if idx <= 231:
        # 6x6x6 color cube
        idx -= 16
        b = idx % 6
        g = (idx // 6) % 6
        r = idx // 36
        def c(v): return 0 if v == 0 else 55 + v * 40
        return (c(r), c(g), c(b))
    # Grayscale ramp 232-255
    v = (idx - 232) * 10 + 8
    return (v, v, v)


# --- Sixel detection ---

def detect_sixel_support():
    return True

def detect_sixel_support_broken():
    """
    Send DA1 (Device Attributes) query and check if terminal reports sixel support.
    Returns True if sixels are supported, False otherwise.
    Times out quickly so we don't hang on non-responsive terminals.
    """
    if not sys.stdout.isatty():
        return False
    try:
        # Save terminal state, switch to raw mode
        import termios, tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        tty.setraw(fd)
        try:
            # Send DA1 query
            sys.stdout.write("\x1b[c")
            sys.stdout.flush()
            # Wait up to 0.5s for a response
            ready, _, _ = select.select([sys.stdin], [], [], 0.5)
            if not ready:
                return False
            response = ""
            while True:
                ready, _, _ = select.select([sys.stdin], [], [], 0.1)
                if not ready:
                    break
                ch = sys.stdin.read(1)
                response += ch
                if ch == 'c':
                    break
            # Sixel support is indicated by '4' in the parameter list
            # e.g. \x1b[?64;4;... or \x1b[?4; ...
            return ';4;' in response or ';4c' in response or '?4;' in response or '?4c' in response
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except Exception:
        return False


# --- Sixel rendering ---

def render_sixel(frame, scale=3, color_mode="256"):
    """
    Render frame as a sixel image.
    Each character cell becomes (scale) pixels wide and (scale*2) pixels tall,
    approximating the ~2:1 height:width aspect ratio of a terminal character cell.
    Uses a 256-entry palette, one entry per xterm color index.
    """
    cell_w = max(1, scale)
    cell_h = max(1, scale * 2)

    src_w = frame.sizeX
    src_h = frame.sizeY
    img_w = src_w * cell_w
    img_h = src_h * cell_h

    # Build source color grid: src_pixels[y][x] = (top_rgb, bottom_rgb)
    # Each character cell is treated as 2 vertically-stacked sub-pixels so
    # that upper/lower half-block characters can show two distinct colors
    # instead of a single blended one.
    src_pixels = []
    for y in range(src_h):
        row = []
        for x in range(src_w):
            char = frame.content[y][x]
            fg_idx = frame.newColorMap[y][x][0]
            bg_idx = frame.newColorMap[y][x][1]
            #if color_mode == "256":
            #    if fg_idx < 8:
            #        fg_idx += 1
            if color_mode == "16":
                fg_idx -= 1
                # bg_idx -= 1

            fg = color_index_to_rgb(fg_idx)
            bg = color_index_to_rgb(bg_idx)

            if char in (' ', '', None):
                # Blank cell - both sub-pixels are background color
                top, bottom = bg, bg
            elif char == '█':
                # Full block - both sub-pixels are foreground color
                top, bottom = fg, fg
            elif char == '▀':
                # Upper half block - top sub-pixel is fg, bottom is bg
                top, bottom = fg, bg
            elif char == '▄':
                # Lower half block - top sub-pixel is bg, bottom is fg
                top, bottom = bg, fg
            elif char == '▓':
                blended = blend(fg, bg, 0.75)
                top, bottom = blended, blended
            elif char in ['▒', '▌', '▐']:
                blended = blend(fg, bg, 0.50)
                top, bottom = blended, blended
            elif char == '░':
                blended = blend(fg, bg, 0.25)
                top, bottom = blended, blended
            else:
                # Solid non-block character - treat as solid fg color
                top, bottom = fg, fg

            row.append((top, bottom))
        src_pixels.append(row)

    # Scale up: pixels[py][px] maps back to src_pixels[py//cell_h][px//cell_w],
    # picking the top or bottom sub-pixel color depending on which half of
    # the cell height py falls into.
    def get_pixel(px, py):
        sx = min(px // cell_w, src_w - 1)
        sy = min(py // cell_h, src_h - 1)
        local_y = py % cell_h
        top, bottom = src_pixels[sy][sx]
        return top if local_y < (cell_h // 2) else bottom

    w, h = img_w, img_h

    # Build palette: collect all unique colors, map to sixel palette entries
    unique_colors = {}
    palette_id = 0
    for py in range(h):
        for px in range(w):
            rgb = get_pixel(px, py)
            if rgb not in unique_colors:
                if palette_id < 256:
                    unique_colors[rgb] = palette_id
                    palette_id += 1

    out = []
    # Sixel header: DCS intro, pixel aspect ratio 1:1, canvas size
    out.append(f"\x1bPq\"1;1;{w};{h}")

    # Register palette entries
    for rgb, pid in unique_colors.items():
        r, g, b = rgb
        # Sixel uses 0-100 percentage RGB
        rp = int(r * 100 / 255)
        gp = int(g * 100 / 255)
        bp = int(b * 100 / 255)
        out.append(f"#{pid};2;{rp};{gp};{bp}")

    # Emit pixel data in bands of 6 rows
    for band_start in range(0, h, 6):
        band_end = min(band_start + 6, h)

        # Group columns by color within this band to use RLE efficiently
        # For each palette entry, emit a full-width sixel row
        # Strategy: collect sixel chars per palette entry, emit only non-empty ones
        band_data = {}  # pid -> list of sixel chars across width

        for x in range(w):
            # For each x, gather which pids are set in which bits
            bit_map = {}  # pid -> six_bits
            for bit, y in enumerate(range(band_start, band_end)):
                rgb = get_pixel(x, y)
                pid = unique_colors.get(rgb)
                if pid is None:
                    pid = nearest_color(rgb, unique_colors)
                if pid not in bit_map:
                    bit_map[pid] = 0
                bit_map[pid] |= (1 << bit)

            # Fill in zeros for pids not present at this x
            for pid in band_data:
                if pid not in bit_map:
                    band_data[pid].append(63)  # '?' = 0 bits = transparent

            for pid, bits in bit_map.items():
                if pid not in band_data:
                    # Backfill with zeroes for columns we skipped
                    band_data[pid] = [63] * x
                band_data[pid].append(63 + bits)

        # Emit each pid's row
        first = True
        for pid, sixel_chars in band_data.items():
            if all(c == 63 for c in sixel_chars):
                continue  # Skip entirely transparent rows
            # RLE compress
            rle = rle_encode(sixel_chars)
            if not first:
                out.append("$")  # CR - return to start of band
            out.append(f"#{pid}")
            out.append(rle)
            first = False

        out.append("-")  # New sixel line (advance 6 pixels down)

    out.append("\x1b\\")  # String Terminator
    return "".join(out)


def blend(fg, bg, alpha):
    """Blend fg over bg with alpha 0..1."""
    return tuple(int(fg[i] * alpha + bg[i] * (1 - alpha)) for i in range(3))


def nearest_color(rgb, palette):
    """Find nearest palette entry by Euclidean distance."""
    best_pid = 0
    best_dist = float('inf')
    r, g, b = rgb
    for (pr, pg, pb), pid in palette.items():
        d = (r-pr)**2 + (g-pg)**2 + (b-pb)**2
        if d < best_dist:
            best_dist = d
            best_pid = pid
    return best_pid


def rle_encode(sixel_chars):
    """Run-length encode a list of sixel char codes into sixel RLE string."""
    if not sixel_chars:
        return ""
    out = []
    count = 1
    cur = sixel_chars[0]
    for c in sixel_chars[1:]:
        if c == cur:
            count += 1
        else:
            if count > 3:
                out.append(f"!{count}{chr(cur)}")
            else:
                out.append(chr(cur) * count)
            cur = c
            count = 1
    if count > 3:
        out.append(f"!{count}{chr(cur)}")
    else:
        out.append(chr(cur) * count)
    return "".join(out)


# --- Plugin entry point ---

def transform_movie(mov, appState=None, opts=opts):
    if not mov.frames:
        return mov

    frame = mov.currentFrame

    # Suspend ncurses (same pattern as jump_to_shell)
    curses.def_prog_mode()
    curses.endwin()

    try:
        print("\033[2J\033[H", end="", flush=True)  # Clear screen

        if not detect_sixel_support():
            print("Sixel graphics are not supported by your terminal.")
            print("Try a Sixel-capable terminal such as xterm -ti vt340, mlterm, WezTerm, or iTerm2.")
        else:
            sixel_data = render_sixel(frame, scale=opts.get('scale', 3), color_mode=appState.colorMode)
            sys.stdout.write(sixel_data)
            sys.stdout.flush()
            print()  # newline after image

        # print("\nPress Enter to return to Durdraw...")
        input()

    except Exception as e:
        print(f"\nSixel preview error: {e}")
        input("Press Enter to return...")

    finally:
        print("\033[2J\033[H", end="", flush=True)
        curses.reset_prog_mode()

    return mov
