/* Store settings. Edit prices, packs and contact details here — the page reads everything from this file. */
window.COCONEO = {
  currency: "₹",
  freeShippingAbove: 499,
  whatsapp: "917907850060",
  // Where "Buy it now" / "Checkout" should go. Point this at your store's cart or checkout URL.
  checkoutUrl: "https://www.coconeo.in/cart",

  // PLACEHOLDER PRICES — confirm before launch.
  packs: [
    { id: "1l", label: "1 L", sub: "1 bottle", litres: 1, price: 449, mrp: 499, img: "assets/img/packshot.webp" },
    { id: "2l", label: "2 L", sub: "Pack of 2", litres: 2, price: 849, mrp: 998, img: "assets/img/mockups/combo-2.webp", tag: "Popular" },
    { id: "3l", label: "3 L", sub: "Pack of 3", litres: 3, price: 1199, mrp: 1497, img: "assets/img/mockups/combo-3.webp", tag: "Best value" }
  ],

  gallery: [
    { src: "assets/img/packshot.webp", thumb: "assets/img/packshot-thumb.webp", alt: "Coco Neo cold pressed coconut oil 1 litre bottle" },
    { src: "assets/img/kerala-goodness.webp", thumb: "assets/img/kerala-goodness-thumb.webp", alt: "Coco Neo bottle among palm leaves and coconuts — Pure Kerala Goodness" },
    { src: "assets/img/tradition.webp", thumb: "assets/img/tradition-thumb.webp", alt: "Coco Neo bottle on a wooden table with coconut milk — Tradition in every drop" },
    { src: "assets/img/self-care.webp", thumb: "assets/img/self-care-thumb.webp", alt: "Coco Neo bottle on pink tiles — for hair, skin and cooking" },
    { src: "assets/img/mockups/infographic.webp", thumb: "assets/img/mockups/infographic-thumb.webp", alt: "What's inside: 100% pure, 0 mg cholesterol, no preservatives, ISO 22000, FSSAI" },
    { src: "assets/img/mockups/label-closeup.webp", thumb: "assets/img/mockups/label-closeup-thumb.webp", alt: "Label close-up with nutrition facts and certifications" }
  ]
};
