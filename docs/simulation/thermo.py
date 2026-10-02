"""Finite-dimensional thermodynamics used by the figures (numerics, not the Lean proofs).

The reservoir is the open chain of `d` sites, `H = -(adjacency of the path)`, the transport
Hamiltonian of NRS³ up to scale. Units: `k_B = 1`. Unitaries are real rotations `exp(tA)` with
`A` antisymmetric; every theorem of the repository holds for them, since they are unitary.
"""

import numpy as np
from scipy.linalg import expm


def chain(d):
    """`H_d`: hopping between neighbouring sites of the open chain."""
    return -(np.eye(d, k=1) + np.eye(d, k=-1))


def gibbs(beta, h):
    w, v = np.linalg.eigh(h)
    p = np.exp(-beta * (w - w.min()))
    return (v * (p / p.sum())) @ v.T


def entropy(rho):
    p = np.linalg.eigvalsh(rho)
    p = p[p > 1e-14]
    return float(-(p * np.log(p)).sum())


def ptrace(rho, da, db, keep):
    r = rho.reshape(da, db, da, db)
    return np.einsum("ijkj->ik", r) if keep == 0 else np.einsum("ijil->jl", r)


def rotation(n, t, rng):
    a = rng.standard_normal((n, n))
    return expm(t * (a - a.T) / np.sqrt(2 * n))


def landauer_run(rho_s, beta, h, u):
    """Entropy lost by the system and heat given to the reservoir."""
    ds, dr = rho_s.shape[0], h.shape[0]
    g = gibbs(beta, h)
    out = u @ np.kron(rho_s, g) @ u.T
    ds_loss = entropy(rho_s) - entropy(ptrace(out, ds, dr, 0))
    heat = float(np.trace(ptrace(out, ds, dr, 1) @ h) - np.trace(g @ h))
    return ds_loss, heat


def carnot_run(beta_h, beta_c, hh, hc, u):
    """Heat taken from the hot reservoir and heat given to the cold one."""
    dh, dc = hh.shape[0], hc.shape[0]
    gh, gc = gibbs(beta_h, hh), gibbs(beta_c, hc)
    out = u @ np.kron(gh, gc) @ u.T
    q_h = float(np.trace(gh @ hh) - np.trace(ptrace(out, dh, dc, 0) @ hh))
    q_c = float(np.trace(ptrace(out, dh, dc, 1) @ hc) - np.trace(gc @ hc))
    return q_h, q_c


def levels(h):
    return np.linalg.eigvalsh(h)


def boltzmann(beta, e):
    p = np.exp(-beta * (e - e.min()))
    return p / p.sum()


def shannon(p):
    p = p[p > 1e-15]
    return float(-(p * np.log(p)).sum())


def landauer_perm(p_s, beta, e, perm):
    """Same as `landauer_run` for a permutation of the joint energy levels (a unitary)."""
    g = boltzmann(beta, e)
    joint = np.kron(p_s, g)[perm].reshape(len(p_s), len(e))
    return shannon(p_s) - shannon(joint.sum(1)), float(joint.sum(0) @ e - g @ e)


def carnot_perm(beta_h, beta_c, eh, ec, perm):
    gh, gc = boltzmann(beta_h, eh), boltzmann(beta_c, ec)
    joint = np.kron(gh, gc)[perm].reshape(len(eh), len(ec))
    return float(gh @ eh - joint.sum(1) @ eh), float(joint.sum(0) @ ec - gc @ ec)
