# -*- coding:utf-8 -*-
#
# Copyright (C) 2020, Maximilian Köhl <koehl@cs.uni-saarland.de>

from __future__ import annotations

import typing as t

import pathlib

import click

import racetrack

from momba.explore import compiler


FUEL_MODELS = {
    "LINEAR": racetrack.fuel_model_linear,
    "QUADRATIC": racetrack.fuel_model_quadratic,
    "REGULAR": racetrack.fuel_model_regular,
}


@click.command()
@click.argument("track_file", type=pathlib.Path)
@click.argument("start_cell", type=int)
@click.argument("output", type=pathlib.Path)
@click.option(
    "--underground",
    "underground_name",
    type=click.Choice(tuple(underground.name for underground in racetrack.Underground)),
    default=racetrack.Underground.TARMAC.name,
)
@click.option(
    "--tank-type",
    "tank_type_name",
    type=click.Choice(tuple(tank_type.name for tank_type in racetrack.TankType)),
    default=racetrack.TankType.LARGE.name,
)
@click.option("--max-speed", type=int, default=2)
@click.option("--max-acceleration", type=int, default=2)
@click.option(
    "--fuel-model",
    "fuel_model_name",
    type=click.Choice(FUEL_MODELS.keys()),
    default="REGULAR",
)
def main(
    track_file: pathlib.Path,
    start_cell: int,
    output: pathlib.Path,
    underground_name: str,
    tank_type_name: str,
    max_speed: int,
    max_acceleration: int,
    fuel_model_name: str,
) -> None:
    """
    Compiles the Racetrack model to MombaCR.
    """
    track = racetrack.Track.from_source(track_file.read_text(encoding="utf-8"))
    if start_cell not in track.start_cells:
        print(
            f"Invalid start cell {start_cell}. Valid start cells {track.start_cells!r}."
        )
        return
    underground = racetrack.Underground[underground_name]
    tank_type = racetrack.TankType[tank_type_name]
    fuel_model = FUEL_MODELS[fuel_model_name]

    # construct a Scenario from the given parameters
    scenario = racetrack.Scenario(
        track,
        start_cell,
        tank_type=tank_type,
        underground=underground,
        max_speed=max_speed,
        max_acceleration=max_acceleration,
        fuel_model=fuel_model,
    )

    print("Building model...")
    network = racetrack.construct_model(scenario)

    print("Compiling model...")
    output.write_text(compiler.compile_network(network), encoding="utf-8")


if __name__ == "__main__":
    main()
