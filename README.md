# GenerAI

> ⚠️ **DEV / STAGING ONLY** — Ne jamais exposer en production.

Outil de génération de fixtures SQL propulsé par LLM. Il s'installe directement dans le `docker-compose.yaml` de n'importe quel projet et génère des données réalistes et cohérentes à partir d'une simple description en langage naturel.

---

## Prérequis

- Docker + Docker Compose
- Une clé API Anthropic ou OpenAI
- Une base de données Mysql/PostgreSQL exposée dans votre docker-compose

---

## Installation

### 1. Ajouter au docker-compose de votre projet

Dans le `docker-compose.yaml` de votre projet existant, ajoutez le service suivant :

```yaml
services:
  # ... vos services existants ...

  generai:
    image: bastienbretenetdev/generai:latest
    ports:
      - "8088:88"
    depends_on:
      - db
```

### 2. Configurer via l'interface Settings

Au premier lancement, ouvrez **Settings** (icône ⚙ en haut à droite) et renseignez :

| Paramètre | Description |
|---|---|
| **Database > Host** | Hôte de la base de données (ex. `db`, `localhost`) |
| **Database > Port** | Port PostgreSQL (défaut : `5432`) |
| **Database > Name** | Nom de la base de données |
| **Database > User** | Utilisateur PostgreSQL |
| **Database > Password** | Mot de passe PostgreSQL |
| **API keys > Claude** | Clé API Anthropic (`sk-ant-...`) |
| **API keys > ChatGpt** | Clé API OpenAI (`sk-proj-...`) |
| **Hash method** | Algorithme de hashage des mots de passe (`bcrypt`, `argon2`, `sha256`) |
| **Password** | Mot de passe injecté via `{password}` dans le SQL (défaut : `Password123!`) |
| **UUID method** | Algorithme de génération des UUIDs (`uuid7`, `uuid6`, `uuid5`) |

> Les valeurs sont persistées en base locale — vous n'avez pas à les ressaisir à chaque redémarrage.

### 3. Lancer

```bash
docker compose up -d
```

Ouvrez [http://localhost:8088](http://localhost:8088)

---

## Utilisation

1. Décrivez ce que vous voulez générer en langage naturel
   > _"Génère 1 immeuble avec 3 lots et chacun un propriétaire différent"_

2. Cliquez sur **Générer** — le LLM analyse votre schéma et produit le SQL

3. Vérifiez le SQL généré

4. Cliquez sur **Appliquer** pour insérer les données en base

---

## Structure du projet

```
src/
├── main.py              # App factory — montage des routers
├── config.py            # Constantes (méthodes UUID, hash, providers LLM)
├── storage/
│   ├── config_store.py  # SQLite local : settings et historique
│   └── target_db.py     # PostgreSQL cible : introspection schéma, exécution SQL
├── services/
│   ├── llm.py           # Abstraction Claude / OpenAI
│   ├── orchestrator.py  # Pipeline de génération (SSE streaming)
│   ├── replacers.py     # Post-traitement SQL (UUIDs, passwords)
│   └── prompt_loader.py # Chargement des templates de prompts
├── routers/
│   ├── fixtures.py      # GET /, POST /ask, POST /apply
│   ├── settings.py      # GET/POST /settings, /settings/test-db
│   └── history.py       # GET /history, /history/{id}
├── prompts/             # Templates .txt pour les appels LLM
├── templates/           # Templates HTML Jinja2
└── static/              # CSS
```

---

## Limitations connues

- Pas de gestion des cycles de clés étrangères
- Pas de gestion des auto-références
- Les types JSON/JSONB/Array sont supportés mais peuvent manquer de précision
- Le SQL généré est validé mais pas garanti à 100% — toujours vérifier avant d'appliquer

---

## Modèles disponibles

**Claude (Anthropic)**

| Modèle | Usage |
|---|---|
| `claude-haiku-4-5-20251001` | Rapide, économique |
| `claude-sonnet-4-6` | Équilibré |
| `claude-opus-4-7` | Qualité maximale |

**OpenAI**

| Modèle | Usage |
|---|---|
| `gpt-4o-mini` | Rapide, économique |
| `gpt-5.4-nano` | GPT-5 économique |
| `gpt-5.4-mini` | GPT-5 équilibré |
| `gpt-5.5` | Qualité maximale |