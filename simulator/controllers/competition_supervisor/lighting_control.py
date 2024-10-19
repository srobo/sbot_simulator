"""
The controller for altering arena lighting provided by a DirectionalLight and a Background.

Currently doesn't support:
- Timed pre-match lighting changes
"""
from __future__ import annotations

from typing import NamedTuple

from controller import Node, Supervisor

MATCH_LIGHTING_INTENSITY = 1.5
DEFAULT_LUMINOSITY = 1


class FromEnd(NamedTuple):
    """
    Represents a time relative to the end of the match.

    Negative values are times before the end of the match. 0 is the last frame
    of the video. All positive values will only appear in the post-match image.
    """

    time: float


class ArenaLighting(NamedTuple):
    """Represents a lighting configuration for the arena."""

    light_def: str
    intensity: float
    colour: tuple[float, float, float] = (1, 1, 1)


class LightingEffect(NamedTuple):
    """Represents a lighting effect to be applied to the arena."""

    start_time: float | FromEnd
    fade_time: float | None = None
    lighting: ArenaLighting = ArenaLighting('SUN', intensity=MATCH_LIGHTING_INTENSITY)
    luminosity: float = DEFAULT_LUMINOSITY
    name: str = ""

    def __repr__(self) -> str:
        light = self.lighting
        lights_info = [
            f"({light.light_def}, int={light.intensity}, col={light.colour})"
        ]
        return (
            f"<LightingEffect: {self.name!r}, "
            f"start={self.start_time}, fade={self.fade_time}, "
            f"lum={self.luminosity}, "
            f"{', '.join(lights_info)}"
            ">"
        )


class LightingStep(NamedTuple):
    """Represents a step in a lighting fade."""

    timestep: int
    light_node: Node
    intensity: float | None
    colour: tuple[float, float, float] | None
    luminosity: float | None
    name: str | None = None


CUE_STACK = [
    LightingEffect(
        0,
        lighting=ArenaLighting('SUN', intensity=0.2),
        luminosity=0.05,
        name="Pre-set",
    ),
    LightingEffect(
        0,
        fade_time=1.5,
        lighting=ArenaLighting('SUN', intensity=MATCH_LIGHTING_INTENSITY),
        luminosity=1,
        name="Fade-up",
    ),
    LightingEffect(
        FromEnd(0),  # This time runs this cue as the last frame of the video
        lighting=ArenaLighting('SUN', intensity=1, colour=(0.8, 0.1, 0.1)),
        luminosity=0.1,
        name="End of match",
    ),
    LightingEffect(
        FromEnd(1),
        lighting=ArenaLighting('SUN', intensity=MATCH_LIGHTING_INTENSITY),
        luminosity=DEFAULT_LUMINOSITY,
        name="Post-match image",
    ),
]


class LightingControl:
    """Controller for managing lighting effects in the arena."""

    def __init__(self, supervisor: Supervisor, duration: int) -> None:
        self._robot = supervisor
        self._final_timestep = duration
        self.timestep = self._robot.getBasicTimeStep()
        self.ambient_node = supervisor.getFromDef('AMBIENT')

        # fetch all nodes used in effects, any missing nodes will be flagged here
        light_names = set(effect.lighting.light_def for effect in CUE_STACK)
        self.lights = {
            name: supervisor.getFromDef(name)
            for name in light_names
        }
        missing_lights = [name for name, light in self.lights.items() if light is None]
        if missing_lights:
            raise ValueError(f"Missing light nodes: {missing_lights}")

        # Convert FromEnd times to absolute times
        cue_stack = self.convert_from_end_times(CUE_STACK)

        self.lighting_steps = self.generate_lighting_steps(cue_stack)

    def convert_from_end_times(self, cue_stack: list[LightingEffect]) -> list[LightingEffect]:
        """Convert FromEnd times to absolute times."""
        new_cue_stack = []
        end_time = (self._final_timestep * self.timestep) / 1000
        # @ 25 fps the last 5 timesteps are not included in the video
        start_of_frame_offset = self.timestep * 6 / 1000
        for cue in cue_stack:
            if isinstance(cue.start_time, FromEnd):
                abs_time = end_time + cue.start_time.time - start_of_frame_offset
                new_cue_stack.append(cue._replace(start_time=abs_time))
            else:
                new_cue_stack.append(cue)

        return new_cue_stack

    def generate_lighting_steps(self, cue_stack: list[LightingEffect]) -> list[LightingStep]:
        """Expand the cue stack into a list of lighting steps."""
        steps: list[LightingStep] = []

        # Generate current values for all lights
        current_values = {
            name: LightingStep(
                0,
                light,
                light.getField('intensity').getSFFloat(),  # type: ignore[attr-defined]
                light.getField('color').getSFColor(),  # type: ignore[attr-defined]
                0,
            )
            for name, light in self.lights.items()
        }
        current_luminosity = self.ambient_node.getField('luminosity').getSFFloat()  # type: ignore[attr-defined]

        for cue in cue_stack:
            # Get the current state of the light with the current luminosity
            current_state = current_values[cue.lighting.light_def]
            current_state = current_state._replace(luminosity=current_luminosity)

            expanded_cue = self.expand_lighting_fade(cue, current_state)

            # Update current values from the last step of the cue
            current_values[cue.lighting.light_def] = expanded_cue[-1]
            current_luminosity = expanded_cue[-1].luminosity

            steps.extend(expanded_cue)

        steps.sort(key=lambda x: x.timestep)
        # TODO optimise steps to remove duplicate steps

        return steps

    def expand_lighting_fade(
        self,
        cue: LightingEffect,
        current_state: LightingStep,
    ) -> list[LightingStep]:
        """Expand a fade effect into a list of steps."""
        fades = []

        assert isinstance(cue.start_time, (float, int)), \
            "FromEnd times should be converted to absolute times"
        cue_start = int((cue.start_time * 1000) / self.timestep)

        if cue.fade_time is None:
            # no fade, just set values
            return [LightingStep(
                cue_start,
                self.lights[cue.lighting.light_def],
                cue.lighting.intensity,
                cue.lighting.colour,
                cue.luminosity,
                cue.name
            )]

        assert current_state.intensity is not None, "Current intensity should be set"
        assert current_state.colour is not None, "Current colour should be set"
        assert current_state.luminosity is not None, "Current luminosity should be set"

        fade_steps = int((cue.fade_time * 1000) / self.timestep)
        if fade_steps == 0:
            fade_steps = 1
        intensity_step = (cue.lighting.intensity - current_state.intensity) / fade_steps
        colour_step = [
            (cue.lighting.colour[0] - current_state.colour[0]) / fade_steps,
            (cue.lighting.colour[1] - current_state.colour[1]) / fade_steps,
            (cue.lighting.colour[2] - current_state.colour[2]) / fade_steps,
        ]
        luminosity_step = (cue.luminosity - current_state.luminosity) / fade_steps

        for step in range(fade_steps):
            fades.append(
                LightingStep(
                    cue_start + step,
                    self.lights[cue.lighting.light_def],
                    current_state.intensity + intensity_step * step,
                    (
                        current_state.colour[0] + (colour_step[0] * step),
                        current_state.colour[1] + (colour_step[1] * step),
                        current_state.colour[2] + (colour_step[2] * step),
                    ),
                    current_state.luminosity + luminosity_step * step,
                    cue.name if step == 0 else None,
                )
            )

        # Replace the last step with the final values
        fades.pop()
        fades.append(LightingStep(
            cue_start + fade_steps,
            self.lights[cue.lighting.light_def],
            cue.lighting.intensity,
            cue.lighting.colour,
            cue.luminosity,
        ))

        return fades

    def set_luminosity(self, luminosity: float) -> None:
        """Set the luminosity of the ambient node."""
        self.ambient_node.getField('luminosity').setSFFloat(float(luminosity))  # type: ignore[attr-defined]

    def set_node_intensity(self, node: Node, intensity: float) -> None:
        """Set the intensity of a node."""
        node.getField('intensity').setSFFloat(float(intensity))  # type: ignore[attr-defined]

    def set_node_colour(self, node: Node, colour: tuple[float, float, float]) -> None:
        """Set the colour of a node."""
        node.getField('color').setSFColor(list(colour))  # type: ignore[attr-defined]

    def service_lighting(self, current_timestep: int) -> int:
        """Service the lighting effects for the current timestep."""
        index = 0

        if current_timestep >= self._final_timestep and self.lighting_steps:
            # Run all remaining steps
            current_timestep = self.lighting_steps[-1].timestep

        while (
            len(self.lighting_steps) > index
            and self.lighting_steps[index].timestep == current_timestep
        ):
            lighting_step = self.lighting_steps[index]
            if lighting_step.name is not None:
                print(
                    f"Running lighting effect: {lighting_step.name} @ "
                    f"{current_timestep * self.timestep / 1000}"
                )

            if lighting_step.intensity is not None:
                self.set_node_intensity(lighting_step.light_node, lighting_step.intensity)

            if lighting_step.colour is not None:
                self.set_node_colour(lighting_step.light_node, lighting_step.colour)

            if lighting_step.luminosity is not None:
                self.set_luminosity(lighting_step.luminosity)

            index += 1

        # Remove all steps that have been processed
        self.lighting_steps = self.lighting_steps[index:]

        if self.lighting_steps:
            return self.lighting_steps[0].timestep - current_timestep
        else:
            return -1
