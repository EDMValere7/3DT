// Renders index.html frame-by-frame and pipes JPEGs into ffmpeg.
// usage: node render.mjs [out.mp4] [--stills 1,5,12]  (FFMPEG env var = ffmpeg binary)
import { chromium } from "playwright";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";
import fs from "node:fs";

const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const stillsArg = args.indexOf("--stills");
const FPS = 30, DUR = 30;
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || undefined, args: ["--disable-gpu-vsync"] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.goto("file://" + path.join(here, "index.html"));
await page.evaluate(() => window.ready);
const shot = () => page.locator("#stage").screenshot({ type: "jpeg", quality: 93 });

if (stillsArg >= 0) {
  const ts = args[stillsArg + 1].split(",").map(Number);
  fs.mkdirSync(path.join(here, "out/stills"), { recursive: true });
  for (const t of ts) { await page.evaluate(t => window.render(t), t); fs.writeFileSync(path.join(here, `out/stills/t${String(t).padStart(5, "0")}.jpg`), await shot()); }
} else {
  const out = args[0] || path.join(here, "out/video_noaudio.mp4");
  fs.mkdirSync(path.dirname(out), { recursive: true });
  const ff = spawn(process.env.FFMPEG || "ffmpeg", ["-y", "-f", "image2pipe", "-framerate", String(FPS), "-i", "-",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "slow", "-movflags", "+faststart", out], { stdio: ["pipe", "ignore", "inherit"] });
  const t0 = Date.now();
  for (let f = 0; f < FPS * DUR; f++) {
    await page.evaluate(t => window.render(t), f / FPS);
    const buf = await shot();
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
    if (f % 90 === 0) console.log(`frame ${f}/${FPS * DUR}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await new Promise(r => ff.on("close", r));
}
await browser.close();
