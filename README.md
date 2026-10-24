# BetterGoogleMapsConcept

> **Main repo:** https://github.com/Darshcmd/BetterGoogleMaps  
> **Author & sole contributor:** Darsh (GitHub: [@Darshcmd](https://github.com/Darshcmd))

A simulation-based comparison of **traditional Google Maps–style routing** vs a **dynamic, congestion-aware "Better Google Maps"** routing algorithm. Maintained as `BetterGoogleMapsConcept`.

---

## 🎯 What this project does

Most navigation apps (Google Maps, Apple Maps, Waze) compute a single "best" route from A → B using Dijkstra's algorithm **once** at the start of the trip, then stick to that route even if road conditions change mid-journey.

This project simulates two approaches side-by-side on the same road network with the same set of travelers:

| Approach | Behavior |
|----------|----------|
| **Google Maps** (`google_maps`) | Computes one Dijkstra path per person upfront. As each edge is traversed, its cost is incremented (simulating congestion the traveler adds to that road). The traveler continues along the precomputed route regardless. |
| **Better Google Maps** (`better_google_maps`) | Recomputes Dijkstra **from the current position** to the destination every time an edge finishes being traversed, using the *live* edge costs. This means travelers dynamically reroute around roads that have become congested by other travelers. |

The shared `simulator` runs a discrete time-step loop where every traveler has a `limbo` counter equal to the time it takes to cross the current road. It reports:

- **System age** — total simulated time until everyone reaches their destination
- **Average time taken per person** — the headline metric for comparing the two algorithms

In the bundled demos, **Better Google Maps consistently achieves a lower average travel time per person** because it adapts to live congestion instead of blindly following a static route.


---

## 📁 Repository structure

```
BetterGoogleMapsConcept/
├── README.md                 # This file
├── demo.sh                   # 3-step demo script (zsh)
├── requirements.txt          # Python dependencies
├── trial.py                  # Main comparison: Google Maps vs Better Google Maps
├── distributedDijkstra.py    # Core algorithms (simulator, google_maps, better_google_maps, dijkstra)
├── plot_graph.py             # Static graph visualization (matplotlib + networkx)
├── test_graphs/              # Sample road-network CSV files (from,to,cost)
│   ├── graph.csv … graph7.csv
│   ├── google_graph.txt
│   └── google_graph_detailed.txt
├── test_persons/             # Sample traveler CSV files (start,end)
│   ├── people5.csv … people8.csv
│   ├── google_people.txt
│   └── start_end_*.txt
├── utils/
│   ├── Graph.py              # Undirected weighted graph loaded from CSV
│   ├── Person.py             # Traveler agent (start, end, path, age, limbo, …)
│   ├── heap.py               # Custom binary heap used by Dijkstra
│   ├── draw.py               # Matplotlib graph drawing
│   ├── google_graph_writer.py# Fetches real route data from Google Maps API
│   └── google_graph_plotter.py# Interactive route map (Bokeh, tile map)
└── graph_img_outputs/        # Generated graph images
```

---

## 🔧 Core algorithms

### `dijkstra(graph, start, end)` — `distributedDijkstra.py:117`
Standard Dijkstra's shortest-path using a custom min-heap (`SpecialMinHeap`). Returns `(total_distance, path)`.

### `google_maps(graph, everyone)` — `distributedDijkstra.py:46`
1. For every traveler, compute a single Dijkstra path from `start` → `end` at time 0.
2. Each time-step, increment each active traveler's `age`.
3. When a traveler finishes crossing an edge (`limbo` hits 0), increment that edge's cost by 1 (congestion) and move to the next node on the **precomputed** path.

### `better_google_maps(graph, everyone)` — `distributedDijkstra.py:79`
1. Each time-step, increment each active traveler's `age`.
2. When a traveler finishes crossing an edge, **recompute Dijkstra** from the current node to `end` using live edge costs, then continue from there.
3. The traversed edge's cost is incremented (congestion) as before.

### `simulator(graph, everyone)` — `distributedDijkstra.py:11`
Discrete-event time loop:
- `system_age` ticks up by 1 each round.
- Every unfinished traveler ages by 1.
- Travelers cross edges one tick at a time via `limbo`.

---

## 🚀 Getting started

### Prerequisites

Python 3.8+ and the packages in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Dependencies:
- `numpy` — numerical arrays / infinity constants
- `networkx` — graph drawing
- `matplotlib` — static plots
- `requests` — Google Maps API calls (live mode only)
- `bokeh` — interactive route maps

### Option 1: Quick comparison (sample data)

```bash
python3 trial.py
```

Output example:
```
GOOGLE PATHS:
Avg Time Taken/Person for Google Maps: 14.2

DARSH PATHS:
Avg Time Taken/Person for BetterGoogleMaps Maps: 11.8
```

### Option 2: Full demo (3 steps + bonus map)

```bash
chmod +x demo.sh
./demo.sh
```

What `demo.sh` does:
1. **Step 1** — Plots a sample bidirectional graph with matplotlib (close the window to continue).
2. **Step 2** — Runs `trial.py` on a simulated city (~108 roads, 5,000 people), printing average travel times for Google Maps vs Better Google Maps.
3. **Step 3** — Runs `distributedDijkstra.py` on real Google Maps data for Mumbai (100 people).
4. **Bonus** — Generates `utils/google_graph_plotter.html`, an interactive route map on a real tile base layer (no API key needed; falls back to cached data).

### Option 3: Live Google Maps data

`utils/google_graph_writer.py` can fetch live routes from the Google Maps Directions API between two locations and write `test_graphs/google_graph_detailed.txt` + `test_persons/google_people.txt`.

```python
from utils.google_graph_writer import write_google_graph
write_google_graph("Four Seasons Hotel, Mumbai", "Dhirubhai Ambani International School, Mumbai")
```

> ⚠️ Live mode requires a valid Google Maps API key. The default key in the source may be expired/invalid; if so, the code falls back to the cached graph data under `test_graphs/`.

---

## 📊 Data formats

### Road network (`test_graphs/*.csv`)
Comma-separated, no header. Each row is one undirected road:

```
from_node,to_node,travel_cost
1,2,4
2,3,4
3,4,5
```

`Graph.__init__` reads this into an adjacency dict where `edges[a][b] == edges[b][a] == cost`.

### Travelers (`test_persons/*.csv`)
Comma-separated, no header. Each row is one person:

```
start_node,end_node
72,15
26,23
8,23
```

`Person(start, end)` initializes an agent at `start_node` trying to reach `end_node`.

---

## 🧠 How to read the results

- **Lower average time per person = better.**
- Because `better_google_maps` re-optimizes whenever a road segment finishes, it naturally avoids edges that other travelers have just congested. Over many travelers this typically reduces total system age and mean commute time compared to the static `google_maps` approach.
- Try swapping graph files (`graph7.csv`, `graph5.csv`, etc.) and person files to experiment with different city sizes and densities.

---

## 🛠 Extending the project

- **Add a new graph:** create `test_graphs/my_graph.csv` in `from,to,cost` format, then point `trial.py` or `plot_graph.py` at it.
- **Add a new routing strategy:** write a function with the same signature as `google_maps(graph, everyone)` / `better_google_maps(graph, everyone)` and pass it to `simulator(graph, strategy(graph, people))`.
- **Visualize a graph:** run `python3 plot_graph.py` or import `plot_graph` from `plot_graph.py`.
- **Plot real routes on a map:** run `python3 -m utils.google_graph_plotter` — opens `utils/google_graph_plotter.html` in your browser.

---

## 📜 License

This project is maintained by Darsh (@Darshcmd) for educational and demonstration purposes.

---

## 🔗 Link

- This repository: https://github.com/Darshcmd/BetterGoogleMapsConcept
