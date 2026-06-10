import pytest
from src.models.blueprint import Blueprint

def test_blueprint_parse():
    line = "Blueprint 1: 4 2 3 14 2 7 1 5 3"
    bp = Blueprint.parse(line)
    assert bp.id == 1
    assert bp.ore_robot_ore == 4
    assert bp.clay_robot_ore == 2
    assert bp.obsidian_robot_ore == 3
    assert bp.obsidian_robot_clay == 14
    assert bp.geode_robot_ore == 2
    assert bp.geode_robot_obsidian == 7
    assert bp.diamond_robot_geode == 1
    assert bp.diamond_robot_clay == 5
    assert bp.diamond_robot_obsidian == 3

def test_blueprint_max_costs():
    bp = Blueprint(1, 4, 2, 3, 14, 2, 7, 1, 5, 3)
    assert bp.max_ore_cost == 4
    assert bp.max_clay_cost == 14
    assert bp.max_obsidian_cost == 7
    assert bp.max_geode_cost == 1

def test_blueprint_parse_invalid():
    # Only 9 numbers
    line = "Blueprint 1: 4 2 3 14 2 7 1 5"
    with pytest.raises(ValueError, match="Expected 10 integers for a Blueprint, but got 9."):
        Blueprint.parse(line)
