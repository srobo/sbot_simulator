"""."""
from __future__ import annotations

import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from controller import Supervisor

# Robot constructor lacks a return type annotation in R2023b
sys.path.insert(0, Supervisor().getProjectPath())  # type: ignore[no-untyped-call]
import environment  # configure path to include modules
from robot_logging import get_match_identifier, prefix_and_tee_streams
from robot_utils import get_game_mode, get_match_data, get_robot_file

# Get the robot object that was created when setting up the environment
_robot = Supervisor.created
assert _robot is not None, "Robot object not created"
supervisor: Supervisor = _robot  # type: ignore[assignment]


class RobotData:
    """Data about a robot in the arena."""

    def __init__(self, zone: int):
        self.registered_ready = False
        self.zone = zone
        self.robot = supervisor.getFromDef(f'ROBOT{zone}')
        if self.robot is None:
            raise ValueError(f"Failed to get Webots node for zone {zone}")

    def zone_occupied(self) -> bool:
        """Check if this zone has a robot.py file associated with it."""
        try:
            _ = get_robot_file(self.zone)
        except FileNotFoundError:
            return False
        return True

    def remove_robot(self) -> None:
        """Delete the robot proto from the world."""
        self.robot.remove()  # type: ignore[attr-defined]

    def preset_robot(self) -> None:
        """Arm the robot so that it waits for the start signal."""
        self.robot.getField('customData').setSFString('prestart')  # type: ignore[attr-defined]

    def robot_ready(self) -> bool:
        """Check if robot has set its pre-start flag."""
        return bool(self.robot.getField('customData').getSFString() == 'ready')  # type: ignore[attr-defined]

    def start_robot(self) -> None:
        """Signal to the robot that the start button has been pressed."""
        self.robot.getField('customData').setSFString('start')  # type: ignore[attr-defined]


class Robots:
    """A collection of robots in the arena."""

    def __init__(self) -> None:
        self.robots: dict[int, RobotData] = {}

        for zone in range(0, environment.NUM_ZONES):
            try:
                robot_data = RobotData(zone)
            except ValueError as e:
                print(e)
            else:
                self.robots[zone] = robot_data

    def remove_unoccupied_robots(self) -> None:
        """Remove all robots that don't have usercode."""
        for robot in list(self.robots.values()):
            if not robot.zone_occupied():
                robot.remove_robot()
                _ = self.robots.pop(robot.zone)

    def preset_robots(self) -> None:
        """Arm all robots so that they wait for the start signal."""
        for robot in self.robots.values():
            robot.preset_robot()

    def wait_for_ready(self, timeout: float) -> None:
        """Wait for all robots to set their pre-start flags."""
        end_time = supervisor.getTime() + timeout
        while supervisor.getTime() < end_time:
            all_ready = True
            # Sleep in individual timesteps to allow the robots to update
            supervisor.step()

            for zone, robot in self.robots.items():
                if not robot.registered_ready:
                    if robot.robot_ready():
                        print(f"Robot in zone {zone} is ready.")
                        # Log only once per robot when ready
                        robot.registered_ready = True
                    else:
                        all_ready = False
            if all_ready:
                break
        else:
            pending_robots = ', '.join([
                str(zone)
                for zone, robot in self.robots.items()
                if not robot.robot_ready()
            ])
            raise TimeoutError(
                f"Robots in zones {pending_robots} failed to initialise. "
                f"Failed to reach wait_start() within {timeout} seconds."
            )

    def start_robots(self) -> None:
        """Signal to all robots that their start buttons have been pressed."""
        for robot in self.robots.values():
            robot.start_robot()


def is_dev_mode() -> bool:
    """Load the mode file and check if we are in dev mode."""
    return (get_game_mode() == 'dev')


@contextmanager
def record_animation(filename: Path) -> Iterator[None]:
    """Record an animation for the duration of the manager."""
    filename.parent.mkdir(parents=True, exist_ok=True)
    print(f"Saving animation to {filename}")
    supervisor.animationStartRecording(str(filename))
    yield
    supervisor.animationStopRecording()  # type: ignore[no-untyped-call]


@contextmanager
def record_video(
    filename: Path,
    resolution: tuple[int, int],
    skip: bool = False
) -> Iterator[None]:
    """Record a video for the duration of the manager."""
    filename.parent.mkdir(parents=True, exist_ok=True)

    if skip:
        print('Not recording movie')
        yield
        return
    else:
        print(f"Saving video to {filename}")

    supervisor.movieStartRecording(
        str(filename),
        width=resolution[0],
        height=resolution[1],
        quality=100,
        codec=0,
        acceleration=1,
        caption=False,
    )
    yield
    supervisor.movieStopRecording()  # type: ignore[no-untyped-call]

    while not supervisor.movieIsReady():  # type: ignore[no-untyped-call]
        time.sleep(0.1)

    if supervisor.movieFailed():  # type: ignore[no-untyped-call]
        print("Movie failed to record")


def save_image(filename: Path) -> None:
    """Capture an image of the arena."""
    filename.parent.mkdir(parents=True, exist_ok=True)
    print(f"Saving image to {filename}")
    supervisor.exportImage(str(filename), 100)


def run_match(
    match_duration: int,
    media_path_stem: Path,
    video_resolution: tuple[int, int],
    skip_video: bool,
) -> None:
    """Run a match in the arena."""
    robots = Robots()
    robots.remove_unoccupied_robots()
    robots.preset_robots()

    # TODO check for required libraries?

    robots.wait_for_ready(5)

    with record_animation(media_path_stem.with_suffix('.html')):
        # Animations don't support lighting changes so start the animation before
        # setting the lighting. Step the simulation to allow the animation to start.
        supervisor.step()
        # TODO set initial lighting
        with record_video(media_path_stem.with_suffix('.mp4'), video_resolution, skip_video):
            print("===========")
            print("Match start")
            print("===========")

            # We are ready to start the match now. "Press" the start button on the robots
            robots.start_robots()
            supervisor.simulationSetMode(Supervisor.SIMULATION_MODE_FAST)  # type: ignore[attr-defined]

            time_step = int(supervisor.getBasicTimeStep())
            match_timesteps = (match_duration * 1000) // time_step
            for _ in range(match_timesteps):
                supervisor.step(time_step)
                # TODO service lighting controller

            print("==================")
            print("Game over, pausing")
            print("==================")
            supervisor.simulationSetMode(Supervisor.SIMULATION_MODE_PAUSE)  # type: ignore[attr-defined]

        # To allow for a clear image of the final state, we reset the lighting first
        # TODO set lighting for match end photo
        # Step while paused to allow the lighting to update
        supervisor.step(0)
        save_image(media_path_stem.with_suffix('.jpg'))
        # TODO score match


def main() -> None:
    """Run the competition supervisor."""
    if is_dev_mode():
        exit()

    match_data = get_match_data()
    match_id = get_match_identifier()

    prefix_and_tee_streams(
        environment.ARENA_ROOT / f'supervisor-log-{match_id}.txt',
        prefix=lambda: f'[{supervisor.getTime():0.3f}] ',
    )

    try:
        run_match(
            match_data.match_duration,
            environment.ARENA_ROOT / 'recordings' / match_id,
            video_resolution=match_data.video_resolution,
            skip_video=(not match_data.video_enabled),
        )
        # Set the overall Webots exit code to follow the supervisor's exit code
    except Exception as e:
        # Print and step so error is printed to console
        print(f"Error: {e}")
        supervisor.step()
        supervisor.simulationQuit(1)
        raise
    else:
        supervisor.simulationQuit(0)


# lighting
# scoring


if __name__ == '__main__':
    main()
