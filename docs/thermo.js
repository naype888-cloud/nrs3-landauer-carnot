// Exact thermodynamics of the open chain of d sites, for the interactive pages.
// The reservoir Hamiltonian is H_d = -(adjacency of the path), with levels -2 cos(kπ/(d+1)).
// Unitaries are permutations of the joint energy levels: every state stays diagonal, so
// entropies and energies are exact sums (no numerical diagonalization). Units: k_B = 1.
(function (root) {
  "use strict";

  function levels(d) {
    const e = [];
    for (let k = 1; k <= d; k++) e.push(-2 * Math.cos((k * Math.PI) / (d + 1)));
    return e.sort((a, b) => a - b);
  }

  function boltzmann(kT, e) {
    const m = Math.min(...e);
    const w = e.map((x) => Math.exp(-(x - m) / kT));
    const z = w.reduce((a, b) => a + b, 0);
    return w.map((x) => x / z);
  }

  function shannon(p) {
    let s = 0;
    for (const x of p) if (x > 1e-15) s -= x * Math.log(x);
    return s;
  }

  const dot = (p, e) => p.reduce((a, x, i) => a + x * e[i], 0);

  // joint[i * nb + j] = pa[i] * pb[j]; a permutation sends level perm[k] to slot k
  function kron(pa, pb) {
    const out = [];
    for (const a of pa) for (const b of pb) out.push(a * b);
    return out;
  }
  const apply = (joint, perm) => perm.map((k) => joint[k]);

  function marginals(joint, na, nb) {
    const a = new Array(na).fill(0), b = new Array(nb).fill(0);
    for (let i = 0; i < na; i++) for (let j = 0; j < nb; j++) {
      a[i] += joint[i * nb + j]; b[j] += joint[i * nb + j];
    }
    return [a, b];
  }

  function shuffle(n, rnd) {
    const p = [...Array(n).keys()];
    for (let i = n - 1; i > 0; i--) {
      const j = Math.floor(rnd() * (i + 1)); [p[i], p[j]] = [p[j], p[i]];
    }
    return p;
  }

  function swaps(n, k, rnd) {
    const p = [...Array(n).keys()];
    for (let s = 0; s < k; s++) {
      const i = Math.floor(rnd() * n);
      let j = Math.floor(rnd() * (n - 1)); if (j >= i) j++;
      [p[i], p[j]] = [p[j], p[i]];
    }
    return p;
  }

  // Landauer: qubit (p, 1-p) and reservoir chain of d sites at kT
  function landauer(pq, kT, d, perm) {
    const e = levels(d), g = boltzmann(kT, e), ps = [pq, 1 - pq];
    const out = apply(kron(ps, g), perm), [s, r] = marginals(out, 2, d);
    return { dS: shannon(ps) - shannon(s), Q: dot(r, e) - dot(g, e), s, r, g, e };
  }

  // the permutation that empties the qubit's second level as much as possible
  function bestErasure(pq, kT, d) {
    const joint = kron([pq, 1 - pq], boltzmann(kT, levels(d)));
    return [...joint.keys()].sort((a, b) => joint[b] - joint[a]);
  }

  // Carnot: hot chain dh at kTh, cold chain dc at kTc
  function carnot(kTh, kTc, dh, dc, perm) {
    const eh = levels(dh), ec = levels(dc), gh = boltzmann(kTh, eh), gc = boltzmann(kTc, ec);
    const out = apply(kron(gh, gc), perm), [h, c] = marginals(out, dh, dc);
    return { Qh: dot(gh, eh) - dot(h, eh), Qc: dot(c, ec) - dot(gc, ec) };
  }

  // Kelvin–Planck: one reservoir, a permutation of its own levels
  function singleBath(kT, d, perm) {
    const e = levels(d), g = boltzmann(kT, e);
    return dot(apply(g, perm), e) - dot(g, e);
  }

  function rng(seed) {
    let s = seed >>> 0;
    return () => {
      s = (s + 0x6d2b79f5) >>> 0;
      let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  const api = { levels, boltzmann, shannon, landauer, bestErasure, carnot, singleBath, shuffle,
    swaps, rng };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.Thermo = api;
})(this);
