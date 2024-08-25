import math

positions_and_radii = [
    ((-3.770, 2.430), 1.15),
    ((-2.571, 1.591), 0.975),
    ((-2.446, 5.291), 0.8),
    ((-2.877, 4.277), 0.7),
    ((-3.628, 4.777), 0.575),
    ((-4.017, 4.220), 0.45),
    ((-4.439, 4.290), 0.375),
    ((-4.740, 4.196), 0.275),
]

for (x, y), r in positions_and_radii:
    print(
    f"""Pose {{
  translation {x:.4f} {y:.4f} -0.5
  children [
    Shape {{
      geometry Cylinder {{
        radius {r:.4f}
        height 1
      }}
    }}
  ]
}}""")