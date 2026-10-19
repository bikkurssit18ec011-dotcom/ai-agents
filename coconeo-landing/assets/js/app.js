/* Coco Neo product page behaviour: stage gallery, pack picker, cart, 24°C test, uses tabs, reviews, entrances. */
(function () {
  "use strict";
  const C = window.COCONEO;
  const R = window.COCONEO_REVIEWS;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const money = (n) => C.currency + n.toLocaleString("en-IN");
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const state = { pack: C.packs[0], qty: 1, img: 0, cart: loadCart(), shown: 6, filter: "all" };

  /* ---------- Stars (drawn, no glyphs) ---------- */
  const starRow = () => '<svg viewBox="0 0 24 24"><use href="#i-star"/></svg>'.repeat(5);
  function paintStars(el, r) {
    el.innerHTML = `${starRow()}<span class="stars__fg" style="width:${(r / 5) * 100}%">${starRow()}</span>`;
  }

  /* ---------- Stage: crossfading gallery ---------- */
  const layers = [$("[data-stage-a]"), $("[data-stage-b]")];
  let front = 0;
  const thumbs = $("[data-thumbs]");
  thumbs.innerHTML = C.gallery.map((g, i) =>
    `<button role="tab" aria-selected="${i === 0}" aria-label="Show image ${i + 1}: ${esc(g.alt)}" data-i="${i}"><img src="${g.thumb}" alt="" width="80" height="80" loading="lazy"></button>`).join("");
  function showImg(i, src, alt) {
    const g = C.gallery[i] || {};
    src = src || g.src; alt = alt || g.alt;
    state.img = i;
    $$("button", thumbs).forEach((b, j) => b.setAttribute("aria-selected", j === i));
    const back = layers[1 - front];
    if (layers[front].getAttribute("src") === src) return;
    const pre = new Image();
    pre.onload = () => {
      back.src = src; back.alt = alt; back.removeAttribute("aria-hidden");
      layers[front].alt = ""; layers[front].setAttribute("aria-hidden", "true");
      back.classList.add("is-on"); layers[front].classList.remove("is-on");
      front = 1 - front;
    };
    pre.src = src;
  }
  thumbs.addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) showImg(+b.dataset.i); });
  // The stage follows the reading column on wide screens
  if (matchMedia("(min-width: 1000px)").matches) {
    const so = new IntersectionObserver((ents) => ents.forEach((en) => {
      if (en.isIntersecting) {
        const i = +en.target.dataset.stage;
        if (en.target.id === "buy" && state.pack.id !== "1l") showImg(i, state.pack.img, `Coco Neo ${state.pack.sub}`);
        else showImg(i);
      }
    }), { rootMargin: "-45% 0px -45% 0px" });
    $$("[data-stage]").forEach((s) => so.observe(s));
  }

  /* ---------- Pack picker and price ---------- */
  const perL = (p) => money(Math.round(p.price / p.litres));
  $("[data-packs]").innerHTML = C.packs.map((p, i) => `
    <label class="pack">
      <input type="radio" name="pack" value="${p.id}" ${i === 0 ? "checked" : ""}>
      <span class="pack__box">
        <b>${p.label}</b>
        <span>${p.sub}</span>
        <span>${money(p.price)}</span>
        ${p.tag ? `<span class="pack__tag">${p.tag}</span>` : `<span>${perL(p)} a litre</span>`}
      </span>
    </label>`).join("");
  function selectPack(id) {
    state.pack = C.packs.find((p) => p.id === id);
    const input = $(`input[name=pack][value="${id}"]`); if (input) input.checked = true;
    renderPrice();
    if (id === "1l") showImg(0); else showImg(state.img, state.pack.img, `Coco Neo ${state.pack.sub}`);
  }
  $("[data-packs]").addEventListener("change", (e) => selectPack(e.target.value));
  function renderPrice() {
    const p = state.pack;
    $("[data-price]").textContent = money(p.price * state.qty);
    $("[data-mrp]").textContent = money(p.mrp * state.qty);
    $("[data-off]").textContent = `Save ${Math.round((1 - p.price / p.mrp) * 100)}%`;
    $("[data-per-litre]").textContent = `${perL(p)} a litre`;
    $("[data-sticky-price]").textContent = `${money(p.price)}, ${p.label}`;
    const msg = `Hi Coco Neo, I'd like to order ${state.qty} × Cold Pressed Coconut Oil (${p.sub}, ${p.label}).`;
    $("[data-whatsapp]").href = `https://wa.me/${C.whatsapp}?text=${encodeURIComponent(msg)}`;
  }
  $$("[data-qty]").forEach((b) => b.addEventListener("click", () => {
    state.qty = Math.min(20, Math.max(1, state.qty + +b.dataset.qty));
    $("[data-qty-val]").textContent = state.qty;
    renderPrice();
  }));

  /* ---------- Price list ---------- */
  $("[data-price-list]").innerHTML = C.packs.map((p) => `
    <li class="reveal">
      <b>${p.sub}, ${p.label}</b><span class="pl-price">${money(p.price)}</span>
      <p>${perL(p)} a litre. MRP <s>${money(p.mrp)}</s>, save ${Math.round((1 - p.price / p.mrp) * 100)}%.</p>
      <button class="btn btn--tone btn--sm" data-add-pack="${p.id}">Add to cart</button>
    </li>`).join("");
  $("[data-price-list]").addEventListener("click", (e) => {
    const b = e.target.closest("[data-add-pack]"); if (!b) return;
    selectPack(b.dataset.addPack);
    state.qty = 1; $("[data-qty-val]").textContent = 1; renderPrice(); addToCart();
  });

  /* ---------- Cart ---------- */
  function loadCart() { try { return JSON.parse(localStorage.getItem("coconeo-cart")) || []; } catch { return []; } }
  function saveCart() { try { localStorage.setItem("coconeo-cart", JSON.stringify(state.cart)); } catch { /* storage unavailable */ } }
  function addToCart() {
    const line = state.cart.find((l) => l.id === state.pack.id);
    if (line) line.qty += state.qty; else state.cart.push({ id: state.pack.id, qty: state.qty });
    saveCart(); renderCart(); toast(`Added ${state.qty} × ${state.pack.sub} to your cart`); openDrawer();
  }
  function renderCart() {
    const lines = state.cart.map((l) => ({ ...l, p: C.packs.find((p) => p.id === l.id) })).filter((l) => l.p);
    const count = lines.reduce((a, l) => a + l.qty, 0);
    const total = lines.reduce((a, l) => a + l.qty * l.p.price, 0);
    $("[data-cart-count]").textContent = count;
    $("[data-cart-items]").innerHTML = lines.length ? lines.map((l) => `
      <div class="line">
        <img src="${l.p.img}" alt="" width="72" height="72">
        <div><b>Cold pressed coconut oil</b><span class="small muted">${l.p.sub}, ${l.p.label}</span>
          <div class="qty"><button data-line="${l.id}" data-d="-1" aria-label="One less">−</button><output>${l.qty}</output><button data-line="${l.id}" data-d="1" aria-label="One more">+</button></div>
        </div>
        <b>${money(l.qty * l.p.price)}</b>
      </div>`).join("") : `<p class="muted">Your cart is empty. Pick a pack size to start.</p>`;
    $("[data-cart-total]").textContent = money(total);
    const gap = C.freeShippingAbove - total;
    $("[data-ship-msg]").textContent = (total === 0 || !C.freeShippingAbove) ? "" : gap > 0 ? `Add ${money(gap)} more for free delivery.` : "Delivery is free on this order.";
  }
  $("[data-cart-items]").addEventListener("click", (e) => {
    const b = e.target.closest("[data-line]"); if (!b) return;
    const l = state.cart.find((x) => x.id === b.dataset.line);
    l.qty += +b.dataset.d;
    if (l.qty <= 0) state.cart = state.cart.filter((x) => x !== l);
    saveCart(); renderCart();
  });
  const drawer = $("[data-drawer]");
  let lastFocus = null;
  function openDrawer() { lastFocus = document.activeElement; drawer.classList.add("is-open"); drawer.setAttribute("aria-hidden", "false"); $("[data-cart-close]").focus({ preventScroll: true }); }
  function closeDrawer() { drawer.classList.remove("is-open"); drawer.setAttribute("aria-hidden", "true"); if (lastFocus) lastFocus.focus({ preventScroll: true }); }
  $$("[data-add-to-cart]").forEach((b) => b.addEventListener("click", addToCart));
  $("[data-cart-open]").onclick = openDrawer;
  $("[data-cart-close]").onclick = closeDrawer;
  drawer.addEventListener("click", (e) => { if (e.target === drawer) closeDrawer(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && drawer.classList.contains("is-open")) closeDrawer(); });
  $("[data-buy-now]").addEventListener("click", (e) => { e.preventDefault(); addToCart(); });
  $("[data-checkout]").href = C.checkoutUrl;

  /* ---------- Pincode (client-side stub; connect your courier's API) ---------- */
  $("[data-pin-check]").addEventListener("click", () => {
    const v = $("[data-pin]").value.trim();
    const msg = $("[data-pin-msg]"); // Stub: replace with your courier's serviceability API
    if (!/^[1-9]\d{5}$/.test(v)) { msg.textContent = "Enter a 6-digit pincode, for example 695122."; msg.className = "small err"; return; }
    msg.textContent = /^6[7-9]/.test(v) ? "We deliver to this Kerala pincode. Cash on delivery available." : "We deliver to this pincode. Cash on delivery available.";
    msg.className = "small ok";
  });

  /* ---------- The 24°C test ---------- */
  const temp = $("[data-temp]"), jar = $("[data-jar]");
  function renderTemp() {
    const t = +temp.value;
    $("[data-temp-out]").textContent = `${t}°C`;
    const solid = t < 24, soft = t >= 22 && t <= 25;
    jar.classList.toggle("is-solid", solid);
    $("[data-jar-cap]").textContent = solid ? "Solid, white" : "Liquid, clear";
    $("[data-temp-msg]").textContent = solid
      ? `At ${t}°C pure coconut oil sets white and solid. Stand the bottle in lukewarm water for a few minutes before pouring.`
      : soft ? `At ${t}°C you are near the line. You may see a few white flakes settle at the bottom. That is the oil starting to set, not dirt.`
        : `At ${t}°C the oil is clear and golden. Pour as usual.`;
  }
  temp.addEventListener("input", renderTemp);

  /* ---------- Uses tabs ---------- */
  const USES = [
    { title: "One bottle for the kitchen", text: "Avial, thoran, fish curry and banana chips. Temper mustard seeds and curry leaves in it and the kitchen smells the way it should.", img: "assets/img/kerala-goodness.webp", alt: "Coco Neo bottle among palm leaves and fresh coconuts" },
    { title: "The weekly hair oiling", text: "Warm two spoons, massage into the scalp and leave it an hour before your bath. The same oil Kerala grew up with.", img: "assets/img/self-care.webp", alt: "Coco Neo bottle on pink tiles with coconut halves and drops of oil" },
    { title: "Dry hands and heels", text: "A few drops on dry skin at night. Patch-test first if your skin is sensitive.", img: "assets/img/tradition.webp", alt: "Coco Neo bottle on a wooden table with fresh coconut" }
  ];
  const useImg = $("[data-use-img]");
  $("[data-use-tabs]").addEventListener("click", (e) => {
    const b = e.target.closest("[data-use]"); if (!b) return;
    const u = USES[+b.dataset.use];
    $$("[data-use]").forEach((x) => x.setAttribute("aria-selected", x === b));
    $("[data-use-title]").textContent = u.title;
    $("[data-use-text]").textContent = u.text;
    useImg.style.opacity = 0;
    setTimeout(() => { useImg.src = u.img; useImg.alt = u.alt; useImg.style.opacity = 1; }, reduced ? 0 : 200);
  });

  /* ---------- Reviews ---------- */
  $$("[data-avg-rating]").forEach((el) => (el.textContent = R.average.toFixed(1)));
  $$("[data-review-total]").forEach((el) => (el.textContent = R.total.toLocaleString("en-IN")));
  $$("[data-stars]").forEach((el) => paintStars(el, R.average));
  if (R.isPlaceholder) { $("[data-preview-note]").hidden = false; $$("[data-sample]").forEach((el) => (el.hidden = false)); }
  const sum = R.breakdown.reduce((a, b) => a + b, 0) || 1;
  $("[data-bars]").innerHTML = R.breakdown.map((n, i) => `
    <div class="bar-row"><span>${5 - i} stars</span><span class="bar-row__track"><span style="width:${(n / sum * 100).toFixed(1)}%"></span></span><span>${n.toLocaleString("en-IN")}</span></div>`).join("");
  const fmtDate = (d) => new Date(d + "T00:00:00").toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
  function renderReviews() {
    const list = R.items.filter((r) => state.filter === "all" || (state.filter === "photos" ? r.photo : r.tag === state.filter));
    $("[data-reviews]").innerHTML = list.slice(0, state.shown).map((r) => `
      <article class="review">
        <span class="stars" data-r="${r.rating}" aria-label="${r.rating} out of 5 stars"></span>
        <h3>${esc(r.title)}</h3>
        <p>${esc(r.body)}</p>
        ${r.photo ? `<img class="review__photo" src="${r.photo}" alt="Photo from ${esc(r.name)}" loading="lazy" width="120" height="150">` : ""}
        <p class="review__who"><b>${esc(r.name)}</b><span>${esc(r.place)}</span>${R.isPlaceholder ? "<span>Sample review</span>" : '<span class="verified">Verified buyer</span>'}</p>
        <p class="review__foot"><span>${esc(r.tag)}, ${fmtDate(r.date)}</span><button class="helpful" data-helpful>Helpful</button></p>
      </article>`).join("") || `<p class="muted">No reviews here yet.</p>`;
    $$(".review .stars").forEach((el) => paintStars(el, +el.dataset.r));
    $("[data-more-reviews]").hidden = list.length <= state.shown;
    observeAll($$(".review"));
  }
  $("[data-filters]").addEventListener("click", (e) => {
    const b = e.target.closest("[data-filter]"); if (!b) return;
    $$("[data-filter]").forEach((x) => { x.classList.toggle("is-on", x === b); x.setAttribute("aria-pressed", x === b); });
    state.filter = b.dataset.filter; state.shown = 6; renderReviews();
  });
  $("[data-more-reviews]").onclick = () => { state.shown += 6; renderReviews(); };
  $("[data-reviews]").addEventListener("click", (e) => {
    const b = e.target.closest("[data-helpful]"); if (!b || b.disabled) return;
    b.textContent = "Marked helpful"; b.disabled = true;
  });
  const dlg = $("[data-review-dialog]");
  $("[data-write-review]").onclick = () => dlg.showModal();
  dlg.addEventListener("close", () => {
    if (dlg.returnValue === "submit") toast("Thank you. Your review appears once we match it to an order.");
    $("[data-review-form]").reset();
  });

  /* ---------- Menu, toast, sticky bar ---------- */
  const menuBtn = $("[data-menu-toggle]");
  menuBtn.onclick = () => { const open = document.body.classList.toggle("menu-open"); menuBtn.setAttribute("aria-expanded", open); menuBtn.textContent = open ? "Close" : "Menu"; };
  $$("[data-menu] a").forEach((a) => a.addEventListener("click", () => { document.body.classList.remove("menu-open"); menuBtn.setAttribute("aria-expanded", "false"); menuBtn.textContent = "Menu"; }));
  let toastT;
  function toast(t) { const el = $("[data-toast]"); el.textContent = t; el.classList.add("is-on"); clearTimeout(toastT); toastT = setTimeout(() => el.classList.remove("is-on"), 2800); }
  const buyBtn = $(".buy [data-add-to-cart]");
  new IntersectionObserver(([en]) => $("[data-sticky]").classList.toggle("is-on", !en.isIntersecting && en.boundingClientRect.top < 0)).observe(buyBtn);

  /* ---------- Entrances: parts of each section rise in, 70ms apart ---------- */
  const io = "IntersectionObserver" in window && !reduced
    ? new IntersectionObserver((ents) => ents.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } }), { rootMargin: "0px 0px -8% 0px" })
    : null;
  function observeAll(els) {
    els.forEach((el, i) => {
      el.style.setProperty("--d", `${(i % 6) * 70}ms`);
      if (io) io.observe(el); else el.classList.add("in");
    });
  }
  $$("section, footer").forEach((sec) => observeAll($$(":scope .reveal", sec).filter((el) => el.closest("section, footer") === sec)));
  // Safety net: never leave content hidden if an observer misses it
  setTimeout(() => $$(".reveal:not(.in), .review:not(.in)").forEach((el) => { if (el.getBoundingClientRect().top < innerHeight) el.classList.add("in"); }), 1200);

  $("[data-year]").textContent = new Date().getFullYear();

  // Search-engine data: product facts and prices only; the rating joins once reviews are real
  const schema = {
    "@context": "https://schema.org", "@type": "Product",
    name: "Coco Neo Cold Pressed Coconut Oil", brand: { "@type": "Brand", name: "Coco Neo" },
    image: C.gallery.map((g) => new URL(g.src, location.href).href),
    description: "100% pure cold pressed coconut oil made in Kerala. No preservatives. ISO 22000:2018 certified unit.",
    offers: C.packs.map((p) => ({ "@type": "Offer", priceCurrency: "INR", price: p.price, availability: "https://schema.org/InStock", name: p.sub }))
  };
  if (!R.isPlaceholder) schema.aggregateRating = { "@type": "AggregateRating", ratingValue: R.average, reviewCount: R.total };
  $("#product-schema").textContent = JSON.stringify(schema);

  if (C.pricesArePlaceholder) $$("[data-price-sample]").forEach((el) => (el.hidden = false));
  renderPrice(); renderCart(); renderReviews(); renderTemp();
})();
