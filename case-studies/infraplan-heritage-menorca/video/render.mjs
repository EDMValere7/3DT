// Renders index.html frame-by-frame and pipes JPEGs into ffmpeg.
// usage: node render.mjs <lang> [out.mp4] | node render.mjs <lang> --stills 1,5,12   (FFMPEG env var = ffmpeg binary)
import { chromium } from "playwright";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";
import fs from "node:fs";

const here = path.dirname(fileURLToPath(import.meta.url));
const [lang = "it", ...args] = process.argv.slice(2);
const stillsArg = args.indexOf("--stills");
const FPS = 30;
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
page.on("pageerror", e => { console.error("page error:", e.message); process.exit(1); });
await page.goto("file://" + path.join(here, "index.html") + "?lang=" + lang);
await page.evaluate(() => window.ready);
const overlaps = await page.evaluate(() => window.overlaps);
if (overlaps.length) { console.error("caption/title overlap:\n" + overlaps.join("\n")); process.exit(1); }
const DUR = await page.evaluate(() => window.DURATION);
const shot = () => page.locator("#stage").screenshot({ type: "jpeg", quality: 93 });

if (stillsArg >= 0) {
  const dir = path.join(here, "out/stills", lang); fs.mkdirSync(dir, { recursive: true });
  for (const t of args[stillsArg + 1].split(",").map(Number)) { await page.evaluate(t => window.render(t), t); fs.writeFileSync(path.join(dir, `t${t.toFixed(2).padStart(6, "0")}.jpg`), await shot()); }
} else {
  const out = args[0] || path.join(here, `out/video_${lang}_noaudio.mp4`);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  const ff = spawn(process.env.FFMPEG || "ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(FPS), "-i", "-",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "medium", out], { stdio: ["pipe", "ignore", "inherit"] });
  for (let f = 0; f < FPS * DUR; f++) {
    await page.evaluate(t => window.render(t), f / FPS);
    const buf = await shot();
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
  }
  ff.stdin.end(); await new Promise(r => ff.on("close", r));
}
await browser.close();
