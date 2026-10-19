// Playwright smoke test: run with `node tests/smoke.mjs` from the coconeo-landing folder.
import { chromium } from "playwright";
import http from "node:http";
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(".");
const types = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".webp": "image/webp", ".png": "image/png" };
const server = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split("?")[0]).replace(/\/$/, "/index.html"));
  if (!p.startsWith(root) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { "content-type": types[path.extname(p)] || "application/octet-stream" });
  fs.createReadStream(p).pipe(res);
}).listen(4173);

const outDir = process.env.SHOTS || "screenshots";
fs.mkdirSync(outDir, { recursive: true });
const browser = await chromium.launch();
const fails = [];
const check = (ok, msg) => { console.log((ok ? "PASS " : "FAIL ") + msg); if (!ok) fails.push(msg); };

for (const vp of [{ name: "desktop", width: 1440, height: 900 }, { name: "mobile", width: 390, height: 844, isMobile: true }]) {
  const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height }, isMobile: !!vp.isMobile, deviceScaleFactor: vp.isMobile ? 2 : 1 });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => m.type() === "error" && !/Failed to load resource/.test(m.text()) && errors.push(m.text()));
  page.on("requestfailed", (r) => !/fonts\.(googleapis|gstatic)/.test(r.url()) && errors.push("request failed: " + r.url()));
  // Google Fonts is not reachable from CI sandboxes; fall back to system fonts.
  await page.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
  await page.goto("http://localhost:4173/", { waitUntil: "load" });

  check(errors.length === 0, `${vp.name}: no JS errors ${errors.join(" | ")}`);
  // Anything sticking out past the right edge (body clips overflow, so check elements directly)
  const overflow = await page.evaluate(() => Math.max(0, ...[...document.querySelectorAll("main *")].filter((el) => !el.closest(".gallery__thumbs, .announce")).map((el) => el.getBoundingClientRect().right - window.innerWidth)));
  check(overflow <= 0, `${vp.name}: no horizontal scroll (overflow ${overflow}px)`);
  check(await page.locator("[data-gallery-thumbs] button").count() === 6, `${vp.name}: 6 gallery thumbnails`);
  check(await page.locator(".review").count() === 6, `${vp.name}: 6 reviews rendered`);
  const broken = await page.evaluate(() => [...document.images].filter((i) => i.complete && i.naturalWidth === 0).map((i) => i.src));
  check(broken.length === 0, `${vp.name}: no broken images ${broken.join(",")}`);

  await page.screenshot({ path: `${outDir}/${vp.name}-hero.png` });
  await page.screenshot({ path: `${outDir}/${vp.name}-full.png`, fullPage: true });

  // Interactions
  await page.locator(".pack").nth(1).click();
  check((await page.textContent("[data-price]")) === "₹849", `${vp.name}: 2L pack updates price`);
  await page.locator(".buy-row [data-add-to-cart]").click();
  await page.waitForTimeout(400);
  check((await page.textContent("[data-cart-count]")) === "1", `${vp.name}: cart count = 1`);
  await page.screenshot({ path: `${outDir}/${vp.name}-cart.png` });
  await page.click("[data-cart-close]");
  await page.click('[data-filter="Hair"]');
  check(await page.locator(".review").count() === 2, `${vp.name}: Hair filter shows 2 reviews`);
  await page.fill("[data-pin]", "695122"); await page.click("[data-pin-check]");
  check(/2–3 days/.test(await page.textContent("[data-pin-msg]")), `${vp.name}: pincode check`);
  await page.locator("#reviews").scrollIntoViewIfNeeded();
  await page.screenshot({ path: `${outDir}/${vp.name}-reviews.png` });
  await page.close();
}
await browser.close(); server.close();
console.log(fails.length ? `\n${fails.length} check(s) failed` : "\nAll checks passed");
process.exit(fails.length ? 1 : 0);
