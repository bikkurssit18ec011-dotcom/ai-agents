/* Coco Neo landing page behaviour: gallery, pack picker, cart, reviews, small UX helpers. */
(function () {
  "use strict";
  const C = window.COCONEO;
  const R = window.COCONEO_REVIEWS;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const money = (n) => C.currency + n.toLocaleString("en-IN");
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  const state = { pack: C.packs[0], qty: 1, img: 0, cart: loadCart(), shown: 6, filter: "all" };

  /* ---------- Gallery ---------- */
  const main = $("[data-gallery-main]");
  const thumbs = $("[data-gallery-thumbs]");
  thumbs.innerHTML = C.gallery.map((g, i) =>
    `<button role="tab" aria-selected="${i === 0}" aria-label="Image ${i + 1}" data-i="${i}"><img src="${g.thumb}" alt="" loading="lazy" width="80" height="80"></button>`).join("");
  function showImg(i) {
    state.img = (i + C.gallery.length) % C.gallery.length;
    const g = C.gallery[state.img];
    main.classList.add("is-fading");
    const pre = new Image();
    pre.onload = () => { main.src = g.src; main.alt = g.alt; main.classList.remove("is-fading"); };
    pre.src = g.src;
    $$("button", thumbs).forEach((b, j) => b.setAttribute("aria-selected", j === state.img));
  }
  thumbs.addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) showImg(+b.dataset.i); });
  $("[data-gallery-prev]").onclick = () => showImg(state.img - 1);
  $("[data-gallery-next]").onclick = () => showImg(state.img + 1);
  let touchX = null;
  main.addEventListener("touchstart", (e) => (touchX = e.touches[0].clientX), { passive: true });
  main.addEventListener("touchend", (e) => {
    if (touchX === null) return;
    const dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 40) showImg(state.img + (dx < 0 ? 1 : -1));
    touchX = null;
  });

  /* ---------- Pack picker & price ---------- */
  const packsEl = $("[data-packs]");
  packsEl.innerHTML = C.packs.map((p, i) => `
    <label class="pack">
      <input type="radio" name="pack" value="${p.id}" ${i === 0 ? "checked" : ""}>
      <span class="pack__box">
        ${p.tag ? `<span class="pack__tag">${p.tag}</span>` : ""}
        <b>${p.label}</b><span>${p.sub}</span>
        <span class="pack__price">${money(p.price)}</span>
        <span class="pack__per">${money(Math.round(p.price / p.litres))}/L</span>
      </span>
    </label>`).join("");
  packsEl.addEventListener("change", (e) => {
    state.pack = C.packs.find((p) => p.id === e.target.value);
    renderPrice();
    if (state.pack.id !== "1l") { main.src = state.pack.img; main.alt = `Coco Neo ${state.pack.sub}`; }
    else showImg(0);
  });
  function renderPrice() {
    const p = state.pack;
    const off = Math.round((1 - p.price / p.mrp) * 100);
    $("[data-price]").textContent = money(p.price * state.qty);
    $("[data-mrp]").textContent = money(p.mrp * state.qty);
    $("[data-off]").textContent = `${off}% OFF`;
    $("[data-per-litre]").textContent = `${money(Math.round(p.price / p.litres))}/L`;
    $("[data-sticky-price]").textContent = `${money(p.price)} · ${p.label}`;
    const msg = `Hi Coco Neo, I'd like to order ${state.qty} × Cold Pressed Coconut Oil (${p.sub}, ${p.label}).`;
    $("[data-whatsapp]").href = `https://wa.me/${C.whatsapp}?text=${encodeURIComponent(msg)}`;
  }
  $$("[data-qty]").forEach((b) => b.addEventListener("click", () => {
    state.qty = Math.min(20, Math.max(1, state.qty + +b.dataset.qty));
    $("[data-qty-val]").textContent = state.qty;
    renderPrice();
  }));

  /* ---------- Cart ---------- */
  function loadCart() { try { return JSON.parse(localStorage.getItem("coconeo-cart")) || []; } catch { return []; } }
  function saveCart() { try { localStorage.setItem("coconeo-cart", JSON.stringify(state.cart)); } catch { /* storage unavailable */ } }
  function addToCart() {
    const line = state.cart.find((l) => l.id === state.pack.id);
    if (line) line.qty += state.qty; else state.cart.push({ id: state.pack.id, qty: state.qty });
    saveCart(); renderCart(); toast(`Added ${state.qty} × ${state.pack.sub} to cart`); openDrawer();
  }
  function renderCart() {
    const lines = state.cart.map((l) => ({ ...l, p: C.packs.find((p) => p.id === l.id) })).filter((l) => l.p);
    const count = lines.reduce((a, l) => a + l.qty, 0);
    const total = lines.reduce((a, l) => a + l.qty * l.p.price, 0);
    $("[data-cart-count]").textContent = count;
    $("[data-cart-count]").classList.toggle("is-on", count > 0);
    $("[data-cart-items]").innerHTML = lines.length ? lines.map((l) => `
      <div class="line">
        <img src="${l.p.img}" alt="" width="64" height="64">
        <div><b>Cold Pressed Coconut Oil</b><span class="muted small">${l.p.sub} · ${l.p.label}</span>
          <div class="qty qty--sm"><button data-line="${l.id}" data-d="-1" aria-label="Decrease">−</button><output>${l.qty}</output><button data-line="${l.id}" data-d="1" aria-label="Increase">+</button></div>
        </div>
        <b>${money(l.qty * l.p.price)}</b>
      </div>`).join("") : `<p class="muted center">Your cart is empty.</p>`;
    $("[data-cart-total]").textContent = money(total);
    const gap = C.freeShippingAbove - total;
    $("[data-ship-msg]").textContent = total === 0 ? "" : gap > 0 ? `Add ${money(gap)} more for free delivery` : "You've unlocked free delivery 🎉";
  }
  $("[data-cart-items]").addEventListener("click", (e) => {
    const b = e.target.closest("[data-line]"); if (!b) return;
    const l = state.cart.find((x) => x.id === b.dataset.line);
    l.qty += +b.dataset.d;
    if (l.qty <= 0) state.cart = state.cart.filter((x) => x !== l);
    saveCart(); renderCart();
  });
  const drawer = $("[data-drawer]");
  function openDrawer() { drawer.classList.add("is-open"); drawer.setAttribute("aria-hidden", "false"); }
  function closeDrawer() { drawer.classList.remove("is-open"); drawer.setAttribute("aria-hidden", "true"); }
  $$("[data-add-to-cart]").forEach((b) => b.addEventListener("click", addToCart));
  $("[data-cart-open]").onclick = openDrawer;
  $("[data-cart-close]").onclick = closeDrawer;
  drawer.addEventListener("click", (e) => { if (e.target === drawer) closeDrawer(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeDrawer(); });
  $("[data-buy-now]").addEventListener("click", (e) => { e.preventDefault(); addToCart(); });
  $("[data-checkout]").href = C.checkoutUrl;

  /* ---------- Pincode check (client-side stub; wire to your courier API) ---------- */
  $("[data-pin-check]").addEventListener("click", () => {
    const v = $("[data-pin]").value.trim();
    const msg = $("[data-pin-msg]");
    if (!/^[1-9]\d{5}$/.test(v)) { msg.textContent = "Please enter a valid 6-digit pincode."; msg.className = "small err"; return; }
    const kerala = /^6[7-9]/.test(v);
    msg.textContent = kerala ? "✓ Delivers in 2–3 days · COD available" : "✓ Delivers in 4–6 days · COD available";
    msg.className = "small ok";
  });

  /* ---------- Reviews ---------- */
  $$("[data-avg-rating]").forEach((el) => (el.textContent = R.average.toFixed(1)));
  $$("[data-review-total]").forEach((el) => (el.textContent = R.total.toLocaleString("en-IN")));
  $$(".stars").forEach((el) => el.style.setProperty("--r", R.average));
  if (R.isPlaceholder) $("[data-preview-note]").hidden = false;
  const sum = R.breakdown.reduce((a, b) => a + b, 0) || 1;
  $("[data-bars]").innerHTML = R.breakdown.map((n, i) => `
    <div class="bar"><span>${5 - i} ★</span><span class="bar__track"><span style="width:${(n / sum * 100).toFixed(1)}%"></span></span><span class="muted">${n.toLocaleString("en-IN")}</span></div>`).join("");

  const fmtDate = (d) => new Date(d + "T00:00:00").toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
  function renderReviews() {
    const list = R.items.filter((r) => state.filter === "all" || (state.filter === "photos" ? r.photo : r.tag === state.filter));
    $("[data-reviews]").innerHTML = list.slice(0, state.shown).map((r) => `
      <article class="review">
        <header>
          <span class="avatar" aria-hidden="true">${esc(r.name[0])}</span>
          <div><b>${esc(r.name)}</b><span class="muted small">${esc(r.place)}${r.verified === false ? "" : ' · <span class="verified">✓ Verified buyer</span>'}</span></div>
        </header>
        <div class="review__meta"><span class="stars" style="--r:${r.rating}" aria-label="${r.rating} out of 5"></span><span class="muted small">${fmtDate(r.date)}</span></div>
        <h3>${esc(r.title)}</h3>
        <p>${esc(r.body)}</p>
        ${r.photo ? `<img class="review__photo" src="${r.photo}" alt="Customer photo" loading="lazy" width="96" height="120">` : ""}
        <footer><span class="chip chip--sm">${esc(r.tag)}</span><button class="helpful" data-helpful>Helpful?</button></footer>
      </article>`).join("") || `<p class="muted center">No reviews in this category yet.</p>`;
    $("[data-more-reviews]").hidden = list.length <= state.shown;
  }
  $("[data-filters]").addEventListener("click", (e) => {
    const b = e.target.closest("[data-filter]"); if (!b) return;
    $$("[data-filter]").forEach((x) => x.classList.toggle("is-active", x === b));
    state.filter = b.dataset.filter; state.shown = 6; renderReviews();
  });
  $("[data-more-reviews]").onclick = () => { state.shown += 6; renderReviews(); };
  $("[data-reviews]").addEventListener("click", (e) => {
    const b = e.target.closest("[data-helpful]"); if (!b || b.disabled) return;
    b.textContent = "Thanks!"; b.disabled = true;
  });
  const dlg = $("[data-review-dialog]");
  $("[data-write-review]").onclick = () => dlg.showModal();
  dlg.addEventListener("close", () => {
    if (dlg.returnValue === "submit") toast("Thanks! Your review will appear after we verify your order.");
    $("[data-review-form]").reset();
  });

  /* ---------- Combos ---------- */
  $("[data-combos]").innerHTML = C.packs.map((p) => `
    <article class="combo">
      ${p.tag ? `<span class="pack__tag">${p.tag}</span>` : ""}
      <img src="${p.img}" alt="Coco Neo ${p.sub}" loading="lazy" width="600" height="600">
      <h3>${p.sub} · ${p.label}</h3>
      <p><b>${money(p.price)}</b> <s class="muted">${money(p.mrp)}</s> <span class="price__off">${Math.round((1 - p.price / p.mrp) * 100)}% OFF</span></p>
      <button class="btn btn--primary btn--block" data-combo="${p.id}">Add to cart</button>
    </article>`).join("");
  $("[data-combos]").addEventListener("click", (e) => {
    const b = e.target.closest("[data-combo]"); if (!b) return;
    const input = $(`input[name=pack][value="${b.dataset.combo}"]`);
    input.checked = true; input.dispatchEvent(new Event("change", { bubbles: true }));
    state.qty = 1; $("[data-qty-val]").textContent = 1; renderPrice(); addToCart();
  });

  /* ---------- Misc ---------- */
  const menuBtn = $("[data-menu-toggle]");
  menuBtn.onclick = () => {
    const open = document.body.classList.toggle("menu-open");
    menuBtn.setAttribute("aria-expanded", open);
  };
  $$("[data-menu] a").forEach((a) => a.addEventListener("click", () => document.body.classList.remove("menu-open")));

  let toastT;
  function toast(t) { const el = $("[data-toast]"); el.textContent = t; el.classList.add("is-on"); clearTimeout(toastT); toastT = setTimeout(() => el.classList.remove("is-on"), 2600); }

  // Sticky buy bar appears once the main buy button scrolls out of view
  const buyBtn = $(".buy-row [data-add-to-cart]");
  new IntersectionObserver(([en]) => $("[data-sticky]").classList.toggle("is-on", !en.isIntersecting && en.boundingClientRect.top < 0)).observe(buyBtn);

  $("[data-year]").textContent = new Date().getFullYear();

  // Structured data for search engines (only real data: price and product facts; ratings are added when reviews are real)
  const schema = {
    "@context": "https://schema.org", "@type": "Product",
    name: "Coco Neo Cold Pressed Coconut Oil", brand: { "@type": "Brand", name: "Coco Neo" },
    image: C.gallery.map((g) => new URL(g.src, location.href).href),
    description: "100% pure and natural coconut oil made in Kerala. No preservatives. ISO 22000:2018 certified unit.",
    offers: C.packs.map((p) => ({ "@type": "Offer", priceCurrency: "INR", price: p.price, availability: "https://schema.org/InStock", name: p.sub }))
  };
  if (!R.isPlaceholder) schema.aggregateRating = { "@type": "AggregateRating", ratingValue: R.average, reviewCount: R.total };
  $("#product-schema").textContent = JSON.stringify(schema);

  renderPrice(); renderCart(); renderReviews();
})();
