# TikTok — « 4 habitudes, c'est tout ce qu'il te faut. »

Version française du format carrousel « 10/10 habits » (Rewired Mind), recréée from scratch dans HyperFrames.

- **Format** : 1080×1920, 15 s, 30 fps — 5 slides × 3 s, calées sur 120 BPM.
- **Structure** : hero (fenêtre sur la ville) → 4 grilles 2×2 (Argent, Corps, Créativité, Esprit), libellés style TikTok, légende sur la jointure centrale.
- **Animation** : cases qui pop à la croche, légende sur le 3e temps, Ken Burns lent, flash blanc sur chaque cut.
- **Son** : `tools/make_score.py` → `assets/audio/score.wav` (beat half-time synthétisé, libre de droits). Conseil : ajoute plutôt un son tendance dans l'app TikTok, il se mixe par-dessus ou remplace celui-ci.
- **Photos** : voir `PROMPTS.md`. Sans photo, chaque case affiche une illustration (dégradé + icône).
- **Carrousel photo** : `slides/slide-1..5.png` (images figées de chaque slide).

```bash
python3 tools/make_score.py        # musique
node tools/scan-photos.mjs         # après avoir ajouté des photos
npx hyperframes render --fps 30 --quality delivery -o renders/4-habitudes.mp4
npx hyperframes snapshot --at 2.8,5.8,8.8,11.8,14.5 --no-end -o slides
```
