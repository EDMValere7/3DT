// On-screen copy, written natively per language (not translated line by line).
// Rule: a TITLE and a CAPTION are never on screen at the same time (checked in index.html).
// Times in seconds. Section cuts: 0 / 7.5 / 18.75 / 30 / 39.375 / 45 (128 BPM, 24 bars).
window.COPY = {
  it: {
    titles: [
      { a: 0.4, b: 3.7, lines: ["Tre città.", "<r>Tre isole.</r>"], stagger: [0, 0.9] },
      { a: 14.6, b: 18.5, lines: ["Dove l'auto", "<r>non arriva?</r>"], stagger: [0, 0.6] },
      { a: 19.0, b: 22.3, lines: ["Scanfly <hl>EVO</hl>"], big: true },
      { a: 33.6, b: 36.4, stat: ["<3", "giorni", "di rilievo sul campo"] },
      { a: 36.6, b: 39.3, stat: ["<10", "cm", "di precisione"] },
    ],
    caps: [
      [3.9, 7.3, "Tutte da trasformare in un gemello digitale 3D."],
      [7.9, 11.0, "Il mobile mapping su auto copre le strade…"],
      [11.2, 14.3, "…ma non vicoli, zone pedonali e isole."],
      [22.5, 25.8, "Dal tetto dell'auto allo zaino. Senza attrezzi."],
      [26.0, 29.6, "Poi ovunque: in bici, a piedi, in barca."],
      [30.3, 33.3, "L'ospedale di Isla del Rey, rilevato a piedi."],
    ],
    cta: "Il case study completo su <b>3dt.cloud</b>",
  },
  en: {
    titles: [
      { a: 0.4, b: 3.7, lines: ["Three towns.", "<r>Three islands.</r>"], stagger: [0, 0.9] },
      { a: 14.6, b: 18.5, lines: ["No road?", "<r>No problem.</r>"], stagger: [0, 0.6] },
      { a: 19.0, b: 22.3, lines: ["Scanfly <hl>EVO</hl>"], big: true },
      { a: 33.6, b: 36.4, stat: ["<3", "days", "in the field"] },
      { a: 36.6, b: 39.3, stat: ["<10", "cm", "accuracy"] },
    ],
    caps: [
      [3.9, 7.3, "All to be captured as a 3D digital twin."],
      [7.9, 11.0, "Car-mounted mobile mapping covers the streets…"],
      [11.2, 14.3, "…but not the alleys, pedestrian zones or islands."],
      [22.5, 25.8, "From car roof to backpack. No tools needed."],
      [26.0, 29.6, "Then anywhere: by bike, on foot, by boat."],
      [30.3, 33.3, "Isla del Rey's old hospital, scanned on foot."],
    ],
    cta: "Full case study at <b>3dt.cloud</b>",
  },
};
