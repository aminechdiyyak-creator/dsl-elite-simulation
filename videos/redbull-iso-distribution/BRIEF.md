---
workflow: general-video
flow: automation
storyboard: no
message: "De l'usine à ta main : le voyage d'une canette Red Bull, en 3D isométrique"
destination: website
aspect: 1920x1080
language: fr
audience: "Entreprises qui cherchent un studio de motion design (pièce de portfolio)"
length: 36s
angle: camera-journey
---

## Intent

Publicité concept (non officielle) pour Red Bull, en motion design, style 3D isométrique.
Illustre le système de distribution : production → stockage → transport → points de vente → consommateur.
Pièce de portfolio qui doit impressionner : zooms, illustrations, animations — « inspire-toi comme tu veux ».

## Customizations

- Un seul monde isométrique continu, parcouru par une caméra virtuelle (blueprint camera-journey + spatial-pan-stations).
- Grand plan large final révélant tout le réseau, compteurs « 175+ pays » et « 12 milliards+ de canettes / an ».
- Final : canette héros + ailes qui se déploient, « Red Bull donne des ailes. »

## Notes

- Pas de logo officiel (taureaux) — canette stylisée, mention « Concept — non affilié à Red Bull ».
- Voix off française ajoutée (Kokoro TTS via `hyperframes tts`, voix `ff_siwis`), 8 répliques calées sur les scènes, dans assets/vo/. Flora et Google TTS indisponibles dans cet environnement (pas de connecteur / pas d'identifiants).
- Pas de musique pour l'instant.
- GSAP vendorisé dans vendor/ (CDN bloqué dans cet environnement).
