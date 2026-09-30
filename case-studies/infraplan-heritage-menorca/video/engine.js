const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const lerp = (a, b, k) => a + (b - a) * k;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const smooth = k => k * k * (3 - 2 * k);
const outExpo = k => (k >= 1 ? 1 : 1 - Math.pow(2, -10 * k));
const outBack = k => { const c = 1.7; return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); };
const inOut = k => (k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);
const $ = id => document.getElementById(id);
const fmt = n => Math.round(n).toLocaleString("it-IT");
function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const R = rng(2024); // deterministic: same frames every render
const turbo = k => {
  const st = [[0.19, 0.07, 0.23], [0.16, 0.47, 0.93], [0.1, 0.84, 0.78], [0.47, 0.98, 0.35], [0.95, 0.83, 0.2], [0.96, 0.4, 0.12], [0.8, 0.1, 0.05]];
  const f = clamp(k) * (st.length - 1), i = Math.min(st.length - 2, Math.floor(f)), r = f - i;
  return [0, 1, 2].map(j => lerp(st[i][j], st[i + 1][j], r));
};

/* ---------- point sets ---------- */
function makeCloud(n) { return { n: 0, X: new Float32Array(n), Y: new Float32Array(n), Z: new Float32Array(n), A: new Float32Array(n * 3), B: new Float32Array(n * 3), K: new Uint8Array(n) }; }
function push(c, x, y, z, a, b, k = 0) { const i = c.n++; c.X[i] = x; c.Y[i] = y; c.Z[i] = z; c.A.set(a, i * 3); c.B.set(b || a, i * 3); c.K[i] = k; }

// real point-cloud renders from the case study -> particles with depth for parallax
async function imageCloud(src, scale, depth, grayTint) {
  const im = new Image(); im.src = src; await im.decode();
  const w = Math.round(im.width * scale), h = Math.round(im.height * scale);
  const cv = document.createElement("canvas"); cv.width = w; cv.height = h;
  const g = cv.getContext("2d"); g.imageSmoothingQuality = "high"; g.drawImage(im, 0, 0, w, h);
  const d = g.getImageData(0, 0, w, h).data, c = makeCloud(w * h);
  for (let v = 0; v < h; v++) for (let u = 0; u < w; u++) {
    const l = d[(v * w + u) * 4] / 255;
    if (l < 0.09 || R() > Math.min(1, l * 1.5)) continue;
    const it = 0.3 + 0.7 * l;
    const zz = -(1 - v / h) * depth + (R() - .5) * 3;
    const raw = grayTint.map(q => q * it), ramp = turbo(0.14 + 0.8 * Math.pow(l, 1.5)).map(q => q * (0.55 + 0.45 * l));
    push(c, (u - w / 2) + (R() - .5) * .7, -(v - h / 2) + (R() - .5) * .7, zz, raw, ramp);
  }
  c.w = w; c.h = h; return c;
}

// stylised Maó harbour map (y = 0 plane)
const inletX = z => 40 + 55 * Math.sin((z + 420) * 0.0062) - 0.12 * z;
const inletW = z => 34 + 46 * clamp((-z - 120) / 300);
const ISL = [[inletX(-40), -40, 20], [inletX(-190) + 6, -190, 11], [inletX(-300) - 8, -300, 14]];
const TOWN = { ox: -120, oz: 190, a: 0.22, blk: 17, st: 5 };
const townToWorld = (u, v) => { const s = TOWN.blk + TOWN.st, c = Math.cos(TOWN.a), n = Math.sin(TOWN.a); const x = u * s, z = v * s; return [TOWN.ox + x * c - z * n, TOWN.oz + x * n + z * c]; };
const PED = { x: -10, z: 150, rx: 55, rz: 70 }; // old-town pedestrian area near the quay
const inPed = (x, z) => ((x - PED.x) / PED.rx) ** 2 + ((z - PED.z) / PED.rz) ** 2 < 1;
const water = (x, z) => Math.abs(x - inletX(z)) < inletW(z) && !ISL.some(([ix, iz, r]) => (x - ix) ** 2 + (z - iz) ** 2 < r * r) || z < -400;
function mapCloud() {
  const c = makeCloud(160000);
  const MW = 280, MZ = 430;
  for (let i = 0; i < 150000 && c.n < 158000; i++) {
    const x = (R() * 2 - 1) * MW, z = (R() * 2 - 1) * MZ;
    if (water(x, z)) { if (R() < 0.2) { const sh = 0.6 + 0.4 * R(); push(c, x, 0, z, [0.08 * sh, 0.26 * sh, 0.5 * sh], null, 3); } continue; }
    const shore = Math.abs(x - inletX(z)) - inletW(z), coast = (shore >= 0 && shore < 5 && z > -400) || ISL.some(([ix, iz, r]) => { const d2 = (x - ix) ** 2 + (z - iz) ** 2; return d2 < r * r && d2 > (r - 3) ** 2; });
    if (coast) { const it = 0.7 + 0.3 * R(); push(c, x, 0.5, z, [0.95 * it, 0.85 * it, 0.65 * it], null, 5); continue; }
    // town grid?
    const inMao = ((x - TOWN.ox) / 200) ** 2 + ((z - TOWN.oz) / 230) ** 2 < 1 && x < inletX(z) - inletW(z);
    const inCas = ((x - 185) / 70) ** 2 + ((z + 190) / 90) ** 2 < 1 && x > inletX(z) + inletW(z);
    const island = ISL.some(([ix, iz, r]) => (x - ix) ** 2 + (z - iz) ** 2 < r * r);
    if (inMao || inCas || island) {
      const s = TOWN.blk + TOWN.st, c0 = Math.cos(-TOWN.a), n0 = Math.sin(-TOWN.a), dx = x - TOWN.ox, dz = z - TOWN.oz;
      const u = (dx * c0 - dz * n0) / s, v = (dx * n0 + dz * c0) / s;
      const fu = u - Math.floor(u), fv = v - Math.floor(v), street = fu < TOWN.st / s || fv < TOWN.st / s;
      const narrow = inPed(x, z) && (fu < 0.1 || fv < 0.1);
      if (street && !inPed(x, z)) { if (R() < 0.35) push(c, x, 0, z, [0.3, 0.33, 0.38], null, 0); continue; }
      if (narrow && R() < .7) continue;
      const hsh = Math.abs(Math.sin(Math.floor(u) * 12.9898 + Math.floor(v) * 78.233) * 43758.5453) % 1, it = (0.4 + 0.6 * hsh) * (0.75 + R() * 0.25);
      push(c, x, R() * 1.5, z, [0.62 * it, 0.74 * it, 0.95 * it], null, inPed(x, z) ? 2 : island ? 4 : 1);
    } else if (R() < 0.28) {
      const it = 0.2 + R() * 0.25; push(c, x, 0, z, [0.34 * it, 0.5 * it, 0.42 * it], null, 0);
    }
  }
  return c;
}
// route of the car through the town grid, ending at the pedestrian zone
const ROUTE = [[-9.5, 6.5], [-4.5, 6.5], [-4.5, 2.5], [-1.5, 2.5], [-1.5, -0.5], [2.5, -0.5], [2.5, -3.5]].map(([u, v]) => townToWorld(u - 0.11, v - 0.11));

/* ---------- camera / projection ---------- */
const W = 1080, Hh = 1920, CX = W / 2, F = 1350;
function mkCam(yaw, pitch, dist, tx = 0, ty = 0, tz = 0, cy = 980) { return { yaw, pitch, dist, tx, ty, tz, cy }; }
function project(cam, x, y, z) {
  const cyw = Math.cos(cam.yaw), syw = Math.sin(cam.yaw), cp = Math.cos(cam.pitch), sp = Math.sin(cam.pitch);
  const dx = x - cam.tx, dy = y - cam.ty, dz = z - cam.tz;
  const x1 = dx * cyw - dz * syw, z1 = dx * syw + dz * cyw;
  const y2 = dy * cp - z1 * sp, z2 = dy * sp + z1 * cp, depth = cam.dist - z2;
  return [CX + F * x1 / depth, cam.cy - F * y2 / depth, depth];
}

const pc = $("pc"), ctx = pc.getContext("2d"), fx = $("fx"), fctx = fx.getContext("2d");
const acc = new Float32Array(W * Hh * 3), img = ctx.createImageData(W, Hh);
const off = document.createElement("canvas"); off.width = W; off.height = Hh; const octx = off.getContext("2d");
const bloom = document.createElement("canvas"); bloom.width = 270; bloom.height = 480; const bctx = bloom.getContext("2d");
const BG = (() => { const g = ctx.createRadialGradient(CX, 1000, 0, CX, 1000, 1300); g.addColorStop(0, "#0f151d"); g.addColorStop(0.6, "#07090c"); g.addColorStop(1, "#040506"); return g; })();

// o: {alpha, sweep (x reveal), band, mix (0 A..1 B), mixSweep, tint(k,i)->[r,g,b]|null, size}
function splat(c, cam, o) {
  const cyw = Math.cos(cam.yaw), syw = Math.sin(cam.yaw), cp = Math.cos(cam.pitch), sp = Math.sin(cam.pitch);
  let shown = 0;
  for (let i = 0; i < c.n; i++) {
    const x = c.X[i]; if (o.sweep !== undefined && x > o.sweep) continue;
    const k = i * 3; let a = o.alpha;
    let m = o.mix || 0; if (o.mixSweep !== undefined) m = clamp((o.mixSweep - x) / 30);
    let r = lerp(c.A[k], c.B[k], m), g = lerp(c.A[k + 1], c.B[k + 1], m), b = lerp(c.A[k + 2], c.B[k + 2], m);
    if (o.tint) { const tn = o.tint(c.K[i], x, c.Z[i]); if (tn) { r = tn[0]; g = tn[1]; b = tn[2]; } }
    let glow = 0;
    if (o.sweep !== undefined && o.band) { const d = (o.sweep - x) / o.band; glow += Math.exp(-d * d); }
    if (o.mixSweep !== undefined && o.band2) { const d = (o.mixSweep - x) / o.band2; glow += 0.8 * Math.exp(-d * d); }
    if (glow > 0.01) { r = lerp(r, 1.6, glow * .8); g = lerp(g, 0.3, glow * .8); b = lerp(b, 0.25, glow * .8); a = Math.max(a, glow * o.alpha * 1.2); }
    const dx = x - cam.tx, dy = c.Y[i] - cam.ty, dz = c.Z[i] - cam.tz;
    const x1 = dx * cyw - dz * syw, z1 = dx * syw + dz * cyw;
    const y2 = dy * cp - z1 * sp, z2 = dy * sp + z1 * cp, depth = cam.dist - z2;
    if (depth < 5) continue;
    const px = (CX + F * x1 / depth) | 0, py = (cam.cy - F * y2 / depth) | 0;
    if (px < 1 || py < 1 || px >= W - 3 || py >= Hh - 3) continue;
    shown++;
    const sz = o.size || 2; r *= a; g *= a; b *= a;
    for (let yy = 0; yy < sz; yy++) { let p = ((py + yy) * W + px) * 3; for (let xx = 0; xx < sz; xx++, p += 3) { acc[p] += r; acc[p + 1] += g; acc[p + 2] += b; } }
  }
  return shown;
}
function flush() {
  const d = img.data;
  for (let p = 0, q = 0; p < acc.length; p += 3, q += 4) { d[q] = Math.min(255, acc[p] * 255); d[q + 1] = Math.min(255, acc[p + 1] * 255); d[q + 2] = Math.min(255, acc[p + 2] * 255); d[q + 3] = 255; }
  octx.putImageData(img, 0, 0);
  ctx.globalCompositeOperation = "source-over"; ctx.fillStyle = BG; ctx.fillRect(0, 0, W, Hh);
  ctx.globalCompositeOperation = "lighter"; ctx.drawImage(off, 0, 0);
  bctx.clearRect(0, 0, 270, 480); bctx.drawImage(off, 0, 0, 270, 480);
  ctx.globalAlpha = 0.5; ctx.drawImage(bloom, 0, 0, W, Hh); ctx.globalAlpha = 1; ctx.globalCompositeOperation = "source-over";
}

