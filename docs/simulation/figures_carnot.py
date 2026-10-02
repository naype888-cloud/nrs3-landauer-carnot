"""Figure for Kelvin–Planck and the Carnot bound (numpy, matplotlib).

Writes docs/figures/carnot_efficiency.png.

Left: two reservoirs, each the open chain of d = 4 sites, the cold one at k_B T_c = 1/2, the hot
one at T_h = T_c / x. Engines are unitaries made of one to three swaps of joint energy levels;
for those that take heat from the hot reservoir and give out work, the efficiency
η = W / Q_h is plotted against x = T_c / T_h. Lean: `MState.carnot_temperature` keeps every
engine on or below η = 1 − T_c / T_h. Right: a single reservoir under every permutation of its
levels and random rotations; its energy never goes down (`MState.inner_gibbsState_le_uConj`),
so no work comes out (values here numerical).

Run:  python3 docs/simulation/figures_carnot.py
"""

import itertools

import matplotlib.pyplot as plt
import numpy as np

import thermo as th
from style import BLUE, INK, INK2, MUTED, ORANGE, OUT, SURFACE

KTC, D = 0.5, 4


def engines(x, rng, n=40000):
    e = th.levels(th.chain(D))
    bh, bc = x / KTC, 1 / KTC
    out = []
    for _ in range(n):
        perm = np.arange(D * D)
        for _ in range(rng.integers(1, 4)):
            i, j = rng.choice(D * D, 2, replace=False)
            perm[[i, j]] = perm[[j, i]]
        qh, qc = th.carnot_perm(bh, bc, e, e, perm)
        if qh > 1e-9 and qh - qc > 1e-9:
            out.append((qh - qc) / qh)
    return np.array(out)


def fig_carnot():
    rng = np.random.default_rng(3)
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.6, 4.6), dpi=150,
                                 gridspec_kw={"width_ratios": [1.35, 1]})
    xs = np.linspace(0, 1, 200)
    ax.fill_between(xs, 1 - xs, 1.05, color=ORANGE, alpha=0.10, lw=0)
    ax.plot(xs, 1 - xs, color=ORANGE, lw=1.8, ls="--", label="η = 1 − T_c / T_h  (Lean bound)")
    best = []
    for x in np.linspace(0.1, 0.9, 9):
        eta = engines(x, rng)
        if len(eta):
            ax.scatter(np.full(len(eta), x) + rng.uniform(-0.012, 0.012, len(eta)), eta, s=3,
                       color=BLUE, alpha=0.08, lw=0)
            best.append((x, eta.max()))
    best = np.array(best)
    ax.plot(best[:, 0], best[:, 1], "o", color=BLUE, mec=SURFACE, mew=1, ms=6,
            label="best engine found")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.0)
    ax.set_xlabel("temperature ratio  T_c / T_h")
    ax.set_ylabel("efficiency  η = W / Q_h")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_title("No engine above Carnot", loc="left", fontsize=11.5)

    h = th.chain(D)
    e = th.levels(h)
    g = th.boltzmann(1 / KTC, e)
    de = [float(g[list(p)] @ e - g @ e) for p in itertools.permutations(range(D))]
    gm = th.gibbs(1 / KTC, h)
    de += [float(np.trace(u @ gm @ u.T @ h) - np.trace(gm @ h))
           for u in (th.rotation(D, t, rng) for t in rng.uniform(0, 4, 2000))]
    bx.hist(de, bins=40, color=BLUE, alpha=0.8)
    bx.axvline(0, color=ORANGE, lw=1.8, ls="--")
    bx.text(0.02, bx.get_ylim()[1] * 0.92, "ΔE = 0", color=ORANGE, fontsize=9.5)
    bx.set_xlabel("energy change of one reservoir  ⟨H⟩′ − ⟨H⟩_γ")
    bx.set_ylabel("unitaries")
    bx.set_title("Kelvin–Planck: one bath gives no work", loc="left", fontsize=11.5)

    fig.suptitle(f"The second law: two chains of {D} sites, k_B T_c = {KTC}", x=0.01,
                 ha="left", fontsize=13, color=INK)
    fig.tight_layout()
    fig.savefig(OUT / "carnot_efficiency.png", facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    fig_carnot()
