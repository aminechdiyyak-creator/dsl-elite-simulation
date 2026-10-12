---
workflow: general-video
flow: automation
storyboard: no
message: "DSL Elite : le jeu qui attire tout, comme un trou noir"
destination: website
aspect: 1920x1080
language: fr
length: 13.5s
---

## Intent

Cinématique de lancement du jeu DSL Elite (business simulation), 10–15 s, avec un trou noir
dans le style de la DSL Academy, et du son.

## Customizations

- Trou noir dessiné sur canvas (disque d'accrétion orange, anneau de photons, arc lentillé),
  fonction pure du temps pilotée par la timeline GSAP.
- HUD « anomalie détectée », deux phrases, effondrement, explosion (flash + ondes de choc),
  logo DSL ELITE, « APPUIE SUR START ».
- Sound design synthétisé (tools/make_sfx.py) : drone, bips HUD, riser, implosion, impact,
  scintillement, whoosh, carillon start.

- Voix off FR (HyperFrames TTS, Kokoro ff_siwis) : 4 répliques (assets/vo/).
- Version verticale 9:16 dans vertical/ (même script cinematic.js, cadrage différent).

## Notes

- Couleurs reprises de l'app DSL Elite (#050505, #ff8c42, #ff4757). Sora n'étant pas embarquée,
  Montserrat la remplace ; JetBrains Mono pour le HUD.
- La vidéo « DSL Academy » d'origine n'est pas dans ce dépôt : style recréé.
