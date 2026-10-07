# Google Flow Browser MCP — installation sur Mac

Copie de [TMSSS05/google-flow-browser-mcp](https://github.com/TMSSS05/google-flow-browser-mcp)
(commit `0c8e80a`) adaptée pour macOS et Claude Code.

## Installation (une seule fois)

Prérequis : Google Chrome dans `/Applications`, Node.js 18+ (`brew install node`), Claude Code.

```bash
cd tools/google-flow-browser-mcp
./scripts/install-mac.sh          # dépendances, config, enregistrement dans Claude Code
./scripts/start-browser-mac.sh    # ouvre Chrome sur Google Flow
```

Dans la fenêtre Chrome qui s'ouvre, connecte-toi à Google **une fois**. Ensuite redémarre
Claude Code et vérifie avec `claude mcp list` que `google-flow` apparaît.

À chaque utilisation : lance `./scripts/start-browser-mac.sh` (ou laisse l'outil `flow_connect`
démarrer Chrome tout seul), puis demande à Claude de générer une image ou une vidéo.

## Ce qui change par rapport à l'original

- **Chemins Mac** : Chrome est trouvé automatiquement (`/Applications/Google Chrome.app`),
  plus de chemins Linux en dur (`/opt/google/chrome`, `~/.config/google-chrome`, `Profile 3`).
- **Profil Chrome dédié par défaut** (`~/.google-flow-mcp/chrome-profile`) : tes cookies
  Google habituels ne sont plus copiés. Chrome 136+ ignore de toute façon le débogage à
  distance sur ton profil principal.
- **Si tu veux quand même utiliser ton profil Chrome habituel** : dans
  `config/flow.config.json`, mets `chromeUserDataDir` à
  `~/Library/Application Support/Google/Chrome`, `chromeProfile` au nom du profil
  (voir `chrome://version`) et `copyProfile` à `true`. La copie temporaire (qui contient ta
  session Google) est maintenant **supprimée** à la fermeture du serveur.
- **Port de débogage limité à ta machine** (`127.0.0.1`).
- **Corrections de bugs** : les logs allaient sur la sortie standard et cassaient le protocole
  MCP (Claude Code n'arrivait pas à parler au serveur) ; le code d'erreur `CONFIG_ERROR`
  utilisé n'était pas défini.
- `extraChromeArgs` (optionnel) : options Chrome supplémentaires.

## À savoir

- Le serveur pilote Google Flow avec ton compte Google et masque l'automatisation à Google
  (`--disable-blink-features=AutomationControlled`). C'est probablement contraire aux
  conditions d'utilisation de Google : utilise de préférence un compte secondaire.
- Tant que Chrome tourne avec le port 9222 ouvert, n'importe quel programme de ton Mac peut
  le piloter. Ferme cette fenêtre Chrome quand tu as fini.
- Le dépôt d'origine n'a pas de fichier de licence (le README annonce MIT).
