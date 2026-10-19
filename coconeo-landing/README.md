# Coco Neo — cold pressed coconut oil landing page

A static, dependency-free product landing page for **coconeo.in**, laid out like the
Tata Simply Better product page: announcement bar → gallery + buy box → trust strip →
benefits → story → comparison → process → uses → product details → reviews → value
packs → FAQ → footer, with a sticky mobile buy bar and a cart drawer.

Open `index.html` in a browser, or serve the folder (`npx http-server .`).

## Files

| Path | What it is |
| --- | --- |
| `index.html` | Page markup (SEO meta, Open Graph, schema.org Product data) |
| `assets/css/styles.css` | All styles. Brand colours are the tokens at the top |
| `assets/js/config.js` | **Edit here:** prices, pack sizes, gallery images, WhatsApp number, checkout URL |
| `assets/js/reviews.js` | **Edit here:** rating totals and reviews (currently placeholders, see below) |
| `assets/js/app.js` | Gallery, pack picker, cart (localStorage), pincode check, review filters |
| `assets/img/` | Product photos and generated mockups |
| `tools/cutout.py` | Cuts the bottle out of the white studio shot |
| `tools/mockups.py` | Generates the combo-pack, infographic, label close-up and OG images |
| `tools/build-preview.py` | Inlines CSS/JS into `dist/preview.html` for the hosted preview |
| `tests/smoke.mjs` | Playwright smoke test (desktop + mobile), `npm test` |

## Before going live

1. **Reviews are placeholders.** Replace `assets/js/reviews.js` with real, verified reviews
   and real totals, then set `isPlaceholder: false`. Until then the page shows a
   "preview content" note and leaves the star rating out of the search-engine data.
   Publishing invented reviews breaks Indian consumer-protection rules and marketplace policies.
2. **Prices are placeholders** (`config.js`: ₹449 / ₹849 / ₹1,199).
3. **"Cold pressed"**: the current bottle label says "Premium Coconut Oil". Make sure the
   cold-pressed claim matches how the oil is made, or update the label.
4. **Shelf life** differs between photos (5 months on the studio shot, 9 months on the
   lifestyle shots). The page avoids a number; confirm which is correct.
5. Point `checkoutUrl` at the real cart, and wire the pincode check to your courier API.

## How it fits into the store

```
Browser ── index.html + css/js (static, CDN-cacheable)
   │  Add to cart → localStorage cart → "Checkout" → config.checkoutUrl (store cart)
   │  "Order on WhatsApp" → wa.me deep link with the chosen pack and quantity
   └─ reviews.js / config.js → swap for an API or store export when ready
```

The page is plain HTML/CSS/JS so it can drop into Shopify (as a product template section),
WooCommerce, or any static host. When the store is chosen, the cart buttons should call
that platform's cart API instead of localStorage, and reviews should come from a review
app (Judge.me, Loox, Google reviews) so they stay verified.
