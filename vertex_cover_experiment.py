"""Minimum Vertex Cover experiments on Zachary's Karate Club network.

The program uses only the Python standard library.  It implements:
1. the maximal-matching 2-approximation taught in COMP6701;
2. a highest-residual-degree greedy heuristic;
3. an exact branch-and-bound solver used only as an experimental benchmark.

Run:
    python3 vertex_cover_experiment.py
"""

from __future__ import annotations

import csv
import json
import random
import statistics
import time
from pathlib import Path


# NetworkX's public Karate Club data matrix, derived from Zachary (1977).
# A positive entry denotes an undirected social tie; weights are ignored here.
KARATE_MATRIX = """
0 4 5 3 3 3 3 2 2 0 2 3 2 3 0 0 0 2 0 2 0 2 0 0 0 0 0 0 0 0 0 2 0 0
4 0 6 3 0 0 0 4 0 0 0 0 0 5 0 0 0 1 0 2 0 2 0 0 0 0 0 0 0 0 2 0 0 0
5 6 0 3 0 0 0 4 5 1 0 0 0 3 0 0 0 0 0 0 0 0 0 0 0 0 0 2 2 0 0 0 3 0
3 3 3 0 0 0 0 3 0 0 0 0 3 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
3 0 0 0 0 0 2 0 0 0 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
3 0 0 0 0 0 5 0 0 0 3 0 0 0 0 0 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
3 0 0 0 2 5 0 0 0 0 0 0 0 0 0 0 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
2 4 4 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
2 0 5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3 0 4 3
0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2
2 0 0 0 3 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
1 0 0 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
3 5 3 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3 2
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3 4
0 0 0 0 0 3 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
2 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 2
2 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3 1
2 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 5 0 4 0 2 0 0 5 4
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 0 3 0 0 0 2 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 5 2 0 0 0 0 0 0 7 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 4 0 0 0 2
0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 4 3 0 0 0 0 0 0 0 0 4
0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 0 2
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3 0 0 4 0 0 0 0 0 3 2
0 2 0 0 0 0 0 0 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3 3
2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 7 0 0 2 0 0 0 4 4
0 0 2 0 0 0 0 0 3 0 0 0 0 0 3 3 0 0 1 0 3 0 2 5 0 0 0 0 0 4 3 4 0 5
0 0 0 0 0 0 0 0 4 2 0 0 0 3 2 4 0 0 2 1 1 0 3 4 0 0 2 4 2 2 3 4 5 0
"""


def load_graph() -> tuple[set[int], set[tuple[int, int]]]:
    rows = [[int(x) for x in line.split()] for line in KARATE_MATRIX.strip().splitlines()]
    assert len(rows) == 34 and all(len(row) == 34 for row in rows)
    vertices = set(range(1, 35))
    # The published matrix is read as an undirected graph; accept a positive
    # entry in either triangular position, as NetworkX does when adding edges.
    edges = {
        (i + 1, j + 1)
        for i in range(34)
        for j in range(i + 1, 34)
        if rows[i][j] > 0 or rows[j][i] > 0
    }
    assert len(edges) == 78
    return vertices, edges


def is_vertex_cover(cover: set[int], edges: set[tuple[int, int]]) -> bool:
    return all(u in cover or v in cover for u, v in edges)


def maximal_matching_2approx(edges: set[tuple[int, int]], order=None) -> tuple[set[int], list[tuple[int, int]]]:
    ordered_edges = sorted(edges) if order is None else list(order)
    matched: set[int] = set()
    matching: list[tuple[int, int]] = []
    for u, v in ordered_edges:
        if u not in matched and v not in matched:
            matching.append((u, v))
            matched.update((u, v))
    return matched, matching


def highest_degree_greedy(vertices: set[int], edges: set[tuple[int, int]]) -> set[int]:
    remaining = set(edges)
    cover: set[int] = set()
    while remaining:
        degree = {v: 0 for v in vertices}
        for u, v in remaining:
            degree[u] += 1
            degree[v] += 1
        chosen = min(vertices, key=lambda v: (-degree[v], v))
        cover.add(chosen)
        remaining = {e for e in remaining if chosen not in e}
    return cover


def greedy_matching_lower_bound(edges: frozenset[tuple[int, int]]) -> int:
    """Size of any maximal matching is a valid lower bound on vertex cover."""
    used: set[int] = set()
    count = 0
    for u, v in sorted(edges):
        if u not in used and v not in used:
            used.update((u, v))
            count += 1
    return count


def exact_vertex_cover(vertices: set[int], edges: set[tuple[int, int]]) -> tuple[set[int], int]:
    """Exact branch-and-bound solver for this small benchmark graph."""
    incumbent = highest_degree_greedy(vertices, edges)
    best = set(incumbent)
    calls = 0

    def search(remaining: frozenset[tuple[int, int]], chosen: frozenset[int]) -> None:
        nonlocal best, calls
        calls += 1
        if not remaining:
            if len(chosen) < len(best):
                best = set(chosen)
            return
        if len(chosen) >= len(best):
            return
        if len(chosen) + greedy_matching_lower_bound(remaining) >= len(best):
            return

        degree: dict[int, int] = {}
        for a, b in remaining:
            degree[a] = degree.get(a, 0) + 1
            degree[b] = degree.get(b, 0) + 1
        u, v = max(remaining, key=lambda e: (degree[e[0]] + degree[e[1]], degree[e[0]], degree[e[1]], -e[0], -e[1]))
        # Every cover must contain u or v. Try the higher-degree endpoint first.
        if degree[v] > degree[u]:
            u, v = v, u
        for x in (u, v):
            reduced = frozenset(e for e in remaining if x not in e)
            search(reduced, chosen | {x})

    search(frozenset(edges), frozenset())
    assert is_vertex_cover(best, edges)
    return best, calls


def median_runtime_us(function, repetitions: int = 2000) -> float:
    samples = []
    for _ in range(7):
        start = time.perf_counter_ns()
        for _ in range(repetitions):
            function()
        samples.append((time.perf_counter_ns() - start) / repetitions / 1000)
    return statistics.median(samples)


def randomized_order_summary(edges: set[tuple[int, int]], trials: int = 1000, seed: int = 6701) -> dict[str, float]:
    rng = random.Random(seed)
    base = list(edges)
    sizes = []
    for _ in range(trials):
        rng.shuffle(base)
        cover, _ = maximal_matching_2approx(edges, base)
        sizes.append(len(cover))
    return {
        "trials": trials,
        "seed": seed,
        "minimum": min(sizes),
        "median": statistics.median(sizes),
        "mean": statistics.mean(sizes),
        "maximum": max(sizes),
    }


def main() -> None:
    output_dir = Path(__file__).resolve().parent
    vertices, edges = load_graph()

    approx_cover, matching = maximal_matching_2approx(edges)
    greedy_cover = highest_degree_greedy(vertices, edges)

    exact_start = time.perf_counter()
    exact_cover, calls = exact_vertex_cover(vertices, edges)
    exact_ms = (time.perf_counter() - exact_start) * 1000

    methods = [
        ("Exact branch-and-bound", exact_cover, exact_ms * 1000),
        ("Maximal-matching 2-approximation", approx_cover, median_runtime_us(lambda: maximal_matching_2approx(edges))),
        ("Highest-degree greedy", greedy_cover, median_runtime_us(lambda: highest_degree_greedy(vertices, edges))),
    ]
    optimum = len(exact_cover)
    results = []
    for name, cover, runtime_us in methods:
        valid = is_vertex_cover(cover, edges)
        assert valid
        results.append({
            "method": name,
            "cover_size": len(cover),
            "ratio_to_optimum": round(len(cover) / optimum, 4),
            "runtime_microseconds": round(runtime_us, 3),
            "valid_cover": valid,
            "vertices": sorted(cover),
        })

    random_summary = randomized_order_summary(edges)
    payload = {
        "dataset": "Zachary's Karate Club",
        "vertices": len(vertices),
        "edges": len(edges),
        "matching_size": len(matching),
        "matching": matching,
        "exact_search_calls": calls,
        "results": results,
        "random_edge_order_2approx": random_summary,
    }

    with (output_dir / "results.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    with (output_dir / "results.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["method", "cover_size", "ratio_to_optimum", "runtime_microseconds", "valid_cover"])
        writer.writeheader()
        for row in results:
            writer.writerow({k: row[k] for k in writer.fieldnames})

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
