# Minimum Vertex Cover on Zachary's Karate Club Network

This COMP6701 mini-project evaluates a maximal-matching 2-approximation algorithm for **Minimum Vertex Cover** on a real social network. An exact branch-and-bound algorithm determines the optimum for comparison, and a highest-residual-degree heuristic provides a second baseline.

The graph has **34 vertices and 78 undirected edges**. The exact optimum is **14 vertices**. In the fixed edge order, the 2-approximation returns **22 vertices**, giving a ratio of **22/14 = 1.571**. Across 1,000 seeded edge orders, the 2-approximation returns covers of **16–26 vertices**. Every cover is valid and satisfies the theoretical limit of **2 × OPT = 28**.

## Files

| File | Description |
| --- | --- |
| `vertex_cover_experiment.py` | Input graph, algorithms, validation, timing, and random edge-order experiment |
| `results.json` | Saved detailed results, including selected vertices and the edge-order summary |
| `results.csv` | Compact comparison of the three algorithms |

## Environment and quick start

The experiment requires **Python 3.9 or newer** and uses **only the Python standard library**. No package installation, API key, or external dataset download is needed.

```bash
git clone https://github.com/TTToGAo/COMP6701_MiniProject.git
cd COMP6701_MiniProject
python3 vertex_cover_experiment.py
```

On a Windows installation where `python3` is unavailable, use `python vertex_cover_experiment.py` instead.

The command prints a JSON summary and writes `results.json` and `results.csv` in the same directory. It overwrites the saved copies of those two files. The code validates the graph's vertex and edge counts and checks that each returned vertex set covers every edge.

## What the experiment does

1. **Maximal-matching 2-approximation.** Scan the edges in lexicographic order. Select an edge if neither endpoint has been matched, then return both endpoints of every selected edge. The matching is maximal, so the returned set covers every edge. If the matching has size `|M|`, any vertex cover needs at least `|M|` vertices, while the algorithm returns exactly `2|M|`. Thus `ALG ≤ 2 OPT` for every edge order. The scan takes `O(|V| + |E|)` time.
2. **Highest-residual-degree heuristic.** Repeatedly select the vertex incident to the most uncovered edges. It is an empirical baseline; this experiment does not claim a worst-case approximation guarantee for it.
3. **Exact branch-and-bound solver.** On an uncovered edge `{u, v}`, branch on including `u` or `v`; prune branches using a maximal-matching lower bound. Its worst-case time is exponential. Here it establishes `OPT = 14` on the small input graph.
4. **Order sensitivity.** Shuffle the edge list 1,000 times using seed `6701`, rerun the maximal-matching algorithm, and summarize the resulting cover sizes.

The saved results include all selected vertex sets, the matching used by the fixed-order approximation, validity flags, the exact solver's recursive-call count, and timing measurements. Running times depend on the computer and Python runtime; the cover sizes and validity checks are the meaningful reproducible outcomes.

## Data source

The script embeds the public Karate Club adjacency matrix used by NetworkX, based on W. W. Zachary's 1977 study. A positive matrix entry denotes an undirected social tie. Edge weights are ignored because the experiment studies **unweighted** vertex cover. Vertices are numbered 1–34.

- W. W. Zachary, “An Information Flow Model for Conflict and Fission in Small Groups,” *Journal of Anthropological Research*, 33(4), 452–473, 1977. DOI: 10.1086/jar.33.4.3629752.
- NetworkX Karate Club graph data: https://github.com/networkx/networkx/blob/main/networkx/generators/social.py.

## Scope

The experiment uses one small network. Its measured runtimes and observed approximation ratios do not establish behavior on larger or structurally different graphs.
