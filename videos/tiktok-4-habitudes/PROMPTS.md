# Photos à générer (Google Flow / tout générateur d'images)

Format **9:16 vertical** pour `hero`, **portrait 9:16** aussi pour les 16 cases (elles sont recadrées en 538×958).
Style commun à ajouter à chaque prompt :
> *cinematic moody photo, dark tones, soft natural light, shallow depth of field, film grain, no text, no logo*

Enregistre chaque image dans `assets/photos/` avec **exactement** le nom indiqué (jpg, png ou webp),
puis lance `node tools/scan-photos.mjs` et refais le rendu. Les cases sans photo gardent l'illustration.

| Fichier | Prompt |
|---|---|
| `hero` | young man reading a book by a large window overlooking a city skyline at golden hour, seen from behind, cozy dim room |
| `argent-investir` | close-up of a laptop showing stock market charts on a dark desk at night, phone with trading app |
| `argent-coder` | programmer's hands on a keyboard, code on a dark monitor, blue screen glow |
| `argent-contenu` | creator filming with a camera on a tripod in a moody home studio, ring light |
| `argent-vendre` | shipping boxes and packages stacked on a table, small online business, warm light |
| `corps-boxe` | boxer wrapping hands in a dark gym, red gloves, dramatic side light |
| `corps-muscu` | man lifting a heavy dumbbell in a dark gym, sweat, rim light |
| `corps-natation` | swimmer underwater in a pool, light rays, deep blue |
| `corps-sport` | football on a night stadium pitch, floodlights, grass close-up |
| `crea-design` | designer drawing on a graphic tablet, colorful UI on screen, dark studio |
| `crea-montage` | video editing timeline on a large monitor in a dark room, headphones |
| `crea-jeux` | chess pieces on a board, dramatic low-key lighting |
| `crea-competences` | hands repairing a watch or a guitar on a workbench, tools, warm lamp |
| `esprit-journal` | hand writing in a leather journal with a pen, coffee, morning light |
| `esprit-lecture` | open book on a bed with a reading lamp at night |
| `esprit-etudes` | student studying with notes and a laptop at a library desk, night |
| `esprit-langues` | notebook with words in several languages, flags and a phone dictionary app |
