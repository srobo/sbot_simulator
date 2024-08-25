import math

diameter = 1.5
ramp_angle = 0.321750554397

circle_positions_heights = [
    ((0,0,0), 2),
    ((-1.555635, 1.555635, -0.25), 1.75),
    ((0, 3.11127, -0.5), 1.5),
    ((2.2, 3.11127, -0.75), 1.25),
]

marker_angles = list(x*0.785398163+3.14159265 for x in range(8))
marker_distance = 1.6-0.005
marker_height_offset = 0.2


ramp_w_l_h = (0.6, 0.743, 1)
marked_positions = [None, 3, 5, 6]

platform_joiner_length = 0.063
platform_joiner_width = 0.6

ramp_positions_angles = [
    ((-0.7778, 0.7778, -0.125), -2.35619449),
    ((-0.7778, 2.3335, -0.375), 2.35619449),
    ((1.1, 3.1113, -0.625), 1.57079632679),
    ((1.4222, 3.8891, -0.875), -2.35619449),
]

next_joiner_angles = [
    -math.pi/4,
    math.pi/4,
    math.pi/2,
    -math.pi/4
]

prev_joiner_angles = [
    None,
    math.pi-math.pi/4,
    -(3/4)*math.pi,
    -(1/2)*math.pi,
]

def do_pillars() -> None:
    print("""DEF PILLARS Group {
  children [""")
    for i, ((x, y, z), h) in enumerate(circle_positions_heights):
        platform_joiner_distance = diameter / 2 - platform_joiner_length / 2
        extra_shapes = ""
        platform_angle = prev_joiner_angles[i]
        if platform_angle:
            platform_joiner_pos = _rotate(platform_angle, platform_joiner_distance)
            extra_shapes += f"""
            Pose {{
              translation {platform_joiner_pos[0]} {platform_joiner_pos[1]} 0
              rotation 0 0 -1 {platform_angle}
              children [
                Shape {{
                  appearance PBRAppearance {{
                    roughness 1
                    metalness 0
                  }}
                  geometry Box {{
                    size {platform_joiner_width} {platform_joiner_length} {h - 0.005}
                  }}
                }}
              ]
            }}"""

        platform_angle = next_joiner_angles[i]
        platform_joiner_pos = _rotate(platform_angle, platform_joiner_distance)
        extra_shapes += f"""
            Pose {{
              translation {platform_joiner_pos[0]} {platform_joiner_pos[1]} 0
              rotation 0 0 -1 {platform_angle}
              children [
                Shape {{
                  appearance PBRAppearance {{
                    roughness 1
                    metalness 0
                  }}
                  geometry Box {{
                    size {platform_joiner_width} {platform_joiner_length} {h - 0.005}
                  }}
                }}
              ]
            }}"""

        print(
        f"""    Solid {{
      translation {x:.4f} {y:.4f} {z-(h/2):.4f}
      children [
        DEF PILLAR Group {{
          children [
            Shape {{
              appearance PBRAppearance {{
                roughness 1
                metalness 0
              }}
              geometry Cylinder {{
                radius {diameter / 2:.4f}
                height {h}
              }}
            }}
            {extra_shapes}
          ]
        }}
      ]
      contactMaterial "floor"
      name "pillar {i}"
      boundingObject USE PILLAR
      locked TRUE
    }}""")
    print("""  ]
}""")

def do_ramps() -> None:
    for i,((x, y, z), bearing) in enumerate(ramp_positions_angles):
        print(f"""Solid {{
    translation {x:.4f} {y:.4f} {z:.4f}
    rotation 0 0 1 {bearing:.4f}
    boundingObject Pose {{
        translation 0 {ramp_w_l_h[2]/2 * math.sin(ramp_angle)} {-ramp_w_l_h[2]/2 * math.cos(ramp_angle)}
        rotation 1 0 0 {ramp_angle:.4f}
        children [
            Shape {{
                geometry Box {{
                    size {ramp_w_l_h[0]} {ramp_w_l_h[1]} {ramp_w_l_h[2]}
                }}
            }}
        ]
    }}
    locked TRUE
    name "Ramp {i}"
}}""")

def _rotate(angle: float, dist: float) -> tuple[float, float]:
    return dist * math.sin(angle), dist * math.cos(angle)

def do_markers() -> None:
    counter = 0
    for i, ((x, y, z), h) in enumerate(circle_positions_heights):
        for j, a in enumerate(marker_angles):
            if marked_positions[i] != j:
                continue
            pos = _rotate(a, marker_distance)
            print(f"""Marker {{
    translation {x + pos[0]:.4f} {y + pos[1]:.4f} {z + marker_height_offset:.4f}
    rotation 0 0 -1 {a}
    upright TRUE
    size 0.08 0.08
    texture_url ["sim_markers/{counter}.png"]
    model "{counter}"
}}""")
            counter += 1

if __name__ == "__main__":
    do_pillars()