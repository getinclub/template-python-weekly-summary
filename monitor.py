"""Informational synthetic weekly report monitor."""
from weekly_summary import merge_groups

TEAMS = ((2, 10.0, 2.0), (6, 20.0, 6.0))
EXPECTED = (8, 17.5, 158.0)


def display(summary):
    n, mean, m2 = summary
    variance = f"{m2 / n:.2f}" if n else "n/a"
    return f"count={n} mean={mean:.2f} population variance={variance}"


if __name__ == "__main__":
    result = merge_groups(*TEAMS)
    print("Two synthetic team summaries imported; both valid")
    print("Observed:", display(result))
    print("Expected:", display(EXPECTED))
    print("MATCH" if result == EXPECTED else "MISMATCH: merged weekly summary differs")
