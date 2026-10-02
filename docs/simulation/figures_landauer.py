"""Figure for Landauer's principle (numpy, matplotlib).

Writes docs/figures/landauer_heat.png.

A qubit holding one bit (maximally mixed) meets a reservoir, the open chain of d = 4 sites at
k_B T = 1/2 in its Gibbs state, through a unitary U. Blue: every permutation of the 8 joint
energy levels (8! unitaries); grey: random rotations exp(tA). Each point is (entropy lost by the
qubit, heat given to the reservoir). Lean: `MState.landauer_temperature` puts every point on or
above the line Q = k_B T ΔS (values here numerical).

Run:  python3 docs/simulation/figures_landauer.py
"""

import itertools

import matplotlib.pyplot as plt
import numpy as np

import thermo as th
from style import BLUE, INK, INK2, MUTED, ORANGE, OUT, SURFACE

KT, D = 0.5, 4


def fig_landauer():
    beta, h = 1 / KT, th.chain(D)
    e, ps = th.levels(h), np.array([0.5, 0.5])
    perm = np.array([th.landauer_perm(ps, beta, e, np.array(p))
                     for p in itertools.permutations(range(2 * D))])
    rng = np.random.default_rng(7)
    rot = np.array([th.landauer_run(np.eye(2) / 2, beta, h, th.rotation(2 * D, t, rng))
                    for t in rng.uniform(0, 4, 1500)])

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.6, 4.6), dpi=150,
                                 gridspec_kw={"width_ratios": [1.35, 1]})
    xs = np.linspace(-0.05, 0.75, 2)
    ax.fill_between(xs, KT * xs, -2, color=ORANGE, alpha=0.10, lw=0)
    ax.plot(xs, KT * xs, color=ORANGE, lw=1.8, ls="--", label="Q = k_B T ΔS  (Lean bound)")
    ax.scatter(rot[:, 0], rot[:, 1], s=5, color=MUTED, alpha=0.35, lw=0,
               label="random rotations exp(tA)")
    ax.scatter(perm[:, 0], perm[:, 1], s=7, color=BLUE, alpha=0.5, lw=0,
               label="permutations of the 8 joint levels")
    ax.axvline(np.log(2), color=INK2, lw=1, ls=":")
    ax.text(np.log(2) - 0.01, -0.12, "one bit\nΔS = ln 2", ha="right", va="bottom", color=INK2,
            fontsize=9)
    ax.set_xlim(-0.05, 0.75)
    ax.set_ylim(-0.15, 1.08 * max(perm[:, 1].max(), rot[:, 1].max()))
    ax.set_xlabel("entropy lost by the qubit  ΔS = S(ρ) − S(ρ′_S)")
    ax.set_ylabel("heat given to the reservoir  Q")
    ax.legend(loc="upper left", fontsize=9)
    ax.set_title("No point below the line", loc="left", fontsize=11.5)

    m = perm[:, 0] > 0.05
    r = perm[m, 1] / (KT * perm[m, 0])
    bx.hist(r, bins=np.linspace(0.9, 6, 52), color=BLUE, alpha=0.8)
    bx.axvline(1, color=ORANGE, lw=1.8, ls="--")
    bx.text(1.08, bx.get_ylim()[1] * 0.92, "Q = k_B T ΔS", color=ORANGE, fontsize=9.5)
    bx.set_xlabel("heat paid per unit of erased entropy  Q / (k_B T ΔS)")
    bx.set_ylabel("permutations with ΔS > 0.05")
    bx.set_title("Erasing always costs at least k_B T per nat", loc="left", fontsize=11.5)

    fig.suptitle(f"Landauer: a qubit and the chain of {D} sites at k_B T = {KT}", x=0.01,
                 ha="left", fontsize=13, color=INK)
    fig.tight_layout()
    fig.savefig(OUT / "landauer_heat.png", facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    fig_landauer()
