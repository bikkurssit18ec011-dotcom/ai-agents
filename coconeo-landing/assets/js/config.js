/* Store settings. Edit prices, packs and contact details here — the page reads everything from this file. */
window.COCONEO = {
  currency: "₹",
  // Free-delivery threshold in rupees. null hides the message until you confirm a real policy.
  freeShippingAbove: null,
  whatsapp: "917907850060",
  // Where "Buy it now" / "Checkout" should go. Point this at your store's cart or checkout URL.
  checkoutUrl: "https://www.coconeo.in/cart",

  // PLACEHOLDER PRICES — confirm before launch. While true, the page shows a "Preview prices" tag.
  pricesArePlaceholder: true,
  packs: [
    { id: "1l", label: "1 L", sub: "1 bottle", litres: 1, price: 449, mrp: 499, img: "assets/img/packshot.webp" },
    { id: "2l", label: "2 L", sub: "Pack of 2", litres: 2, price: 849, mrp: 998, img: "assets/img/mockups/combo-2.webp", tag: "Popular" },
    { id: "3l", label: "3 L", sub: "Pack of 3", litres: 3, price: 1199, mrp: 1497, img: "assets/img/mockups/combo-3.webp", tag: "Best value" }
  ],

  gallery: [
    { src: "assets/img/packshot.webp", thumb: "assets/img/packshot-thumb.webp", alt: "Coco Neo cold pressed coconut oil, 1 litre bottle" },
    { src: "assets/img/kerala-goodness.webp", thumb: "assets/img/kerala-goodness-thumb.webp", alt: "Coco Neo bottle among palm leaves and fresh coconuts" },
    { src: "assets/img/tradition.webp", thumb: "assets/img/tradition-thumb.webp", alt: "Coco Neo bottle on a wooden table with coconut milk and fresh coconut" },
    { src: "assets/img/self-care.webp", thumb: "assets/img/self-care-thumb.webp", alt: "Coco Neo bottle on pink tiles with coconut halves and drops of oil" },
    { src: "assets/img/mockups/label-closeup.webp", thumb: "assets/img/mockups/label-closeup-thumb.webp", alt: "Close-up of the Coco Neo label with nutrition and certifications" },
    { src: "assets/img/mockups/infographic.webp", thumb: "assets/img/mockups/infographic-thumb.webp", alt: "What is inside: 100% pure, 0 mg cholesterol, no preservatives, ISO 22000, FSSAI" },
    { src: "assets/img/mockups/combo-3.webp", thumb: "assets/img/mockups/combo-3-thumb.webp", alt: "Three bottles of Coco Neo coconut oil, the 3 litre family pack" }
  ]
};
