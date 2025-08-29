

def international_appearance_points(rank: int, percentage_played: float) -> int:
    """
    Returns the points for international appearance based on FIFA rank and percentage played.
    Returns -1 for Auto-Pass, 0 for no points, or integer points.
    """
    # Define ranking bands and corresponding point tables
    # Each band: [(min_percent, max_percent, points or -1 for Auto-Pass)]
    bands = [
        # 1–10
        (range(1, 11), [
            (90, 100, -1),  # Auto-Pass
            (80, 89, 15),
            (70, 79, 10),
            (60, 69, 7),
            (50, 59, 5),
        ]),
        # 11–20
        (range(11, 21), [
            (90, 100, -1),  # Auto-Pass
            (80, 89, 13),
            (70, 79, 10),
            (60, 69, 7),
            (50, 59, 4),
        ]),
        # 21–30
        (range(21, 31), [
            (90, 100, 12),
            (80, 89, 10),
            (70, 79, 7),
            (60, 69, 5),
            (50, 59, 3),
        ]),
        # 31–50
        (range(31, 51), [
            (90, 100, 10),
            (80, 89, 8),
            (70, 79, 6),
            (60, 69, 4),
            (50, 59, 2),
        ]),
        # 51+
        (range(51, 1000), [  # 1000 is arbitrary large number
            (90, 100, 6),
            (80, 89, 5),
            (70, 79, 4),
            (60, 69, 2),
            (50, 59, 1),
        ]),
    ]

    # Find which band the rank falls in
    for band_range, thresholds in bands:
        if rank in band_range:
            for min_p, max_p, pts in thresholds:
                if min_p <= percentage_played <= max_p:
                    return pts
            return 0  # No points for <50%
    return 0  # Out of band (shouldn't happen)