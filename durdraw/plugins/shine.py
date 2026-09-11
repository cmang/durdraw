# Durdraw Plugin
# Type: Transform Movie
# Name: Shine

import math

# Durdraw plugin format version
durdraw_plugin_version = 1

durdraw_plugin = {
    "name": "Shine",
    "author": "",
    "version": 1,
    "provides": ["transform_movie"],
    "type": ["effect"],
    "desc": ("Sweeps a diagonal glimmer/highlight across the frame range, "
             "brightening the foreground color of every cell (including "
             "blanks) as the band passes over it, then fading back to the "
             "original color.")
}

opts = {
    "start frame":    1,      # First frame to affect (1-indexed)
    "end frame":      0,      # Last frame to affect (0 = last frame of movie)

    "brightness":     0.8,    # Peak brighten amount, 0.0 (no change) to 1.0 (blows out to white)
    "band width":     6,      # Width in columns of the glimmer band (horizontal falloff)
    "diagonal shift": 1,      # Columns the band shifts left per row (creates the diagonal angle)
    "travel margin":  10,     # Extra columns the band travels off-screen at each end, so the sweep eases in/out
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
    """Convert a Durdraw color index (low-16 or 256) to (r, g, b) 0-255."""
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
    v = (idx - 232) * 10 + 8
    return (v, v, v)


def rgb_to_low16(r, g, b):
    """Find the nearest Durdraw low-16 color index for an RGB value."""
    best_idx = 0
    best_dist = float('inf')
    for idx, (vr, vg, vb) in enumerate(VGA_16):
        dist = (r - vr) ** 2 + (g - vg) ** 2 + (b - vb) ** 2
        if dist < best_dist:
            best_dist = dist
            best_idx = idx
    return best_idx


def rgb_to_xterm256(r, g, b):
    """Find the nearest xterm-256 color index (indices 16-255) for an RGB value."""
    best_idx = 16
    best_dist = float('inf')

    for ri in range(6):
        rv = 0 if ri == 0 else 55 + ri * 40
        for gi in range(6):
            gv = 0 if gi == 0 else 55 + gi * 40
            for bi in range(6):
                bv = 0 if bi == 0 else 55 + bi * 40
                dist = (r - rv) ** 2 + (g - gv) ** 2 + (b - bv) ** 2
                if dist < best_dist:
                    best_dist = dist
                    best_idx = 16 + ri * 36 + gi * 6 + bi

    for gi in range(24):
        gv = gi * 10 + 8
        dist = (r - gv) ** 2 + (g - gv) ** 2 + (b - gv) ** 2
        if dist < best_dist:
            best_dist = dist
            best_idx = 232 + gi

    return best_idx


def brighten(color_idx, amount, color_mode):
    """Blend a color toward white by `amount` (0.0-1.0), remapped to a valid index."""
    if amount <= 0:
        return color_idx

    r, g, b = color_index_to_rgb(color_idx)
    r2 = int(r + (255 - r) * amount)
    g2 = int(g + (255 - g) * amount)
    b2 = int(b + (255 - b) * amount)

    if color_mode == "256":
        return rgb_to_xterm256(r2, g2, b2)
    else:
        return rgb_to_low16(r2, g2, b2)


def transform_movie(mov, appState=None, opts=opts):
    start = int(opts["start frame"])
    end = int(opts["end frame"])
    if end <= 0:
        end = mov.frameCount

    start = max(1, min(start, mov.frameCount))
    end   = max(start, min(end, mov.frameCount))

    brightness      = opts["brightness"]
    band_width      = max(1, int(opts["band width"]))
    diagonal_shift  = opts["diagonal shift"]
    travel_margin   = int(opts["travel margin"])

    color_mode = appState.colorMode if appState else "16"

    num_frames = end - start + 1

    # Total distance the band needs to travel so that it starts fully
    # off-screen to the left (even accounting for the diagonal shift on
    # the bottom-most row) and ends fully off-screen to the right.
    max_row_shift = diagonal_shift * (mov.sizeY - 1)
    sweep_start = -band_width - travel_margin - max_row_shift
    sweep_end   = mov.sizeX + band_width + travel_margin

    for i, frame_idx in enumerate(range(start - 1, end)):
        frame = mov.frames[frame_idx]

        # Progress 0.0 (first frame) -> 1.0 (last frame)
        progress = i / max(num_frames - 1, 1)
        band_center_row0 = sweep_start + (sweep_end - sweep_start) * progress

        for y in range(mov.sizeY):
            # Each row's band shifts further left, creating the diagonal angle
            row_center = band_center_row0 - diagonal_shift * y

            for x in range(mov.sizeX):
                dist = x - row_center
                if abs(dist) >= band_width:
                    continue  # outside the glimmer band, leave color untouched

                # Triangular falloff: 1.0 at the center of the band, 0.0 at its edges
                falloff = 1.0 - (abs(dist) / band_width)

                fg = frame.colorMap[y][x][0]
                frame.colorMap[y][x][0] = brighten(fg, falloff * brightness, color_mode)

    return mov
