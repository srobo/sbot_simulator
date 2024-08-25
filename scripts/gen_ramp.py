import math

positions = [
    (-0.282396, 5.82031148),
    (0.96760445, 5.82031148),
    (1.26760445, 5.68041918),
    (3.61453948, 2.88345093),
    (4.04794540, 2.54483711),
    (4.49734242, 2.32565154),
    (4.88546071, 2.22888278),
    (5.38515612, 2.21143303),
    (5.92680039, 2.30693953),
    (6.48311070, 2.53170349),
]

def rotate(point: tuple[float,float], angle: float) -> tuple[float, float]:
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    px, py = point
    qx =  math.cos(angle) * px - math.sin(angle) * py
    qy = math.sin(angle) * px + math.cos(angle) * py
    return qx, qy

for i, (y, z) in enumerate(positions):
    if i == 0:
        continue

    (prev_y, prev_z) = positions[i - 1]

    y_diff, z_diff = y - prev_y, z - prev_z

    ang = math.atan2(z_diff, y_diff)

    tangent_ang = ang + math.pi / 2

    length = math.sqrt(y_diff ** 2 + z_diff ** 2)
    depth = 1

    offset = rotate((-depth / 2, 0), tangent_ang)
    mid_ramp = (prev_y + y_diff / 2 + offset[0], prev_z + z_diff / 2 + offset[1])

    print(
    f"""Pose {{
  translation 0 {mid_ramp[0]:.4f} {mid_ramp[1]:.4f}
  rotation 1 0 0 {ang:.4f}
  children [
    Shape {{
      geometry Box {{
        size 1.5 {length:.4f} {depth:.4f}
      }}
    }}
  ]
}}""")