"""
Author: Joon Sung Park (joonspk@stanford.edu)
Optimized by: ChatGPT

Description:
Defines the Maze class, which represents the simulated world
as a 2D grid with semantic layers and fast reverse lookups.
"""

import json
import math
from collections import defaultdict
from typing import Dict, List, Tuple, Set

from global_methods import env_matrix
from utils import read_file_to_list


TileCoord = Tuple[int, int]
Event = Tuple[str, object, object, object]


class Maze:
    def __init__(self, maze_name: str):
        self.maze_name = maze_name

        # -----------------------------
        # Load meta information
        # -----------------------------
        meta_path = f"{env_matrix}/maze_meta_info.json"
        with open(meta_path, "r") as f:
            meta = json.load(f)

        self.maze_width = int(meta["maze_width"])
        self.maze_height = int(meta["maze_height"])
        self.sq_tile_size = int(meta["sq_tile_size"])
        self.special_constraint = meta["special_constraint"]

        # -----------------------------
        # Load special block mappings
        # -----------------------------
        blocks_folder = f"{env_matrix}/special_blocks"

        def load_block_map(filename: str) -> Dict[str, str]:
            rows = read_file_to_list(f"{blocks_folder}/{filename}", header=False)
            return {row[0]: row[-1] for row in rows}

        world_block = read_file_to_list(
            f"{blocks_folder}/world_blocks.csv", header=False
        )[0][-1]

        sector_blocks = load_block_map("sector_blocks.csv")
        arena_blocks = load_block_map("arena_blocks.csv")
        object_blocks = load_block_map("game_object_blocks.csv")
        spawn_blocks = load_block_map("spawning_location_blocks.csv")

        # -----------------------------
        # Load maze matrices
        # -----------------------------
        maze_folder = f"{env_matrix}/maze"

        def load_maze(filename: str) -> List[str]:
            return read_file_to_list(f"{maze_folder}/{filename}", header=False)[0]

        collision_raw = load_maze("collision_maze.csv")
        sector_raw = load_maze("sector_maze.csv")
        arena_raw = load_maze("arena_maze.csv")
        object_raw = load_maze("game_object_maze.csv")
        spawn_raw = load_maze("spawning_location_maze.csv")

        # -----------------------------
        # Build tiles
        # -----------------------------
        self.tiles: List[List[Dict]] = []
        self.address_tiles: Dict[str, Set[TileCoord]] = defaultdict(set)

        for y in range(self.maze_height):
            row = []
            for x in range(self.maze_width):
                idx = y * self.maze_width + x

                tile = {
                    "world": world_block,
                    "sector": sector_blocks.get(sector_raw[idx], ""),
                    "arena": arena_blocks.get(arena_raw[idx], ""),
                    "game_object": object_blocks.get(object_raw[idx], ""),
                    "spawning_location": spawn_blocks.get(spawn_raw[idx], ""),
                    "collision": collision_raw[idx] != "0",
                    "events": set(),
                }

                # Initialize game object event
                if tile["game_object"]:
                    obj_path = (
                        f"{tile['world']}:"
                        f"{tile['sector']}:"
                        f"{tile['arena']}:"
                        f"{tile['game_object']}"
                    )
                    tile["events"].add((obj_path, None, None, None))

                # Reverse address indexing
                self._index_tile_addresses(tile, x, y)

                row.append(tile)
            self.tiles.append(row)

    # -----------------------------
    # Internal helpers
    # -----------------------------
    def _index_tile_addresses(self, tile: Dict, x: int, y: int):
        if tile["sector"]:
            self.address_tiles[f"{tile['world']}:{tile['sector']}"].add((x, y))

        if tile["arena"]:
            self.address_tiles[
                f"{tile['world']}:{tile['sector']}:{tile['arena']}"
            ].add((x, y))

        if tile["game_object"]:
            self.address_tiles[
                f"{tile['world']}:{tile['sector']}:{tile['arena']}:{tile['game_object']}"
            ].add((x, y))

        if tile["spawning_location"]:
            self.address_tiles[f"<spawn_loc>{tile['spawning_location']}"].add((x, y))

    # -----------------------------
    # Public API
    # -----------------------------
    def turn_coordinate_to_tile(self, px: Tuple[int, int]) -> TileCoord:
        return (
            math.ceil(px[0] / self.sq_tile_size),
            math.ceil(px[1] / self.sq_tile_size),
        )

    def access_tile(self, tile: TileCoord) -> Dict:
        x, y = tile
        return self.tiles[y][x]

    def get_tile_path(self, tile: TileCoord, level: str) -> str:
        t = self.access_tile(tile)

        if level == "world":
            return t["world"]
        if level == "sector":
            return f"{t['world']}:{t['sector']}"
        if level == "arena":
            return f"{t['world']}:{t['sector']}:{t['arena']}"
        return f"{t['world']}:{t['sector']}:{t['arena']}:{t['game_object']}"

    def get_nearby_tiles(self, tile: TileCoord, vision_r: int) -> List[TileCoord]:
        x, y = tile
        x_min = max(0, x - vision_r)
        x_max = min(self.maze_width, x + vision_r + 1)
        y_min = max(0, y - vision_r)
        y_max = min(self.maze_height, y + vision_r + 1)

        return [(i, j) for i in range(x_min, x_max) for j in range(y_min, y_max)]

    def add_event_from_tile(self, event: Event, tile: TileCoord):
        self.access_tile(tile)["events"].add(event)

    def remove_event_from_tile(self, event: Event, tile: TileCoord):
        self.access_tile(tile)["events"].discard(event)

    def turn_event_from_tile_idle(self, event: Event, tile: TileCoord):
        events = self.access_tile(tile)["events"]
        if event in events:
            events.remove(event)
            events.add((event[0], None, None, None))

    def remove_subject_events_from_tile(self, subject: str, tile: TileCoord):
        events = self.access_tile(tile)["events"]
        events_copy = set(events)
        for ev in events_copy:
            if ev[0] == subject:
                events.remove(ev)
