// DSL Elite launch cinematic: shared by index.html (16:9) and vertical/index.html (9:16).
// Builds and returns the paused timeline; each page registers it inline.
window.buildDslCinematic = function () {
  const tl = gsap.timeline({ paused: true });
  const DUR = 13.5;
  // canvas size, framing and hole scale come from the root, so one script drives every format
  const ROOT = document.getElementById("root");
  const W = +ROOT.dataset.width,
    H = +ROOT.dataset.height,
    CX = W / 2,
    CY = H / 2;
  const HOLE = +(ROOT.dataset.holeScale || 1); // shadow-radius multiplier
  const REBORN_Y = +(ROOT.dataset.rebornY || 455); // centre of the reborn hole behind the logo
  const T_COLLAPSE = 6.7,
    T_BANG = 7.95;

  // deterministic PRNG
  let seed = 1971;
  const rand = () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const smooth = (a, b, v) => {
    const x = clamp((v - a) / (b - a));
    return x * x * (3 - 2 * x);
  };

  // ---------- particle sets ----------
  const stars = [];
  for (let i = 0; i < 900; i++) {
    stars.push({ x: rand() * W * 1.4 - W * 0.2, y: rand() * H * 1.4 - H * 0.2, s: rand() < 0.08 ? 2.4 : 1.2, b: 0.25 + rand() * 0.75, ph: rand() * 6.28 });
  }
  const disk = [];
  for (let i = 0; i < 5200; i++) {
    const u = rand();
    const r = 1.55 + Math.pow(u, 1.8) * 3.8; // in shadow radii, dense near the inner edge
    disk.push({ r, th: rand() * Math.PI * 2, s: 1.2 + rand() * 2.4, j: (rand() - 0.5) * 0.05, v: 0.6 + rand() * 1.4, k: rand() });
  }
  const halo = [];
  for (let i = 0; i < 1400; i++) {
    const u = rand();
    halo.push({ r: 1.04 + Math.pow(u, 2.2) * 0.42, a: rand() * Math.PI * 2, s: 1 + rand() * 1.6, k: rand() });
  }

  // colour by temperature (0 = hot inner, 1 = cool outer)
  function tempColor(x, alpha) {
    let r, g, b;
    if (x < 0.25) {
      const k = x / 0.25;
      r = 255; g = 244 - 52 * k; b = 214 - 124 * k;
    } else if (x < 0.65) {
      const k = (x - 0.25) / 0.4;
      r = 255; g = 192 - 52 * k; b = 90 - 24 * k;
    } else {
      const k = (x - 0.65) / 0.35;
      r = 255 - 10 * k; g = 140 - 69 * k; b = 66 + 21 * k;
    }
    return `rgba(${r | 0},${g | 0},${b | 0},${alpha.toFixed(3)})`;
  }

  // integral of spin speed (spin accelerates into the collapse)
  function spinPhase(t) {
    if (t < T_COLLAPSE) return t;
    const d = Math.min(t, T_BANG) - T_COLLAPSE;
    const span = T_BANG - T_COLLAPSE;
    return T_COLLAPSE + d + 7 * (d * d * d) / (3 * span * span);
  }

  const cv = document.getElementById("space");
  const ctx = cv.getContext("2d");

  function draw(t) {
    ctx.globalCompositeOperation = "source-over";
    ctx.fillStyle = "#050505";
    ctx.fillRect(0, 0, W, H);

    const pre = t < T_BANG;
    const after = t - T_BANG;
    // shadow radius: far → push-in → collapse; reborn small behind the logo
    let R;
    if (pre) {
      R = (42 + 168 * smooth(1.0, 6.9, t)) * HOLE;
      R *= 1 - 0.78 * Math.pow(clamp((t - T_COLLAPSE) / (T_BANG - T_COLLAPSE)), 2.2);
    } else {
      R = 245 * HOLE * smooth(1.4, 3.4, after);
    }
    const bright = pre ? smooth(0.8, 2.6, t) * (1 + 0.9 * smooth(T_COLLAPSE, T_BANG, t)) : 0.6 * smooth(1.4, 3.4, after);
    const tilt = -0.14 + 0.06 * smooth(0, DUR, t);
    const cosT = Math.cos(tilt),
      sinT = Math.sin(tilt);
    const ASPECT = 0.24;
    const phase = pre ? spinPhase(t) : 8 + after * 0.6;
    const cy = pre ? CY : REBORN_Y; // reborn hole frames the "DSL" mark

    // starfield with gravitational lensing + streaks on the bang
    const lens = R * R * 2.2;
    for (const s of stars) {
      let dx = s.x - CX + (pre ? -t * 6 : 0),
        dy = s.y - cy;
      let d2 = dx * dx + dy * dy + 1;
      const d = Math.sqrt(d2);
      const push = lens / d; // Einstein-ring style displacement
      let x = CX + (dx / d) * (d + push),
        y = cy + (dy / d) * (d + push);
      let a = s.b * (0.55 + 0.45 * Math.sin(t * 2.3 + s.ph)) * smooth(0, 1.2, t);
      if (!pre && after < 1.5) {
        const k = Math.pow(clamp(1 - after / 1.5), 2) * 260;
        ctx.strokeStyle = `rgba(255,220,190,${(a * 0.8).toFixed(3)})`;
        ctx.lineWidth = s.s;
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x + (dx / d) * k, y + (dy / d) * k);
        ctx.stroke();
      }
      if (Math.hypot(x - CX, y - cy) < R * 1.02) continue;
      ctx.fillStyle = `rgba(255,240,230,${a.toFixed(3)})`;
      ctx.fillRect(x, y, s.s, s.s);
    }

    if (bright <= 0.001 && pre) return;

    // outer glow
    if (R > 1) {
      const g = ctx.createRadialGradient(CX, cy, R * 0.9, CX, cy, R * 5.5);
      g.addColorStop(0, `rgba(255,140,66,${(0.35 * bright).toFixed(3)})`);
      g.addColorStop(0.35, `rgba(255,71,87,${(0.12 * bright).toFixed(3)})`);
      g.addColorStop(1, "rgba(255,71,87,0)");
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, W, H);
    }

    ctx.globalCompositeOperation = "lighter";
    const project = (p, scaleR) => {
      const th = p.th + phase * p.v * 1.6 / Math.pow(p.r, 1.5);
      const x = Math.cos(th) * p.r * scaleR,
        y = Math.sin(th) * p.r * scaleR * ASPECT;
      return { X: CX + x * cosT - y * sinT, Y: cy + x * sinT + y * cosT + p.j * scaleR, th, front: Math.sin(th) > 0, cos: Math.cos(th) };
    };

    // explosion debris (disk particles flung outward)
    if (!pre && after < 3) {
      const fade = Math.exp(-after * 1.6);
      for (const p of disk) {
        const th = p.th;
        const dist = (p.r * 40) + Math.pow(after, 0.6) * (500 + p.k * 1400);
        const x = CX + Math.cos(th) * dist,
          y = CY + Math.sin(th) * dist * 0.62;
        ctx.fillStyle = tempColor(clamp((p.r - 1.55) / 3.8), 0.9 * fade);
        ctx.fillRect(x, y, p.s * 1.6, p.s * 1.6);
      }
    }
    if (R < 2) return;

    // soft luminous band along the disk plane
    ctx.save();
    ctx.translate(CX, cy);
    ctx.rotate(tilt);
    ctx.scale(1, ASPECT);
    const band = ctx.createRadialGradient(0, 0, R * 1.2, 0, 0, R * 5.4);
    band.addColorStop(0, `rgba(255,190,120,${(0.42 * bright).toFixed(3)})`);
    band.addColorStop(0.3, `rgba(255,140,66,${(0.2 * bright).toFixed(3)})`);
    band.addColorStop(1, "rgba(255,71,87,0)");
    ctx.fillStyle = band;
    ctx.beginPath();
    ctx.arc(0, 0, R * 5.4, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // back half of the disk
    const DR = R;
    for (const p of disk) {
      const q = project(p, DR);
      if (q.front) continue;
      const dop = 1 + 0.55 * -q.cos;
      const a = clamp(0.55 * bright * dop * (1.2 - (p.r - 1.55) / 4.5));
      ctx.fillStyle = tempColor(clamp((p.r - 1.55) / 3.8), a);
      ctx.fillRect(q.X, q.Y, p.s, p.s);
    }
    // gravitational lensing: the far side of the disk bends over the top of the hole,
    // a fainter image wraps under it
    for (const p of disk) {
      const th = p.th + phase * p.v * 1.6 / Math.pow(p.r, 1.5);
      const sn = Math.sin(th);
      const u = clamp((p.r - 1.55) / 3.8);
      const top = sn < 0;
      const rho = R * (top ? 1.06 + 0.42 * Math.pow(u, 0.8) : 1.04 + 0.16 * Math.pow(u, 0.8));
      const ang = top ? th : th;
      const x = CX + Math.cos(ang) * rho,
        y = cy + Math.sin(ang) * rho;
      const a = clamp((top ? 0.62 : 0.26) * bright * (1.25 - u) * (0.55 + 0.45 * Math.abs(sn)));
      ctx.fillStyle = tempColor(u, a);
      ctx.fillRect(x, y, p.s * 0.9, p.s * 0.9);
    }
    // lensed image of the far disk: a halo hugging the shadow, brightest top & bottom
    for (const h of halo) {
      const a0 = h.a + phase * 0.35;
      const rr = R * h.r;
      const x = CX + Math.cos(a0) * rr,
        y = cy + Math.sin(a0) * rr;
      const tb = 0.35 + 0.65 * Math.abs(Math.sin(a0));
      const a = clamp(0.7 * bright * tb * (1.5 - h.r));
      ctx.fillStyle = tempColor(clamp((h.r - 1.04) * 1.6), a);
      ctx.fillRect(x, y, h.s, h.s);
    }
    ctx.globalCompositeOperation = "source-over";
    // event horizon (shadow)
    ctx.fillStyle = "#000000";
    ctx.beginPath();
    ctx.arc(CX, cy, R, 0, Math.PI * 2);
    ctx.fill();
    // photon ring
    ctx.globalCompositeOperation = "lighter";
    for (let k = 0; k < 4; k++) {
      ctx.strokeStyle = `rgba(255,${200 - k * 25},${150 - k * 30},${(0.5 * bright / (k + 1)).toFixed(3)})`;
      ctx.lineWidth = 2 + k * 3;
      ctx.beginPath();
      ctx.arc(CX, cy, R * 1.02 + k * 1.5, 0, Math.PI * 2);
      ctx.stroke();
    }
    // front half of the disk (crosses in front of the shadow)
    for (const p of disk) {
      const q = project(p, DR);
      if (!q.front) continue;
      const dop = 1 + 0.55 * -q.cos;
      const a = clamp(0.75 * bright * dop * (1.25 - (p.r - 1.55) / 4.5));
      ctx.fillStyle = tempColor(clamp((p.r - 1.55) / 3.8), a);
      ctx.fillRect(q.X, q.Y, p.s, p.s);
    }
    ctx.globalCompositeOperation = "source-over";
  }

  // one driver tween: every canvas frame is a pure function of time
  const clock = { t: 0 };
  draw(0);
  tl.fromTo(clock, { t: 0 }, { t: DUR, duration: DUR, ease: "none", onUpdate: () => draw(clock.t) }, 0);

  // ---------- HUD ----------
  const typeLine = (id, at, dur) => tl.fromTo(id, { width: 0 }, { width: 760, duration: dur, ease: "steps(28)" }, at);
  typeLine("#hl1", 0.5, 0.6);
  typeLine("#hl2", 1.3, 0.5);
  typeLine("#hl3", 2.1, 0.6);
  typeLine("#hl4", 2.85, 0.35);
  tl.fromTo("#hl4", { opacity: 1 }, { opacity: 0.35, duration: 0.16, ease: "steps(1)", yoyo: true, repeat: 5 }, 3.2);
  tl.fromTo("#hud-corner", { opacity: 0 }, { opacity: 1, duration: 0.4 }, 0.6);
  tl.to(["#hud", "#hud-corner"], { opacity: 0, x: -20, duration: 0.5, ease: "power2.in" }, 5.0);

  // ---------- cinematic lines ----------
  tl.fromTo("#l1", { opacity: 0, y: 24, scale: 1.08 }, { opacity: 1, y: 0, scale: 1, duration: 0.8, ease: "power3.out" }, 3.65);
  tl.to("#l1", { opacity: 0, y: -16, duration: 0.4, ease: "power2.in" }, 5.05);
  tl.fromTo("#l2", { opacity: 0, y: 24, scale: 1.08 }, { opacity: 1, y: 0, scale: 1, duration: 0.8, ease: "power3.out" }, 5.45);
  tl.to("#l2", { opacity: 0, scale: 0.8, duration: 0.5, ease: "power3.in" }, 6.95);

  // ---------- collapse shake, flash, shockwaves ----------
  tl.fromTo("#stage", { x: 0, y: 0 }, { keyframes: { x: [0, -4, 5, -7, 8, -10, 6, -3, 0], y: [0, 3, -5, 6, -6, 9, -4, 2, 0] }, duration: 1.0, ease: "none" }, 7.0);
  tl.fromTo("#stage", { scale: 1 }, { keyframes: { scale: [1, 1.06, 0.98, 1] }, duration: 0.9, ease: "power2.out", immediateRender: false }, T_BANG);
  tl.fromTo("#flash", { opacity: 0 }, { opacity: 1, duration: 0.12, ease: "power2.in" }, T_BANG - 0.1);
  tl.to("#flash", { opacity: 0, duration: 0.9, ease: "power2.out" }, T_BANG + 0.05);
  tl.fromTo("#ring1", { scale: 0.05, opacity: 1 }, { scale: 6.5, opacity: 0, immediateRender: false, duration: 1.4, ease: "power3.out" }, T_BANG);
  tl.fromTo("#ring2", { scale: 0.05, opacity: 0.9 }, { scale: 4.2, opacity: 0, immediateRender: false, duration: 1.1, ease: "power2.out" }, T_BANG + 0.12);

  // ---------- logo ----------
  tl.fromTo("#dsl", { scale: 1.9, opacity: 0, filter: "blur(18px)" }, { scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.55, ease: "power4.out" }, 8.05);
  tl.fromTo("#dsl-r", { x: -26, opacity: 0.9 }, { x: 0, opacity: 0, duration: 0.6, ease: "power3.out" }, 8.1);
  tl.fromTo("#dsl-o", { x: 26, opacity: 0.9 }, { x: 0, opacity: 0, duration: 0.6, ease: "power3.out" }, 8.1);
  tl.fromTo("#elite", { opacity: 0, scaleX: 1.6 }, { opacity: 1, scaleX: 1, duration: 0.9, ease: "power3.out" }, 8.45);
  tl.fromTo("#rule", { scaleX: 0 }, { scaleX: 1, duration: 0.7, ease: "power3.inOut" }, 8.9);
  tl.fromTo("#sub", { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }, 9.1);
  tl.fromTo("#cta-tag", { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }, 11.0);
  tl.fromTo("#cta", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 12.0);
  tl.fromTo("#cta", { opacity: 1 }, { opacity: 0.25, duration: 0.3, ease: "sine.inOut", yoyo: true, repeat: 1, immediateRender: false }, 12.35);
  tl.fromTo("#logo", { scale: 1 }, { scale: 1.04, duration: 5.3, ease: "sine.inOut" }, 8.2);
  tl.fromTo("#fadeout", { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "power1.in" }, 13.0);

  return tl;
};
