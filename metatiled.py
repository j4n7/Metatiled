import os
import shutil
import colorsys
import argparse
from PIL import Image, ImageOps, ImageDraw


# COLOR -----------------------------------------------------------------------

palettes = {
    "morn": {
        "GRAY": [(28, 31, 16), (21, 21, 21), (13, 13, 13), (7, 7, 7)],
        "RED": [(28, 31, 16), (31, 19, 24), (30, 10, 6), (7, 7, 7)],
        "GREEN": [(22, 31, 10), (12, 25, 1), (5, 14, 0), (7, 7, 7)],
        "WATER": [(23, 23, 31), (18, 19, 31), (13, 12, 31), (7, 7, 7)],
        "YELLOW": [(28, 31, 16), (31, 31, 7), (31, 16, 1), (7, 7, 7)],
        "BROWN": [(28, 31, 16), (24, 18, 7), (20, 15, 3), (7, 7, 7)],
        "ROOF": [(28, 31, 16), (15, 31, 31), (5, 17, 31), (7, 7, 7)],
        "TEXT": [(31, 31, 16), (31, 31, 16), (14, 9, 0), (0, 0, 0)]
    },
    "day": {
        "GRAY": [(27, 31, 27), (21, 21, 21), (13, 13, 13), (7, 7, 7)],
        "RED": [(27, 31, 27), (31, 19, 24), (30, 10, 6), (7, 7, 7)],
        "GREEN": [(22, 31, 10), (12, 25, 1), (5, 14, 0), (7, 7, 7)],
        "WATER": [(23, 23, 31), (18, 19, 31), (13, 12, 31), (7, 7, 7)],
        "YELLOW": [(27, 31, 27), (31, 31, 7), (31, 16, 1), (7, 7, 7)],
        "BROWN": [(27, 31, 27), (24, 18, 7), (20, 15, 3), (7, 7, 7)],
        "ROOF": [(27, 31, 27), (15, 31, 31), (5, 17, 31), (7, 7, 7)],
        "TEXT": [(31, 31, 16), (31, 31, 16), (14, 9, 0), (0, 0, 0)]
    },
    "nite": {
        "GRAY": [(15, 14, 24), (11, 11, 19), (7, 7, 12), (0, 0, 0)],
        "RED": [(15, 14, 24), (14, 7, 17), (13, 0, 8), (0, 0, 0)],
        "GREEN": [(15, 14, 24), (8, 13, 19), (0, 11, 13), (0, 0, 0)],
        "WATER": [(15, 13, 27), (10, 9, 20), (4, 3, 18), (0, 0, 0)],
        "YELLOW": [(30, 30, 11), (16, 14, 18), (16, 14, 10), (0, 0, 0)],
        "BROWN": [(15, 14, 24), (12, 9, 15), (8, 4, 5), (0, 0, 0)],
        "ROOF": [(15, 14, 24), (13, 12, 23), (11, 9, 20), (0, 0, 0)],
        "TEXT": [(31, 31, 16), (31, 31, 16), (14, 9, 0), (0, 0, 0)]
    },
    "dark": {
        "GRAY": [(1, 1, 2), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
        "RED": [(1, 1, 2), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
        "GREEN": [(1, 1, 2), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
        "WATER": [(1, 1, 2), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
        "YELLOW": [(30, 30, 11), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
        "BROWN": [(1, 1, 2), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
        "ROOF": [(1, 1, 2), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
        "TEXT": [(31, 31, 16), (31, 31, 16), (14, 9, 0), (0, 0, 0)]
    },
    "indoor": {
        "GRAY": [(30, 28, 26), (19, 19, 19), (13, 13, 13), (7, 7, 7)],
        "RED": [(30, 28, 26), (31, 19, 24), (30, 10, 6), (7, 7, 7)],
        "GREEN": [(18, 24, 9), (15, 20, 1), (9, 13, 0), (7, 7, 7)],
        "WATER": [(30, 28, 26), (15, 16, 31), (9, 9, 31), (7, 7, 7)],
        "YELLOW": [(30, 28, 26), (31, 31, 7), (31, 16, 1), (7, 7, 7)],
        "BROWN": [(26, 24, 17), (21, 17, 7), (16, 13, 3), (7, 7, 7)],
        "ROOF": [(30, 28, 26), (17, 19, 31), (14, 16, 31), (7, 7, 7)],
        "TEXT": [(31, 31, 16), (31, 31, 16), (14, 9, 0), (0, 0, 0)]
    }
}


def is_same_tone(tile_tone, palette_tone, tolerance=1):
    match = all([abs(tile_tone[i] - palette_tone[i])
                <= tolerance for i in range(3)])
    return match


def is_same_color(tile_tones, palette_tones):
    match = all([any(is_same_tone(tile_tone, palette_tone)
                for palette_tone in palette_tones) for tile_tone in tile_tones])
    return match


def convert_to_5bit_rgb(color):
    return tuple((c * 31) // 255 for c in color)


def convert_to_8bit_rgb(color):
    return tuple((c * 255) // 31 for c in color)


def rgb_to_hex(rgb):
    return ''.join(f'{value:02X}' for value in rgb)


def hex_to_rgb(hex_color):
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def palettes_to_8bit_rgb(palettes):
    palettes_8bit = {
        palette_name: {
            color_name: [convert_to_8bit_rgb(c) for c in tones]
            for color_name, tones in colors.items()
        }
        for palette_name, colors in palettes.items()
    }
    return palettes_8bit


def sort_color(tones):
    '''Sort using luminance formula'''
    return sorted(tones, key=lambda c: (
        0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]), reverse=True)


def is_tile_white(tile):
    white_pixel = (255, 255, 255)
    for pixel in tile.getdata():
        if pixel != white_pixel:
            return False
    return True


def tile_to_grayscale(tile, color_to_grays):
    grayscale = {
        0: (255, 255, 255),
        1: (170, 170, 170),
        2: (85, 85, 85),
        3: (0, 0, 0)
    }
    grays = {gray: grayscale[position]
             for gray, position in color_to_grays.items()}
    new_tile = Image.new('RGB', (8, 8))
    for y in range(8):
        for x in range(8):
            pixel = tile.getpixel((x, y))
            new_tile.putpixel(
                (x, y), grays.get(pixel, (255, 255, 255)))
    return new_tile


def tile_to_color(tile, color_to_grays):
    grayscale = {
        (255, 255, 255): 0,
        (170, 170, 170): 1,
        (85, 85, 85): 2,
        (0, 0, 0): 3
    }

    color_tile = Image.new('RGB', (8, 8))
    for y in range(8):
        for x in range(8):
            gray_pixel = tile.getpixel((x, y))
            gray_index = grayscale.get(gray_pixel, 0)
            tone = next(key for key, value in color_to_grays.items()
                        if value == gray_index)
            color_tile.putpixel((x, y), tone)
    return color_tile


def get_tile_tones(tile):
    tile_tones = set(tile.getpixel((i % 8, i // 8)) for i in range(64))
    tile_tones = sort_color(tile_tones)
    return tile_tones


def process_partial_colors(lst):
    lst_sorted = sorted(lst, key=len, reverse=True)
    unique_list = []
    for sublist in lst_sorted:
        sublist_set = set(sublist)
        if not any(sublist_set.issubset(set(existing_sublist)) for existing_sublist in unique_list):
            unique_list.append(sublist)
    return unique_list


def identify_palette(tile_color_tones, palettes):
    palette_scores = {palette_name: 0 for palette_name in palettes}

    for tile_tones in tile_color_tones:
        for palette_name, colors in palettes.items():
            for color_name, palette_tones in colors.items():
                if is_same_color(tile_tones, palette_tones):
                    palette_scores[palette_name] += 1
                    break

    total_score = sum(palette_scores.values())
    if total_score == 0:
        print('Palette: monochrome')
        return 'monochrome'

    palette_name = max(palette_scores, key=palette_scores.get)
    print(f'Palette: {palette_name}')

    return palette_name


def get_roof_colors(unique_tiles, palette):
    '''For monochrome maps and roof tiles.'''

    if not palette.get('ROOF'):
        return

    def is_roof(tile_tones, palette):
        for color_name, palette_tones in palette.items():
            if all(any(is_same_tone(tile_tone, palette_tone) for palette_tone in palette_tones) for tile_tone in tile_tones):
                return False
        return True

    roof_tones = []
    for tile in unique_tiles:
        tile_tones = set(tile.getpixel((i % 8, i // 8)) for i in range(64))
        tile_tones = sort_color(tile_tones)
        if is_roof(tile_tones, palette):
            roof_tones.append(tile_tones)

    palette['ROOF'] = process_partial_colors(roof_tones)[0] if process_partial_colors(
        roof_tones) else palette['ROOF']


def get_tile_palette_color(tile_tones, palette):
    matching_positions = {}

    for color_name, palette_tones in palette.items():
        positions = {}
        match = True
        for i, tile_tone in enumerate(tile_tones):
            found = False
            for j, palette_tone in enumerate(palette_tones):
                if is_same_tone(tile_tone, palette_tone):
                    positions[tile_tone] = j
                    found = True
                    break
            if not found:
                match = False
                break
        if match:
            matching_positions[color_name] = positions

    color_name = next(iter(matching_positions))
    return color_name, matching_positions[color_name]


def load_info(image_path):
    txt_path = image_path.replace('.png', '.txt')
    if not os.path.exists(txt_path):
        return None

    with open(txt_path, 'r') as f:
        lines = f.read().strip().split('\n')

    custom_palette = {}
    collision_colors = {}
    in_palette_section = False
    in_collision_section = False
    current_color_name = None

    for line in lines:
        line = line.strip()
        if line == '[PALETTE]':
            in_palette_section = True
            in_collision_section = False
            print('Custom palette found!')
            continue
        elif line == '[COLLISIONS]':
            in_palette_section = False
            in_collision_section = True
            if os.path.exists(image_path.replace('.png', '_coll.png')):
                print('Collision info and mask found!')
            continue

        if in_palette_section:
            if line and not line.startswith('['):
                if len(line) == 6 and all(c in '0123456789ABCDEFabcdef' for c in line):
                    if current_color_name:
                        custom_palette[current_color_name].append(
                            hex_to_rgb(line))
                else:
                    current_color_name = line
                    custom_palette[current_color_name] = []

        if in_collision_section:
            if line and not line.startswith('['):
                parts = line.split(',')
                if len(parts) == 2:
                    collision_name = parts[0].strip()
                    collision_color = f'#{parts[1].strip()}'
                    collision_colors[collision_color] = collision_name

    return custom_palette, collision_colors


# ANALYZE ---------------------------------------------------------------------


def get_palette_color(tile, palette_colors):
    '''Used when you don't know the name of the color'''
    def fits_color(tile, color):
        unique_tones = {tile.getpixel((x, y))
                        for x in range(8) for y in range(8)}
        return len(unique_tones) <= 4 and all(tone in color for tone in unique_tones)

    for index, color in enumerate(palette_colors):
        if fits_color(tile, color):
            return index, color
    return None, None


def generate_distinct_colors(n):
    colors = []
    for i in range(n):
        hue = i / n
        lightness = 0.5
        saturation = 0.9
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        colors.append(tuple(int(c * 255) for c in rgb))
    return colors


def analyze(image_path):
    image = Image.open(image_path)
    width, height = image.size

    if width % 32 != 0 or height % 32 != 0:
        raise ValueError("Image dimensions must be multiples of 32")

    tiles = []
    for y in range(0, height, 8):
        for x in range(0, width, 8):
            tile = image.crop((x, y, x + 8, y + 8))
            tiles.append((x, y, tile))

    tile_color_tones = []
    wrong_tiles = 0
    for _, _, tile in tiles:
        tile_tones = get_tile_tones(tile)
        if len(tile_tones) <= 4:
            tile_color_tones.append(tile_tones)
        else:
            wrong_tiles += 1
    palette_colors = process_partial_colors(tile_color_tones)

    print("Colors found:", len(palette_colors),
          "(> 7)" if len(palette_colors) > 7 else "")
    print("Tiles with more than 4 tones:", wrong_tiles)
    if len(palette_colors) <= 7 and wrong_tiles == 0:
        print("The palette is valid!")
    else:
        print("The palette is invalid! The output image will help you fix the errors.")

    mode = "fill"
    output_image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(output_image)
    display_colors = generate_distinct_colors(len(palette_colors))

    for x, y, tile in tiles:
        color_index, color = get_palette_color(tile, palette_colors)
        if (color_index, color) != (None, None):
            sorted_color = sort_color(color)
            for i, tone in enumerate(sorted_color):
                for dx in range(4):
                    for dy in range(4):
                        tile.putpixel((4*(i % 2) + dx, 4*(i//2) + dy), tone)
            if len(sorted_color) < 4:
                missing_index = len(sorted_color)
                for dx in range(4):
                    for dy in range(4):
                        tile.putpixel((4*(missing_index % 2) + dx,
                                       4*(missing_index//2) + dy), (0, 255, 0))
        output_image.paste(tile, (x, y))
        if (color_index, color) != (None, None):
            if mode == "fill":
                draw.rectangle([x, y, x + 8, y + 8],
                               fill=display_colors[color_index])
            else:
                center_x = x + 3
                center_y = y + 3
                draw.rectangle([center_x, center_y, center_x + 1,
                               center_y + 1], fill=display_colors[color_index])
        draw.rectangle([x, y, x + 7, y + 7], outline=(0, 0, 0))

    output_image.save(image_path.replace(".png", "_analysis.png"))


# PROCESS ---------------------------------------------------------------------


def divide_into_metatiles(image):
    width, height = image.size
    metatiles = []
    positions = []
    for y in range(0, height, 32):
        for x in range(0, width, 32):
            metatile = image.crop((x, y, x + 32, y + 32))
            metatiles.append(metatile)
            positions.append((x // 32 + 1, y // 32 + 1))
    return metatiles, positions


def identify_unique_metatiles(metatiles, positions, darkest_tone):
    unique_metatiles = []
    metatile_positions = []
    metatile_indexes = []

    border_metatile = Image.new('RGB', (32, 32), color=darkest_tone)
    unique_metatiles.append(border_metatile)
    metatile_positions.append((0, 0))

    for i, metatile in enumerate(metatiles):
        if metatile not in unique_metatiles:
            unique_metatiles.append(metatile)
            metatile_positions.append(positions[i])
        metatile_indexes.append(unique_metatiles.index(metatile))
    print('Unique metatiles:', len(unique_metatiles))
    return unique_metatiles, metatile_positions, metatile_indexes


def identify_unique_tiles(unique_metatiles, metatile_positions, palettes, palette=None):
    monocrhome = False
    unique_tiles = []
    tile_color_tones = []
    tile_color_names = []
    color_to_grays = []

    for i, metatile in enumerate(unique_metatiles):
        for y in range(0, 32, 8):
            for x in range(0, 32, 8):
                tile = metatile.crop((x, y, x + 8, y + 8))
                if tile not in unique_tiles:
                    unique_tiles.append(tile)
                    tile_tones = get_tile_tones(tile)
                    if len(tile_tones) > 4:
                        raise SystemExit(
                            f'[Error] Tile ({x // 8 + 1}, {y // 8 + 1}) in metatile {metatile_positions[i]} has more than 4 colors. Analyze the map first.')
                    if tile_tones not in tile_color_tones:
                        tile_color_tones.append(tile_tones)

    print(f'Unique tiles: {len(unique_tiles)}',
          '(> 192)' if len(unique_tiles) > 192 else '')

    palette_colors = process_partial_colors(tile_color_tones)

    if palette == 'extract':
        if len(palette_colors) > 7:
            raise SystemExit(
                f'[Error] {len(palette_colors)} colors found. Limit is 7. Analyze the map first.')
        print(f'Unique colors: {len(palette_colors)}')
        return palette_colors, None, None, None

    if not palette:
        print(f'Unique colors: {len(palette_colors)}')

        palette_name = identify_palette(palette_colors, palettes)
        if palette_name == 'monochrome':
            monocrhome = True
            palette_name = 'morn'
        palette = palettes[palette_name]

    get_roof_colors(unique_tiles, palette)

    for tile in unique_tiles:
        tile_tones = get_tile_tones(tile)
        color, positions = get_tile_palette_color(tile_tones, palette)
        tile_color_names.append(color)
        color_to_grays.append(positions)
        # print(color, positions)

    # ? Tile $7F (128) is reserved for the space character
    if len(unique_tiles) > 192:
        space_tile = Image.new('RGB', (8, 8), color=(0, 255, 255))
        unique_tiles.insert(127, space_tile)
        tile_color_names.insert(127, 'TEXT')
        color_to_grays.insert(127, {(0, 255, 255): 0})

    return unique_tiles, tile_color_names, color_to_grays, monocrhome


def compress_tiles(tiles, tile_color_names, color_to_grays):
    compressed_tiles = []
    transformations = []

    for i, tile in enumerate(tiles):
        # ? Tile $7F (128) is reserved for the space character
        if len(tiles) <= 192 or (len(tiles) > 192 and i != 127):
            gray_tile = tile_to_grayscale(tile, color_to_grays[i])
            color = tile_color_names[i]
            variants = {
                'original': gray_tile,
                'flip_x': ImageOps.mirror(gray_tile),
                'flip_y': ImageOps.flip(gray_tile),
                'flip_xy': ImageOps.flip(ImageOps.mirror(gray_tile))
            }

            found = False
            for variant_name, variant_tile in variants.items():
                for j, comp_tile in enumerate(compressed_tiles):
                    if variant_tile.tobytes() == comp_tile.tobytes():
                        flip_x = 'flip_x' in variant_name or 'flip_xy' in variant_name
                        flip_y = 'flip_y' in variant_name or 'flip_xy' in variant_name
                        transformations.append((j, flip_x, flip_y, color))

                        # Reapply transformations to original tile
                        retransformed_tile = reapply_transformations(
                            comp_tile, flip_x, flip_y, color_to_grays[i])

                        # Debugging
                        # tile.save(f"debug/{i}_original_tile.png")
                        # gray_tile.save(f"debug/{i}_gray_tile.png")
                        # retransformed_tile.save(f"debug/{i}_retransformed_tile_{variant_name}.png")

                        assert retransformed_tile.tobytes() == tile.tobytes(), \
                            f"Transformation error: tile {i}, variant {variant_name}, flip_x={flip_x}, flip_y={flip_y}, color={color}"

                        found = True
                        break
                if found:
                    break

            if not found:
                compressed_tiles.append(gray_tile)
                transformations.append(
                    (len(compressed_tiles) - 1, False, False, color))

    # ? It seems Polished crystal always uses tile $7F for the space character
    if len(compressed_tiles) > 127:
        space_tile = Image.new('RGB', (8, 8), color=(0, 255, 255))
        compressed_tiles.insert(127, space_tile)

        # Adjust indices in transformations
        for idx, (j, flip_x, flip_y, color) in enumerate(transformations):
            if j >= 127:
                transformations[idx] = (j + 1, flip_x, flip_y, color)

    print(
        f'Compressed tiles: {len(tiles)} to {len(compressed_tiles)} ({len(tiles) - len(compressed_tiles)})')

    return compressed_tiles, transformations


def reapply_transformations(tile, flip_x, flip_y, color_to_grays):
    if flip_x:
        tile = ImageOps.mirror(tile)
    if flip_y:
        tile = ImageOps.flip(tile)
    recolored_tile = tile_to_color(tile, color_to_grays)
    return recolored_tile


def get_attr_metatiles(metatiles, compressed_tiles, transformations, color_to_grays):
    if len(color_to_grays) > 192:
        del color_to_grays[127]

    attr_metatiles = []

    for metatile in metatiles:
        metatile_info = []
        for y in range(0, 32, 8):
            for x in range(0, 32, 8):
                tile = metatile.crop((x, y, x + 8, y + 8))
                for i, (compressed_index, flip_x, flip_y, color) in enumerate(transformations):
                    retransformed_tile = reapply_transformations(
                        compressed_tiles[compressed_index], flip_x, flip_y, color_to_grays[i])
                    if tile.tobytes() == retransformed_tile.tobytes():
                        metatile_info.append(
                            (compressed_index, color, flip_x, flip_y))
                        break
        attr_metatiles.append(metatile_info)

    return attr_metatiles


# MERGE -----------------------------------------------------------------------


def read_bin_file(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
        return [list(content[i:i+16]) for i in range(0, len(content), 16)]


def process_tileset(image_path):
    tileset_image = Image.open(image_path).convert("RGB")
    width, height = tileset_image.size

    tiles = []

    for y in range(0, height, 8):
        for x in range(0, width, 8):
            tile = tileset_image.crop((x, y, x + 8, y + 8))

            if is_tile_white(tile):
                # Check if last tile is white
                if x + 8 >= width and y + 8 >= height:
                    # ! Fringe case: last tile is really white
                    break

                # Check if next tile is white
                next_x = x + 8
                next_y = y
                if next_x >= width:
                    next_x = 0
                    next_y = y + 8

                if next_y < height:
                    next_tile = tileset_image.crop(
                        (next_x, next_y, next_x + 8, next_y + 8))
                    if is_tile_white(next_tile):
                        break

            tiles.append(tile)

    return tiles


def merge_maps(map_dir, base_tileset_index, metatiles_index_mappings, ablk=False):
    map_files = os.listdir(map_dir)
    base_map_file = os.path.join(map_dir, map_files[base_tileset_index])

    base_map = read_bin_file(base_map_file)
    base_map_count = len(base_map)

    for map_file in map_files:
        if map_file != os.path.basename(base_map_file):
            file_path = os.path.join(map_dir, map_file)
            map = read_bin_file(file_path)

            new_map = []
            for line in map:
                line_length = len(line)
                for i in range(line_length):
                    mapped = False
                    for mapping in metatiles_index_mappings:
                        if line[i] in mapping:
                            line[i] = mapping[line[i]]
                            mapped = True
                            break
                    if not mapped:
                        new_metatile_index = base_map_count + len(base_map)
                        line[i] = new_metatile_index

                new_map.append(line)

            extension = 'ablk' if ablk else 'blk'

            output_file_path = os.path.join(
                map_dir, f"{os.path.splitext(map_file)[0]}Merged.{extension}")
            with open(output_file_path, 'wb') as f:
                for metatile in new_map:
                    f.write(bytes(metatile))


# blk -------------------------------------------------------------------------


def merge_blk_tilesets(gfx_dir):
    tilesets = []
    palette_maps = []
    found_pal_file = False
    for filename in os.listdir(gfx_dir):
        if filename.endswith('.png'):
            tileset_path = os.path.join(gfx_dir, filename)
            tiles = process_tileset(tileset_path)
            tilesets.append(tiles)
        elif filename.endswith('.asm'):
            palette_map_path = os.path.join(gfx_dir, filename)
            palette_map = []
            with open(palette_map_path, 'r') as f:
                lines = f.read().strip().split('\n')
                for line in lines:
                    if line.startswith('\ttilepal'):
                        colors = line.split(', ')[1:]
                        palette_map.extend(colors)
            palette_maps.append(palette_map)
        elif filename.endswith('.pal') and not found_pal_file:
            pal_file_path = os.path.join(gfx_dir, filename)
            shutil.copy(pal_file_path, os.path.join(gfx_dir, 'merged.pal'))
            found_pal_file = True

    base_tileset = max(tilesets, key=len)
    base_tileset_index = tilesets.index(base_tileset)
    base_palette_map = palette_maps[base_tileset_index]

    tiles_index_mappings = [{} for _ in range(len(tilesets))]

    for i, tileset in enumerate(tilesets):
        if i == base_tileset_index:
            continue

        for tile_index, tile in enumerate(tileset):
            for base_tile_index, base_tile in enumerate(base_tileset):
                if tile.tobytes() == base_tile.tobytes():
                    if palette_maps[i][tile_index] == base_palette_map[base_tile_index]:
                        tiles_index_mappings[i][tile_index] = base_tile_index

                        # debug_dir = os.path.join(gfx_dir, 'debug')
                        # os.makedirs(debug_dir, exist_ok=True)
                        # debug_image = Image.new('RGB', (8, 16))
                        # debug_image.paste(tile, (0, 0))
                        # debug_image.paste(base_tile, (0, 8))
                        # debug_image_path = os.path.join(debug_dir, f'match_{i}_{tile_index}_{base_tile_index}.png')
                        # debug_image.save(debug_image_path)

                        break

    tile_width, tile_height = base_tileset[0].size
    merged_tiles = base_tileset[:]
    merged_palette_map = base_palette_map[:len(base_tileset)]
    for i, tileset in enumerate(tilesets):
        if i == base_tileset_index:
            continue
        for tile_index, tile in enumerate(tileset):
            if tile_index not in tiles_index_mappings[i]:
                tiles_index_mappings[i][tile_index] = len(merged_tiles)
                merged_tiles.append(tile)
                merged_palette_map.append(palette_maps[i][tile_index])

    merged_width = tile_width * 16
    merged_height = tile_height * ((len(merged_tiles) + 15) // 16)
    merged_image = Image.new(
        'RGB', (merged_width, merged_height), (255, 255, 255))

    for idx, tile in enumerate(merged_tiles):
        x = (idx % 16) * tile_width
        y = (idx // 16) * tile_height
        merged_image.paste(tile, (x, y))

    merged_image_path = os.path.join(gfx_dir, 'merged.png')
    merged_image.save(merged_image_path)

    save_palette_map_asm_file(merged_palette_map, os.path.join(
        gfx_dir, 'merged_palette_map.asm'))

    tiles_index_mappings = [mapping for i, mapping in enumerate(
        tiles_index_mappings) if i != base_tileset_index]

    return base_tileset_index, tiles_index_mappings


def merge_blk_metatiles(data_dir, base_tileset_index, tiles_index_mappings):
    bin_files = [f for f in os.listdir(data_dir) if f.endswith('.bin')]
    base_metatiles_file = os.path.join(data_dir, bin_files[base_tileset_index])

    base_metatiles = read_bin_file(base_metatiles_file)
    base_metatiles_count = len(base_metatiles)

    collision_files = [f for f in os.listdir(
        data_dir) if f.endswith('collision.asm')]
    if len(collision_files) == 0 or len(collision_files) != len(bin_files):
        raise SystemExit('[Error] Some collision files are missing.')

    base_collision_file = os.path.join(
        data_dir, collision_files[base_tileset_index])
    with open(base_collision_file, 'r') as f:
        base_collision_lines = [
            line for line in f if line.startswith('\ttilecoll')]
    new_collision_lines = base_collision_lines[:]

    metatiles_index_mappings = []

    for filename in bin_files:
        if filename != os.path.basename(base_metatiles_file):
            file_path = os.path.join(data_dir, filename)
            metatiles = read_bin_file(file_path)

            collision_file_path = file_path.replace(
                'metatiles.bin', 'collision.asm')
            with open(collision_file_path, 'r') as f:
                collision_lines = [
                    line for line in f if line.startswith('\ttilecoll')]

            file_index_mapping = {}
            for metatile_index, metatile in enumerate(metatiles):
                for i in range(16):
                    tile_index = metatile[i]
                    for mapping in tiles_index_mappings:
                        if tile_index in mapping:
                            metatile[i] = mapping[tile_index]
                            break
                match_found = False
                for base_metatile_index, base_metatile in enumerate(base_metatiles[:base_metatiles_count]):
                    if metatile == base_metatile:
                        file_index_mapping[metatile_index] = base_metatile_index
                        match_found = True
                        break
                if not match_found:
                    file_index_mapping[metatile_index] = len(base_metatiles)
                    base_metatiles.append(metatile)
                    new_collision_lines.append(collision_lines[metatile_index])

            if file_index_mapping:
                metatiles_index_mappings.append(file_index_mapping)

    output_file_path = os.path.join(data_dir, 'merged_metatiles.bin')
    with open(output_file_path, 'wb') as f:
        for metatile in base_metatiles:
            f.write(bytes(metatile))

    output_file_path = os.path.join(data_dir, 'merged_collision.asm')
    with open(output_file_path, 'w') as f:
        for line in new_collision_lines:
            f.write(line)

    return metatiles_index_mappings


# ablk ------------------------------------------------------------------------


def merge_ablk_tilesets(gfx_dir):
    tilesets = []
    found_pal_file = False
    for filename in os.listdir(gfx_dir):
        if filename.endswith('.png'):
            tileset_path = os.path.join(gfx_dir, filename)
            tiles = process_tileset(tileset_path)
            tilesets.append(tiles)
        elif filename.endswith('.pal') and not found_pal_file:
            pal_file_path = os.path.join(gfx_dir, filename)
            shutil.copy(pal_file_path, os.path.join(gfx_dir, 'merged.pal'))
            found_pal_file = True

    base_tileset = max(tilesets, key=len)
    base_tileset_index = tilesets.index(base_tileset)

    tiles_index_mappings = [{} for _ in range(len(tilesets))]

    for i, tileset in enumerate(tilesets):
        if i == base_tileset_index:
            continue

        for tile_index, tile in enumerate(tileset):
            for base_tile_index, base_tile in enumerate(base_tileset):
                # Compare the original tile
                if tile.tobytes() == base_tile.tobytes():
                    tiles_index_mappings[i][tile_index] = (
                        base_tile_index, False, False)
                    break

                # Compare the tile with flip x
                tile_flipped_x = ImageOps.mirror(tile)
                if tile_flipped_x.tobytes() == base_tile.tobytes():
                    tiles_index_mappings[i][tile_index] = (
                        base_tile_index, True, False)
                    break

                # Comparar the tile with flip y
                tile_flipped_y = ImageOps.flip(tile)
                if tile_flipped_y.tobytes() == base_tile.tobytes():
                    tiles_index_mappings[i][tile_index] = (
                        base_tile_index, False, True)
                    break

                # Comparar the tile with flip x and y
                tile_flipped_xy = ImageOps.mirror(tile_flipped_y)
                if tile_flipped_xy.tobytes() == base_tile.tobytes():
                    tiles_index_mappings[i][tile_index] = (
                        base_tile_index, True, True)
                    break

    tile_width, tile_height = base_tileset[0].size
    merged_tiles = base_tileset[:]
    for i, tileset in enumerate(tilesets):
        if i == base_tileset_index:
            continue
        for tile_index, tile in enumerate(tileset):
            if tile_index not in tiles_index_mappings[i]:
                tiles_index_mappings[i][tile_index] = (
                    len(merged_tiles), False, False)
                merged_tiles.append(tile)

    merged_width = tile_width * 16
    merged_height = tile_height * ((len(merged_tiles) + 15) // 16)
    merged_image = Image.new(
        'RGB', (merged_width, merged_height), (255, 255, 255))

    for idx, tile in enumerate(merged_tiles):
        x = (idx % 16) * tile_width
        y = (idx // 16) * tile_height
        merged_image.paste(tile, (x, y))

    merged_image_path = os.path.join(gfx_dir, 'merged.png')
    merged_image.save(merged_image_path)

    tiles_index_mappings = [mapping for i, mapping in enumerate(
        tiles_index_mappings) if i != base_tileset_index]

    return base_tileset_index, tiles_index_mappings


def merge_ablk_metatiles(data_dir, base_tileset_index, tiles_index_mappings):
    def get_tile_index_real(tile_index, tile_info):
        tile_bank = (tile_info >> 3) & 1
        if tile_bank == 1:
            tile_index += 128  # $80 = 128
        return tile_index

    def set_tile(tile_index_mapping, tile_attrs):
        tile_index_real, flip_x, flip_y = tile_index_mapping
        if tile_index_real >= 128:
            tile_bank = 1
            tile_index = tile_index_real - 128
        else:
            tile_bank = 0
            tile_index = tile_index_real

        if tile_bank == 1:
            tile_attrs |= (1 << 3)
        else:
            tile_attrs &= ~(1 << 3)

        # Invert bits 5 and 6
        if flip_x:
            tile_attrs ^= (1 << 5)
        if flip_y:
            tile_attrs ^= (1 << 6)

        return tile_index, tile_attrs

    metatiles_files = [f for f in os.listdir(
        data_dir) if f.endswith('metatiles.bin')]
    base_metatiles_file = os.path.join(
        data_dir, metatiles_files[base_tileset_index])

    base_metatiles = read_bin_file(base_metatiles_file)
    base_metatiles_count = len(base_metatiles)

    attributes_files = [f for f in os.listdir(
        data_dir) if f.endswith('attributes.bin')]
    base_attributes_file = os.path.join(
        data_dir, attributes_files[base_tileset_index])

    base_attributes = read_bin_file(base_attributes_file)

    collision_files = [f for f in os.listdir(
        data_dir) if f.endswith('collision.asm')]
    if len(collision_files) == 0 or len(collision_files) != len(metatiles_files):
        raise SystemExit('[Error] Some collision files are missing.')

    base_collision_file = os.path.join(
        data_dir, collision_files[base_tileset_index])
    with open(base_collision_file, 'r') as f:
        base_collision_lines = [
            line for line in f if line.startswith('\ttilecoll')]
    new_collision_lines = base_collision_lines[:]

    metatiles_index_mappings = []

    for filename in metatiles_files:
        if filename != os.path.basename(base_metatiles_file):
            file_path = os.path.join(data_dir, filename)
            metatiles = read_bin_file(file_path)
            attributes = read_bin_file(file_path.replace(
                'metatiles.bin', 'attributes.bin'))

            collision_file_path = file_path.replace(
                'metatiles.bin', 'collision.asm')
            with open(collision_file_path, 'r') as f:
                collision_lines = [
                    line for line in f if line.startswith('\ttilecoll')]

            file_index_mapping = {}
            for metatile_index, metatile in enumerate(metatiles):
                metatile_attrs = attributes[metatile_index]
                for i in range(16):
                    tile_index = metatile[i]
                    tile_attrs = metatile_attrs[i]
                    tile_index_real = get_tile_index_real(
                        tile_index, tile_attrs)
                    for mapping in tiles_index_mappings:
                        if tile_index_real in mapping:
                            tile_info = set_tile(
                                mapping[tile_index_real], tile_attrs)
                            metatile[i] = tile_info[0]
                            metatile_attrs[i] = tile_info[1]
                            break
                match_found = False
                for base_metatile_index, base_metatile in enumerate(base_metatiles[:base_metatiles_count]):
                    if metatile == base_metatile and metatile_attrs == base_attributes[base_metatile_index]:
                        file_index_mapping[metatile_index] = base_metatile_index
                        match_found = True
                        break
                if not match_found:
                    file_index_mapping[metatile_index] = len(base_metatiles)
                    base_metatiles.append(metatile)
                    base_attributes.append(metatile_attrs)
                    new_collision_lines.append(collision_lines[metatile_index])

            if file_index_mapping:
                metatiles_index_mappings.append(file_index_mapping)

    output_file_path = os.path.join(data_dir, 'merged_metatiles.bin')
    with open(output_file_path, 'wb') as f:
        for metatile in base_metatiles:
            f.write(bytes(metatile))

    output_file_path = os.path.join(data_dir, 'merged_attributes.bin')
    with open(output_file_path, 'wb') as f:
        for attrs in base_attributes:
            f.write(bytes(attrs))

    output_file_path = os.path.join(data_dir, 'merged_collision.asm')
    with open(output_file_path, 'w') as f:
        for line in new_collision_lines:
            f.write(line)

    return metatiles_index_mappings


# FILES -----------------------------------------------------------------------


def ensure_file(base_dir, file_name):
    makefile_path = os.path.join(base_dir, file_name)
    if not os.path.exists(makefile_path):
        with open(makefile_path, 'w') as f:
            f.write("# Generated by Metatiled\n")
            f.write(
                "# Polished Map assumes a directory with a Makefile is the main project directory.\n")
            f.write(
                "# Polished Map++ assumes a directory with a Main.asm is the main project directory.\n")


def process_directories(base_dir, create=False):
    directories = [
        "data/tilesets",
        "gfx/tilesets",
        "maps"
    ]
    dir_paths = []
    for directory in directories:
        path = os.path.join(base_dir, directory)
        if create and not os.path.exists(path):
            os.makedirs(path)
        dir_paths.append(path)
    return dir_paths


# SAVE ------------------------------------------------------------------------


def save_blk_file(output_path, metatile_indexes):
    with open(output_path, 'wb') as f:
        for position in metatile_indexes:
            f.write(position.to_bytes(1, 'big'))


def save_palette_txt_file(image_path, palette):
    with open(f"{image_path[:-4]}.txt", "w") as file:
        file.write("[PALETTE]\n\n")
        for i, color_tones in enumerate(palette):
            file.write("?\n")
            for tone in color_tones:
                file.write(f"{rgb_to_hex(tone)}\n")
            for _ in range(4 - len(color_tones)):
                file.write("------\n")
            if i < len(palette) - 1:
                file.write("\n")


def save_pal_file(pal_path, custom_palette, compress):
    color_order = palettes['morn'].keys()
    with open(pal_path, 'w') as file:
        if compress:
            file.write("\n")
            for color_name in color_order:
                tones = custom_palette.get(color_name, [(0, 0, 0)] * 4)
                rgb_values = []
                for tone in tones:
                    r, g, b = convert_to_5bit_rgb(tone)
                    rgb_values.append(f"{r:02},{g:02},{b:02}")
                rgb_values_str = ', '.join(rgb_values)
                file.write(f"\tRGB {rgb_values_str} ; {color_name.lower()}\n")
        else:
            for color_name in color_order:
                file.write(f"; {color_name.lower()}\n")
                tones = custom_palette.get(color_name, [(0, 0, 0)] * 4)
                for tone in tones:
                    r, g, b = convert_to_5bit_rgb(tone)
                    file.write(f"\tRGB {r:02}, {g:02}, {b:02}\n")


def save_collision_asm_file(collision_mask, collision_colors, metatile_positions, output_path):
    metatile_collisions = []

    for i, (pos_x, pos_y) in enumerate(metatile_positions):

        real_x = (pos_x - 1) * 32
        real_y = (pos_y - 1) * 32
        collision_metatile = collision_mask.crop(
            (real_x, real_y, real_x + 32, real_y + 32))

        collisions = []
        for tile_y in range(0, 32, 16):
            for tile_x in range(0, 32, 16):
                color = collision_metatile.getpixel((tile_x, tile_y))
                if color:
                    hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
                    collision_type = collision_colors.get(
                        hex_color, '?') if i != 0 else 'VOID'
                    collisions.append(collision_type)

                    # metatiles[i].save(os.path.join('debug', f'metatile_{i}.png'))
                    # collision_metatile.save(os.path.join('debug', f'collision_metatile_{i}.png'))

        metatile_collisions.append(collisions)

    lines = []
    for i, collisions in enumerate(metatile_collisions):
        line = f"\ttilecoll {', '.join(collisions)} ; {i:02x}"
        lines.append(line)

    with open(output_path, 'w') as f:
        for line in lines:
            f.write(line + '\n')


# blk -------------------------------------------------------------------------


def save_tileset_image(tiles, color_to_grays, output_path, grayscale=True):
    num_rows = (len(tiles) + 15) // 16
    height = num_rows * 8

    tileset_image = Image.new('RGB', (128, height), (255, 255, 255))

    if grayscale:
        for i, tile in enumerate(tiles):
            new_tile = tile if len(tiles) > 192 and i == 127 else tile_to_grayscale(
                tile, color_to_grays[i])
            x = (i % 16) * 8
            y = (i // 16) * 8
            tileset_image.paste(new_tile, (x, y))

    else:
        for i, tile in enumerate(tiles):
            x = (i % 16) * 8
            y = (i // 16) * 8
            tileset_image.paste(tile, (x, y))

    tileset_image.save(output_path)


def save_metatiles_bin_file(metatiles, tiles, output_path):
    with open(output_path, 'wb') as f:
        for metatile in metatiles:
            for y in range(0, 32, 8):
                for x in range(0, 32, 8):
                    tile = metatile.crop((x, y, x + 8, y + 8))
                    tile_index = tiles.index(tile)

                    # ? The space tile can't be used in any metatiles
                    if len(tiles) > 192 and tile_index == 127:
                        tile_index = tiles.index(tile, 128)

                    f.write(tile_index.to_bytes(1, 'big'))


def save_palette_map_asm_file(colors, output_path):
    vram_area_tiles = 96
    if len(colors) > 192:
        vram_area_tiles = 128

    lines = []

    # Section 1
    lines.append("; bottom-left vram area $00 - $7F")
    for i in range(vram_area_tiles // 8):
        line_colors = colors[i * 8:(i + 1) * 8]
        if len(line_colors) < 8:
            line_colors.extend(['TEXT'] * (8 - len(line_colors)))
        line = "\ttilepal 0, " + ", ".join(line_colors)
        lines.append(line)

    if len(colors) <= 192:
        # Section 2
        lines.append("rept 16")
        lines.append("    db $ff")
        lines.append("endr")

    # Section 3
    lines.append("\n; bottom-right vram area $80 - $FF")
    for i in range(vram_area_tiles // 8):
        line_colors = colors[(vram_area_tiles // 8 + i)
                             * 8:(vram_area_tiles // 8 + 1 + i) * 8]
        if len(line_colors) < 8:
            line_colors.extend(['TEXT'] * (8 - len(line_colors)))
        line = "\ttilepal 1, " + ", ".join(line_colors)
        lines.append(line)

    with open(output_path, 'w') as f:
        for i, line in enumerate(lines):
            if i < len(lines) - 1:
                f.write(line + '\n')
            else:
                f.write(line)


# ablk ------------------------------------------------------------------------


def save_compressed_tileset_image(tiles, output_path):
    num_rows = (len(tiles) + 15) // 16
    height = num_rows * 8

    tileset_image = Image.new('RGB', (128, height), (255, 255, 255))

    for i, tile in enumerate(tiles):
        x = (i % 16) * 8
        y = (i // 16) * 8
        tileset_image.paste(tile, (x, y))

    tileset_image.save(output_path)


def save_attr_metatiles_bin_file(attr_metatiles, output_path):
    with open(output_path, 'wb') as f:
        for metatile_info in attr_metatiles:
            for compressed_index, color, flip_x, flip_y in metatile_info:
                f.write(bytes([compressed_index % 0x80]))


def save_attributes_bin_file(attr_metatiles, palettes, output_path):
    with open(output_path, 'wb') as f:
        for metatile_info in attr_metatiles:
            for compressed_index, color, flip_x, flip_y in metatile_info:
                color_index = list(palettes['morn'].keys()).index(color)
                attributes = color_index & 0x07
                if compressed_index >= 0x80:
                    attributes |= 0x08  # Set bank 1
                if flip_x:
                    attributes |= 0x20
                if flip_y:
                    attributes |= 0x40
                f.write(bytes([attributes]))


# -----------------------------------------------------------------------------


def main():
    palettes_8bit_rgb = palettes_to_8bit_rgb(palettes)

    parser = argparse.ArgumentParser(
        description='Convert an image (PNG) to a map.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('map_image', type=str, nargs='?', default=None,
                       help='Name of the map image file (PNG).')
    group.add_argument('--merge', '-m', action='store_true',
                       help='Merge tilesets along with their related files.')

    parser.add_argument('--palette', '-p', type=str,
                        help='Specify palette to use (avoid auto-detect).')
    parser.add_argument('--compress', '-c', action='store_true',
                        help='Apply additional compression to tiles.')
    parser.add_argument('--extract-palette', '-e', action='store_true',
                        help='Extract the palette from the image.')
    parser.add_argument('--analyze-palette', '-a', action='store_true',
                        help='Validate the palette; if invalid, output a guiding image.')

    args = parser.parse_args()

    map_path = args.map_image
    palette_name = args.palette
    merge = args.merge
    compress = args.compress
    extract_palette = args.extract_palette
    analyze_palette = args.analyze_palette

    base_dir = os.path.dirname(os.path.abspath(__file__))

    if merge:
        data_dir, gfx_dir, map_dir = process_directories(base_dir)
        if not compress:
            base_tileset_index, tiles_index_mappings = merge_blk_tilesets(
                gfx_dir)
            metatiles_index_mappings = merge_blk_metatiles(
                data_dir, base_tileset_index, tiles_index_mappings)
            merge_maps(map_dir, base_tileset_index,
                       metatiles_index_mappings)
        else:
            base_tileset_index, tiles_index_mappings = merge_ablk_tilesets(
                gfx_dir)
            metatiles_index_mappings = merge_ablk_metatiles(
                data_dir, base_tileset_index, tiles_index_mappings)
            merge_maps(map_dir, base_tileset_index,
                       metatiles_index_mappings, ablk=True)
        print('Merged!')
        return

    base_name = os.path.splitext(os.path.basename(map_path))[0]

    if analyze_palette:
        analyze(map_path)
        return

    process_directories(base_dir, create=True)

    palette = palettes_8bit_rgb[palette_name] if palette_name else None
    palette = 'extract' if extract_palette else palette

    info = load_info(map_path)

    custom_palette = info[0] if info and not palette else None
    collision_colors = info[1] if info else None

    if custom_palette:
        palettes_8bit_rgb['custom'] = custom_palette
        palette = custom_palette

        pal_file_path = os.path.join(
            base_dir, 'gfx', 'tilesets', f'{base_name}.pal')
        save_pal_file(pal_file_path, palette, compress)

    map_image = Image.open(map_path).convert("RGB")  # Remove transparency
    darkest_tone = sort_color(list(set(map_image.getdata())))[-1]
    metatiles, positions = divide_into_metatiles(map_image)
    unique_metatiles, metatile_positions, metatile_indexes = identify_unique_metatiles(
        metatiles, positions, darkest_tone)
    tiles, tile_color_names, color_to_grays, monochrome = identify_unique_tiles(
        unique_metatiles, metatile_positions, palettes_8bit_rgb, palette)

    if extract_palette:
        palette_colors = tiles
        save_palette_txt_file(map_path, palette_colors)

        print('Done!')
        return

    if collision_colors:
        collision_mask = Image.open(map_path.replace(
            '.png', '_collision.png')).convert('RGB')
        collision_asm_path = os.path.join(
            base_dir, 'data', 'tilesets', f'{base_name}_collision.asm')
        save_collision_asm_file(
            collision_mask, collision_colors, metatile_positions, collision_asm_path)

    if not compress:
        ensure_file(base_dir, 'Makefile')

        blk_file_name = ''.join([word.capitalize()
                                for word in base_name.split('_')]) + '.blk'
        blk_file_path = os.path.join(base_dir, 'maps', blk_file_name)
        save_blk_file(blk_file_path, metatile_indexes)

        tileset_image_path = os.path.join(
            base_dir, 'gfx', 'tilesets', f'{base_name}.png')
        save_tileset_image(tiles, color_to_grays,
                           tileset_image_path, grayscale=True)

        metatiles_binary_path = os.path.join(
            base_dir, 'data', 'tilesets', f'{base_name}_metatiles.bin')
        save_metatiles_bin_file(unique_metatiles, tiles, metatiles_binary_path)

        if not monochrome:
            asm_file_path = os.path.join(
                base_dir, 'gfx', 'tilesets', f'{base_name}_palette_map.asm')
            save_palette_map_asm_file(tile_color_names, asm_file_path)
    else:
        compressed_tiles, transformations = compress_tiles(
            tiles, tile_color_names, color_to_grays)
        attr_metatiles = get_attr_metatiles(
            unique_metatiles, compressed_tiles, transformations, color_to_grays)

        ensure_file(base_dir, 'Main.asm')

        compressed_tileset_image_path = os.path.join(
            base_dir, 'gfx', 'tilesets', f'{base_name}.png')
        save_compressed_tileset_image(
            compressed_tiles, compressed_tileset_image_path)

        metatiles_binary_path = os.path.join(
            base_dir, 'data', 'tilesets', f'{base_name}_metatiles.bin')
        save_attr_metatiles_bin_file(attr_metatiles, metatiles_binary_path)

        attributes_binary_path = os.path.join(
            base_dir, 'data', 'tilesets', f'{base_name}_attributes.bin')
        save_attributes_bin_file(
            attr_metatiles, palettes_8bit_rgb, attributes_binary_path)

        ablk_file_name = ''.join([word.capitalize()
                                  for word in base_name.split('_')]) + '.ablk'
        ablk_file_path = os.path.join(base_dir, 'maps', ablk_file_name)
        save_blk_file(ablk_file_path, metatile_indexes)

    print('Done!')


if __name__ == "__main__":
    main()
