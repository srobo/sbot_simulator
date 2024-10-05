#!/usr/bin/env python3
"""A script to run a competition match."""

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from run_simulator import get_webots_parameters

NUM_ZONES = 4
GAME_DURATION_SECONDS = 150


class MatchParams(argparse.Namespace):
    """Parameters for running a competition match."""

    archives_dir: Path
    match_num: int
    teams: list[str]
    duration: int
    video_enabled: bool
    video_resolution: tuple[int, int]


def load_team_code(
    usercode_dir: Path,
    arena_root: Path,
    match_parameters: MatchParams,
) -> None:
    """Load the team code into the arena root."""
    for zone_id, tla in enumerate(match_parameters.teams):
        zone_path = arena_root / f"zone_{zone_id}"

        if zone_path.exists():
            shutil.rmtree(zone_path)

        if tla == '-':
            # no team in this zone
            continue

        zone_path.mkdir()
        with ZipFile(usercode_dir / f'{tla}.zip') as zipfile:
            zipfile.extractall(zone_path)


def generate_match_file(save_path: Path, match_parameters: MatchParams) -> None:
    """Write the match file to the arena root."""
    match_file = save_path / 'match.json'

    # Use a format that is compatible with SRComp
    match_file.write_text(json.dumps(
        {
            'match_number': match_parameters.match_num,
            'arena_id': 'Simulator',
            'teams': {
                tla: {'zone': idx}
                for idx, tla in enumerate(match_parameters.teams)
                if tla != '-'
            },
            'duration': match_parameters.duration,
            'recording_config': {
                'enabled': match_parameters.video_enabled,
                'resolution': list(match_parameters.video_resolution)
            }
        },
        indent=4,
    ))


def set_comp_mode(arena_root: Path) -> None:
    """Write the mode file to indicate that the competition is running."""
    (arena_root / 'mode.txt').write_text('comp')


def archive_zone_files(
    team_archives_dir: Path,
    arena_root: Path,
    zone: int,
    match_id: str,
) -> None:
    """Zip the files in the zone directory and save them to the team archives directory."""
    zone_dir = arena_root / f'zone_{zone}'

    shutil.make_archive(str(team_archives_dir / f'{match_id}-zone-{zone}'), 'zip', zone_dir)


def archive_zone_folders(
    archives_dir: Path,
    arena_root: Path,
    teams: list[str],
    match_id: str,
) -> None:
    """Zip the zone folders and save them to the archives directory."""
    for zone_id, tla in enumerate(teams):
        if tla == '-':
            # no team in this zone
            continue

        tla_dir = archives_dir / tla
        tla_dir.mkdir(exist_ok=True)

        archive_zone_files(tla_dir, arena_root, zone_id, match_id)


def archive_match_recordings(archives_dir: Path, arena_root: Path, match_id: str) -> None:
    """Copy the video, animation, and image files to the archives directory."""
    recordings_dir = archives_dir / 'recordings'
    recordings_dir.mkdir(exist_ok=True)

    match_recordings = arena_root / 'recordings'

    # Copy the video file
    video_file = match_recordings / f'{match_id}.mp4'
    if video_file.exists():
        shutil.copy(video_file, recordings_dir)

    # Copy the animation files
    animation_files = [
        match_recordings / f'{match_id}.html',
        match_recordings / f'{match_id}.json',
        match_recordings / f'{match_id}.x3d',
        match_recordings / f'{match_id}.css',
    ]
    for animation_file in animation_files:
        shutil.copy(animation_file, recordings_dir)

    # Copy the animation textures
    # Every match will have the same textures, so we only need one copy of them
    textures_dir = match_recordings / 'textures'
    shutil.copytree(textures_dir, recordings_dir / 'textures', dirs_exist_ok=True)

    # Copy the image file
    image_file = match_recordings / f'{match_id}.jpg'
    shutil.copy(image_file, recordings_dir)


def archive_match_file(archives_dir: Path, match_file: Path, match_number: int) -> None:
    """
    Copy the match file (which may contain scoring data) to the archives directory.

    This also renames the file to be compatible with SRComp.
    """
    matches_dir = archives_dir / 'matches'
    matches_dir.mkdir(exist_ok=True)

    # SRComp expects YAML files. JSON is a subset of YAML, so we can just rename the file.
    completed_match_file = matches_dir / f'{match_number:0>3}.yaml'

    shutil.copy(match_file, completed_match_file)


def archive_supervisor_log(archives_dir: Path, arena_root: Path, match_id: str) -> None:
    """Archive the supervisor log file."""
    log_archive_dir = archives_dir / 'supervisor_logs'
    log_archive_dir.mkdir(exist_ok=True)

    log_file = arena_root / f'supervisor-log-{match_id}.txt'

    shutil.copy(log_file, log_archive_dir)


def execute_match(arena_root: Path) -> None:
    """Run Webots with the right world."""
    # Webots is only on the PATH on Linux so we have a helper function to find it
    try:
        webots, world_file = get_webots_parameters()
    except RuntimeError:
        raise FileNotFoundError("Webots executable not found.")

    sim_env = os.environ.copy()
    sim_env['ARENA_ROOT'] = str(arena_root)
    try:
        subprocess.check_call(
            [
                str(webots),
                '--batch',
                '--stdout',
                '--stderr',
                '--mode=realtime',
                str(world_file),
            ],
            env=sim_env,
        )
    except subprocess.CalledProcessError as e:
        # TODO review log output here
        raise RuntimeError(f"Webots failed with return code {e.returncode}") from e


def run_match(match_parameters: MatchParams) -> None:
    """Run the match in a temporary directory and archive the results."""
    with TemporaryDirectory(suffix=f'match-{match_parameters.match_num}') as temp_folder:
        arena_root = Path(temp_folder)
        match_num = match_parameters.match_num
        match_id = f'match-{match_num}'
        archives_dir = match_parameters.archives_dir

        # unzip teams code into zone_N folders under this folder
        load_team_code(archives_dir, arena_root, match_parameters)
        # Create info file to tell the comp supervisor what match this is
        # and how to handle recordings
        generate_match_file(arena_root, match_parameters)
        # Set mode file to comp
        set_comp_mode(arena_root)

        try:
            # Run webots with the right world
            execute_match(arena_root)
        except (FileNotFoundError, RuntimeError) as e:
            print(f"Failed to run match: {e}")
            # Save the supervisor log as it may contain useful information
            archive_supervisor_log(archives_dir, arena_root, match_id)
            raise

        # Archive the supervisor log first in case any collation fails
        archive_supervisor_log(archives_dir, arena_root, match_id)
        # Zip up and collect all files for each zone
        archive_zone_folders(archives_dir, arena_root, match_parameters.teams, match_id)
        # Collect video, animation & image
        archive_match_recordings(archives_dir, arena_root, match_id)
        # Collect ancillary files
        archive_match_file(archives_dir, arena_root / 'match.json', match_num)


def parse_args() -> MatchParams:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run a competition match.")

    parser.add_argument(
        'archives_dir',
        help=(
            "The directory containing the teams' robot code, as Zip archives "
            "named for the teams' TLAs. This directory will also be used as the "
            "root for storing the resulting logs and recordings."
        ),
        type=Path,
    )
    parser.add_argument(
        'match_num',
        type=int,
        help="The number of the match to run.",
    )
    parser.add_argument(
        'teams',
        nargs=NUM_ZONES,
        help=(
            "TLA of the team in each zone, in order from zone 0 to "
            f"{NUM_ZONES - 1}. Use dash (-) for an empty zone. "
            "Must specify all zones."
        ),
        metavar='tla',
    )
    parser.add_argument(
        '--duration',
        help="The duration of the match (in seconds).",
        type=int,
        default=GAME_DURATION_SECONDS,
    )
    parser.add_argument(
        '--no-record',
        help=(
            "Inhibit creation of the MPEG video, the animation is unaffected. "
            "This can greatly increase the execution speed on GPU limited systems "
            "when the video is not required."
        ),
        action='store_false',
        dest='video_enabled',
    )
    parser.add_argument(
        '--resolution',
        help="Set the resolution of the produced video.",
        type=int,
        nargs=2,
        default=[1920, 1080],
        metavar=('width', 'height'),
        dest='video_resolution',
    )
    return parser.parse_args(namespace=MatchParams())


def main() -> None:
    """Run a competition match entrypoint."""
    match_parameters = parse_args()
    run_match(match_parameters)


if __name__ == '__main__':
    main()
