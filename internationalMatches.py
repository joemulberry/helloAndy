def international_appearance_points(rank: int, percentage_played: float) -> int:
    """
    Return FA Men's GBE 2025/26 International Appearances points based on FIFA rank and
    percentage of competitive senior internationals in the last 24 months.
    Returns 15 for Auto-Pass entries, or an integer points value (0–10) otherwise.
    """
    percentage_played = percentage_played* 100
    # Clamp percentage into [0, 100]
   
    p = max(0.0, min(100.0, float(percentage_played)))

    def band_1_10(pct: float) -> int:
        if 90 <= pct <= 100: return 15
        if 80 <= pct < 90:  return 15
        if 70 <= pct < 80:  return 15
        if 60 <= pct < 70:  return 15
        if 50 <= pct < 60:  return 15
        if 40 <= pct < 50:  return 15
        if 30 <= pct < 40:  return 15
        if 20 <= pct < 30:  return 10
        if 10 <= pct < 20:  return 9
        if 1  <= pct < 10:  return 8
        return 0

    def band_11_20(pct: float) -> int:
        if 90 <= pct <= 100: return 15
        if 80 <= pct < 90:  return 15
        if 70 <= pct < 80:  return 15
        if 60 <= pct < 70:  return 15
        if 50 <= pct < 60:  return 15
        if 40 <= pct < 50:  return 15
        if 30 <= pct < 40:  return 10
        if 20 <= pct < 30:  return 9
        if 10 <= pct < 20:  return 8
        if 1  <= pct < 10:  return 7
        return 0

    def band_21_30(pct: float) -> int:
        if 90 <= pct <= 100: return 15
        if 80 <= pct < 90:  return 15
        if 70 <= pct < 80:  return 15
        if 60 <= pct < 70:  return 15
        if 50 <= pct < 60:  return 10
        if 40 <= pct < 50:  return 9
        if 30 <= pct < 40:  return 8
        if 20 <= pct < 30:  return 7
        # 0 points below 20%
        return 0

    def band_31_50(pct: float) -> int:
        if 90 <= pct <= 100: return 15
        if 80 <= pct < 90:  return 15
        if 70 <= pct < 80:  return 15
        if 60 <= pct < 70:  return 10
        if 50 <= pct < 60:  return 8
        if 40 <= pct < 50:  return 7
        if 30 <= pct < 40:  return 6
        # 0 points below 30%
        return 0

    def band_51_plus(pct: float) -> int:
        if 90 <= pct <= 100: return 2
        if 80 <= pct < 90:  return 1
        # 0 points otherwise
        return 0
    
    print('rank', rank, 'pPlayed', p)

    if 1 <= rank <= 10:
        return band_1_10(p)
    if 11 <= rank <= 20:
        return band_11_20(p)
    if 21 <= rank <= 30:
        return band_21_30(p)
    if 31 <= rank <= 50:
        return band_31_50(p)
    # 51+
    return band_51_plus(p)