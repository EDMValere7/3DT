// Renders the social graphics (carousel slides + reel cover) for both languages to out/<lang>/.
import { chromium } from "playwright";
import { fileURLToPath } from "node:url";
import path from "node:path";
import fs from "node:fs";

const here = path.dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
for (const lang of ["it", "en"]) {
  const dir = path.join(here, "out", lang); fs.mkdirSync(dir, { recursive: true });
  for (const g of ["c1", "c2", "c3", "c4", "c5", "cover"]) {
    await page.goto(`file://${path.join(here, "graphics.html")}?lang=${lang}&g=${g}`);
    await page.evaluate(() => window.ready);
    await page.locator(".frame").screenshot({ path: path.join(dir, `${g}.png`) });
  }
}
await browser.close();
