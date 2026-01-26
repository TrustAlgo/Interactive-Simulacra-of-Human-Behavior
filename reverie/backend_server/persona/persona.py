"""
Author: Joon Sung Park (joonspk@stanford.edu)

Defines the Persona (GenerativeAgent) class used in Reverie.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

from persona.memory_structures.spatial_memory import MemoryTree
from persona.memory_structures.associative_memory import AssociativeMemory
from persona.memory_structures.scratch import Scratch

from persona.cognitive_modules.perceive import perceive
from persona.cognitive_modules.retrieve import retrieve
from persona.cognitive_modules.plan import plan
from persona.cognitive_modules.reflect import reflect
from persona.cognitive_modules.execute import execute
from persona.cognitive_modules.converse import open_convo_session


class Persona:
    """
    Persona (aka GenerativeAgent) that powers agent cognition in Reverie.
    """

    def __init__(self, name: str, folder_mem_saved: str | Path = "") -> None:
        self.name = name

        base_path = Path(folder_mem_saved) / "bootstrap_memory"

        # Spatial memory
        self.s_mem = MemoryTree(base_path / "spatial_memory.json")

        # Associative memory
        self.a_mem = AssociativeMemory(base_path / "associative_memory")

        # Scratch (short-term memory)
        self.scratch = Scratch(base_path / "scratch.json")

    # ---------------------------------------------------------------------
    # Persistence
    # ---------------------------------------------------------------------

    def save(self, save_folder: str | Path) -> None:
        save_path = Path(save_folder)

        self.s_mem.save(save_path / "spatial_memory.json")
        self.a_mem.save(save_path / "associative_memory")
        self.scratch.save(save_path / "scratch.json")

    # ---------------------------------------------------------------------
    # Cognitive pipeline (thin wrappers)
    # ---------------------------------------------------------------------

    def perceive(self, maze: Any):
        return perceive(self, maze)

    def retrieve(self, perceived):
        return retrieve(self, perceived)

    def plan(self, maze, personas, new_day, retrieved):
        return plan(self, maze, personas, new_day, retrieved)

    def execute(self, maze, personas, plan_result):
        return execute(self, maze, personas, plan_result)

    def reflect(self) -> None:
        reflect(self)

    # ---------------------------------------------------------------------
    # Main agent loop
    # ---------------------------------------------------------------------

    def move(
        self,
        maze: Any,
        personas: Dict[str, "Persona"],
        curr_tile: Tuple[int, int],
        curr_time: datetime.datetime,
    ):
        # Update scratch state
        self.scratch.curr_tile = curr_tile

        # Detect new day
        new_day = False
        if not self.scratch.curr_time:
            new_day = "First day"
        elif self.scratch.curr_time.strftime("%A %B %d") != curr_time.strftime(
            "%A %B %d"
        ):
            new_day = "New day"

        self.scratch.curr_time = curr_time

        # Cognitive sequence
        perceived = self.perceive(maze)
        retrieved = self.retrieve(perceived)
        plan_result = self.plan(maze, personas, new_day, retrieved)
        self.reflect()

        return self.execute(maze, personas, plan_result)

    # ---------------------------------------------------------------------
    # Conversation
    # ---------------------------------------------------------------------

    def open_convo_session(self, convo_mode: str) -> None:
        open_convo_session(self, convo_mode)
