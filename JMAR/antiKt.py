import math
import matplotlib.pyplot as plt


# ============================================================
# Toy anti-kT jet clustering playground
# ============================================================

R = 0.4


# ------------------------------------------------------------
# Input particles
#
# You can play with:
#   - pT
#   - eta
#   - phi
#
# Try moving C farther away, or making B very hard, etc.
# ------------------------------------------------------------

particles = [
    {"name": "A", "pt": 100.0, "eta": 0.00, "phi": 0.00, "constituents": ["A"]},
    {"name": "B", "pt": 10.0,  "eta": 0.10, "phi": 0.05, "constituents": ["B"]},
    {"name": "C", "pt": 5.0,   "eta": 0.25, "phi": 0.10, "constituents": ["C"]},
    {"name": "D", "pt": 50.0,  "eta": 1.20, "phi": 1.20, "constituents": ["D"]},
]


def delta_phi(phi1, phi2):
    """
    Return phi1 - phi2 wrapped into [-pi, pi].
    This matters in real collider events because phi is periodic.
    """
    dphi = phi1 - phi2

    while dphi > math.pi:
        dphi -= 2.0 * math.pi

    while dphi < -math.pi:
        dphi += 2.0 * math.pi

    return dphi


def delta_r2(obj1, obj2):
    """
    Compute Delta R^2 = Delta eta^2 + Delta phi^2.
    """
    deta = obj1["eta"] - obj2["eta"]
    dphi = delta_phi(obj1["phi"], obj2["phi"])

    return deta * deta + dphi * dphi


def anti_kt_pair_distance(obj1, obj2, radius):
    """
    Anti-kT pairwise distance:

        d_ij = min(1/pt_i^2, 1/pt_j^2) * DeltaR_ij^2 / R^2
    """
    inv_pt2_i = 1.0 / (obj1["pt"] * obj1["pt"])
    inv_pt2_j = 1.0 / (obj2["pt"] * obj2["pt"])

    return min(inv_pt2_i, inv_pt2_j) * delta_r2(obj1, obj2) / (radius * radius)


def anti_kt_beam_distance(obj):
    """
    Anti-kT beam distance:

        d_iB = 1 / pt_i^2
    """
    return 1.0 / (obj["pt"] * obj["pt"])


def merge_objects(obj1, obj2):
    """
    Merge two objects.

    For this toy example, we use a pT-weighted average for eta and phi.
    In real jet clustering, four-vector recombination is usually used.

    This approximation is good enough for understanding the algorithm.
    """
    new_pt = obj1["pt"] + obj2["pt"]

    new_eta = (obj1["pt"] * obj1["eta"] + obj2["pt"] * obj2["eta"]) / new_pt
    new_phi = (obj1["pt"] * obj1["phi"] + obj2["pt"] * obj2["phi"]) / new_pt

    new_constituents = obj1["constituents"] + obj2["constituents"]
    new_name = "(" + "+".join(new_constituents) + ")"

    return {
        "name": new_name,
        "pt": new_pt,
        "eta": new_eta,
        "phi": new_phi,
        "constituents": new_constituents,
    }


def print_objects(objects, title):
    print("\n" + title)
    print("-" * len(title))

    for obj in objects:
        print(
            f"{obj['name']:12s}  "
            f"pT = {obj['pt']:8.3f} GeV,  "
            f"eta = {obj['eta']:7.3f},  "
            f"phi = {obj['phi']:7.3f},  "
            f"constituents = {obj['constituents']}"
        )


def find_smallest_distance(objects, radius):
    """
    Compute all pair distances and beam distances.
    Return the smallest one.

    Return format:
        {
            "type": "pair" or "beam",
            "distance": value,
            "i": index,
            "j": index or None
        }
    """
    smallest = {
        "type": None,
        "distance": float("inf"),
        "i": None,
        "j": None,
    }

    # Pairwise distances
    for i in range(len(objects)):
        for j in range(i + 1, len(objects)):
            dij = anti_kt_pair_distance(objects[i], objects[j], radius)

            if dij < smallest["distance"]:
                smallest = {
                    "type": "pair",
                    "distance": dij,
                    "i": i,
                    "j": j,
                }

    # Beam distances
    for i in range(len(objects)):
        diB = anti_kt_beam_distance(objects[i])

        if diB < smallest["distance"]:
            smallest = {
                "type": "beam",
                "distance": diB,
                "i": i,
                "j": None,
            }

    return smallest


def print_distance_table(objects, radius):
    """
    Print all pair and beam distances for the current clustering step.
    """
    print("\nDistances")
    print("---------")

    rows = []

    for i in range(len(objects)):
        for j in range(i + 1, len(objects)):
            name = f"d({objects[i]['name']}, {objects[j]['name']})"
            dij = anti_kt_pair_distance(objects[i], objects[j], radius)
            rows.append((name, dij))

    for i in range(len(objects)):
        name = f"d({objects[i]['name']}, beam)"
        diB = anti_kt_beam_distance(objects[i])
        rows.append((name, diB))

    rows = sorted(rows, key=lambda x: x[1])

    for name, value in rows:
        print(f"{name:28s} = {value:.8e}")


def run_anti_kt_clustering(input_particles, radius):
    """
    Run anti-kT clustering step by step.
    """
    active_objects = [p.copy() for p in input_particles]
    final_jets = []

    step = 1

    print_objects(active_objects, "Initial particles")

    while len(active_objects) > 0:
        print("\n")
        print("=" * 70)
        print(f"Step {step}")
        print("=" * 70)

        print_objects(active_objects, "Current active objects")
        print_distance_table(active_objects, radius)

        smallest = find_smallest_distance(active_objects, radius)

        if smallest["type"] == "pair":
            i = smallest["i"]
            j = smallest["j"]

            obj1 = active_objects[i]
            obj2 = active_objects[j]

            print(
                f"\nSmallest distance is pair distance: "
                f"d({obj1['name']}, {obj2['name']}) = {smallest['distance']:.8e}"
            )

            print(f"Merging {obj1['name']} and {obj2['name']}")

            merged = merge_objects(obj1, obj2)

            # Remove larger index first so indices do not shift
            for index in sorted([i, j], reverse=True):
                active_objects.pop(index)

            active_objects.append(merged)

        elif smallest["type"] == "beam":
            i = smallest["i"]
            obj = active_objects[i]

            print(
                f"\nSmallest distance is beam distance: "
                f"d({obj['name']}, beam) = {smallest['distance']:.8e}"
            )

            print(f"Declaring {obj['name']} as a final jet")

            final_jets.append(obj)
            active_objects.pop(i)

        step += 1

    print("\n")
    print("=" * 70)
    print("Final jets")
    print("=" * 70)

    print_objects(final_jets, "Final anti-kT jets")

    return final_jets


def plot_event(input_particles, final_jets, radius):
    """
    Plot initial particles and final jet circles in eta-phi plane.
    """
    fig, ax = plt.subplots(figsize=(7, 6))

    # Plot input particles
    for p in input_particles:
        size = 20.0 + 3.0 * p["pt"]

        ax.scatter(p["eta"], p["phi"], s=size, alpha=0.7)
        ax.text(
            p["eta"] + 0.02,
            p["phi"] + 0.02,
            f"{p['name']}\n{p['pt']:.0f} GeV",
            fontsize=10,
        )

    # Plot final jet axes and radius circles
    for idx, jet in enumerate(final_jets, start=1):
        ax.scatter(
            jet["eta"],
            jet["phi"],
            s=120,
            marker="x",
            linewidths=2,
        )

        circle = plt.Circle(
            (jet["eta"], jet["phi"]),
            radius,
            fill=False,
            linestyle="--",
            linewidth=2,
        )

        ax.add_patch(circle)

        ax.text(
            jet["eta"] + 0.03,
            jet["phi"] - 0.08,
            f"Jet {idx}\n{jet['pt']:.0f} GeV\n{jet['constituents']}",
            fontsize=10,
        )

    ax.set_xlabel(r"$\eta$")
    ax.set_ylabel(r"$\phi$")
    ax.set_title(rf"Toy anti-$k_T$ clustering, $R={radius}$")

    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    final_jets = run_anti_kt_clustering(particles, R)
    plot_event(particles, final_jets, R)
