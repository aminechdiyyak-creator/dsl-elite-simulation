---
message: "De l'usine à ta main : le voyage d'une canette Red Bull, en 3D isométrique"
audience: "Entreprises qui cherchent un studio de motion design (portfolio)"
mode: autonomous
duration: 36s
canvas: 1920x1080 @ 30fps
---

Un seul monde isométrique (SVG généré au chargement, projection 30°) parcouru par une
caméra virtuelle (`#world` = legs, `#cam` = micro-drift). Blueprints : `camera-journey`
(legs variés, motivés) + `spatial-pan-stations` (une station = un arrêt + panneau HUD).

## Frame 1 — Ouverture (0–3.7s)
status: built · src: index.html#open
Canette héros + « Chaque canette a un voyage. » — reflet qui balaie la canette, puis la
canette zoome à travers l'écran et laisse apparaître le monde (match cut sur le convoyeur).

## Frame 2 — 01 Production (3.0–9.0s)
status: built · src: index.html (world: factory)
Zoom arrière décéléré (×5.2 → ×2.2, power4.out) depuis les canettes du convoyeur jusqu'à
l'usine : silos, cheminée qui fume, canettes en flux continu.

## Frame 3 — 02 Stockage (9.0–13.9s)
status: built · src: index.html (world: warehouse)
Pan qui suit le convoyeur jusqu'à l'entrepôt ; les palettes apparaissent une à une, le
chariot élévateur fait la navette.

## Frame 4 — 03 Transport (13.9–19.0s)
status: built · src: index.html (world: port + route)
Plongée sur le port : la caméra suit un camion Red Bull sur la route, cargo et grue.

## Frame 5 — 04 Point de vente (19.0–24.0s)
status: built · src: index.html (world: shop)
Swoop en arc (dézoom puis plongée) vers le magasin ; le frigo se remplit, la Mini à
canette arrive.

## Frame 6 — Réseau mondial (24.0–29.4s)
status: built · src: index.html#hud-wide
Grand plan large : les routes se tracent en jaune, des « paquets » circulent, pins 01–05,
compteurs 175+ pays / 12 Mrd+ canettes par an.

## Frame 7 — … jusqu'à toi (29.4–31.2s)
status: built · src: index.html#hud-toi
Poussée violente (power4.in, ×7.5) dans l'écran géant du festival, flash blanc.

## Frame 8 — Signature (31.2–36s)
status: built · src: index.html#end
Canette héros, ailes qui se déploient plume par plume, étincelles,
« Red Bull donne des ailes. » + mention concept non officiel.
