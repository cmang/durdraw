# Durdraw Plugin
# Type: Transform Movie
# Name: Fade In

# Durdraw plugin format version
durdraw_plugin_version = 1

durdraw_plugin = {
    "name": "Fade In",
    "author": "",
    "version": 1,
    "provides": ["transform_movie"],
    "type": ["effect"],
    "desc": "Fades in a range of frames by darkening colors toward black, without changing characters."
}

opts = {
    "start frame": 1,
    "end frame": 5,
}

# --- VGA palette for Durdraw's low-16 colors (TheDraw/Aciddraw/Pablodraw order) ---

VGA_16 = [
    (0,   0,   0  ),  #  0 Black
    (0,   0,   170),  #  1 Blue
    (0,   170, 0  ),  #  2 Green
    (0,   170, 170),  #  3 Cyan
    (170, 0,   0  ),  #  4 Red
    (170, 0,   170),  #  5 Magenta
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


def color_index_to_rgb(idx):
    """Convert a Durdraw color index to (r, g, b) 0-255."""
    if idx < 0:
        return (0, 0, 0)
    if idx < 16:
        return VGA_16[idx]
    if idx <= 231:
        i = idx - 16
        r = i // 36
        g = (i % 36) // 6
        b = i % 6
        def c(v): return 0 if v == 0 else 55 + v * 40
        return (c(r), c(g), c(b))
    # Grayscale ramp 232-255
    v = (idx - 232) * 10 + 8
    return (v, v, v)


def rgb_to_xterm256(r, g, b):
    """Find the nearest xterm-256 color index (indices 16-255) for an RGB value.
    We restrict to 16-255 so we always return a well-defined 256-color index
    that terminals can render accurately, avoiding the terminal-dependent low-16.
    """
    best_idx = 16
    best_dist = float('inf')

    # Search 6x6x6 cube (indices 16-231)
    for ri in range(6):
        rv = 0 if ri == 0 else 55 + ri * 40
        for gi in range(6):
            gv = 0 if gi == 0 else 55 + gi * 40
            for bi in range(6):
                bv = 0 if bi == 0 else 55 + bi * 40
                dist = (r - rv)**2 + (g - gv)**2 + (b - bv)**2
                if dist < best_dist:
                    best_dist = dist
                    best_idx = 16 + ri * 36 + gi * 6 + bi

    # Search grayscale ramp (indices 232-255)
    for gi in range(24):
        gv = gi * 10 + 8
        dist = (r - gv)**2 + (g - gv)**2 + (b - gv)**2
        if dist < best_dist:
            best_dist = dist
            best_idx = 232 + gi

    return best_idx


def darkened_color(color_idx, brightness):
    """
    Return an xterm-256 color index that is a darkened version of color_idx,
    scaled by brightness (0.0 = black, 1.0 = original).
    Always returns an index in the 16-255 range.
    """
    r, g, b = color_index_to_rgb(color_idx)
    r2 = int(r * brightness)
    g2 = int(g * brightness)
    b2 = int(b * brightness)
    return rgb_to_xterm256(r2, g2, b2)


def transform_movie(mov, appState=None, opts=opts):
    start = int(opts["start frame"])
    end = int(opts["end frame"])

    # Clamp to valid frame range (1-indexed from user, 0-indexed internally)
    start = max(1, min(start, mov.frameCount))
    end   = max(start, min(end, mov.frameCount))

    num_fade_frames = end - start + 1

    for i, frame_idx in enumerate(range(start - 1, end)):
        # brightness goes from near-0 (first frame) to 1.0 (last frame)
        # We use a small floor (0.02) so the first frame isn't pure black —
        # just very dark, preserving a hint of hue.
        brightness = (i + 1) / num_fade_frames

        frame = mov.frames[frame_idx]

        for y in range(mov.sizeY):
            for x in range(mov.sizeX):
                fg = frame.newColorMap[y][x][0]
                # Leave background color alone — only fade the foreground
                frame.newColorMap[y][x][0] = darkened_color(fg, brightness)

    return mov
