*Introduction au DevOps*

# TP01 — Forge, dépôt fil rouge et flux de travail

Compte-rendu du trinôme

| Élément | Valeur |
| --- | --- |
| Membres | Marouane Aliouche · Edivasco Dos Santos · Qassim Messili |
| Dépôt GitHub | github.com/edossantos1/visites-MarEdiQas |
| Date de la séance | 12 octobre 2026 |
| État du rendu | Étapes 1 à 4 réalisées ; étapes 5 à 7 en cours (parties surlignées à compléter) |

## 1. Contexte et organisation

Le TP met en place le dépôt « visites » (API FastAPI avec compteur Redis, tests pytest, ruff) qui servira jusqu'à la restitution, et fait pratiquer GitHub Flow : branches courtes, commits conventionnels signés, pull requests, revue croisée, fusion par squash, résolution de conflit par rebase et contrôles automatisés.

Le sujet est prévu pour un binôme. Nous l'avons réalisé à trois en ajoutant une troisième fonctionnalité et en faisant tourner la revue, afin que chaque membre relise une PR et soit relu une fois.

### 1.1 Répartition des rôles

| Rôle | Membre | Login GitHub | Responsabilités |
| --- | --- | --- | --- |
| A | Edivasco Dos Santos | edossantos1 | Crée le dépôt et invite les autres ; feat/version-header ; pre-commit ; tag v0.1.0 |
| B | Marouane Aliouche | malirouad-arch | feat/reset (POST /reset) ; CONTRIBUTING.md ; vérifie le tag |
| C | Qassim Messili | qassimMessili | feat/lecture (GET /visites) ; modèle de PR ; vérifie le tag |

### 1.2 Revue en rond

| Auteur | PR | Relecteur (approuve et fusionne) |
| --- | --- | --- |
| A — Edivasco | feat/version-header (#3) | B — Marouane |
| B — Marouane | feat/reset (#2) | C — Qassim (Edivasco à défaut) |
| C — Qassim | feat/lecture | A — Edivasco |

## 2. Environnement de travail

Poste de Marouane : machine virtuelle Debian, utilisateur `user1`. Les autres membres utilisent leur propre poste.

| Outil | Version constatée | Remarque |
| --- | --- | --- |
| Python | 3.13.5 | Conforme au prérequis 3.13 |
| Git | sortie de git --version **[À COMPLÉTER]** | Version Debian, à comparer à 2.56 |
| GitHub CLI (gh) | sortie de gh --version **[À COMPLÉTER]** | Installé depuis le dépôt officiel cli.github.com |
| Docker | docker.io (Debian) | hello-world OK après ajout de user1 au groupe docker |
| Redis | redis:8-alpine | Lancé en conteneur ; fakeredis dans les tests |

## 3. Étape 1 — Configuration de Git, de la clé SSH et de la signature

Chaque membre a configuré son identité, généré une clé ed25519 et l'a déclarée deux fois sur GitHub : comme clé d'authentification et comme clé de signature. Exemple pour Marouane :

```
git config --global user.name "Marouane Aliouche"
git config --global user.email "malirouad@gmail.com"
git config --global init.defaultBranch main
git config --global pull.rebase true

ssh-keygen -t ed25519 -C "malirouad@gmail.com"
gh auth login                                   # SSH, authentification par navigateur
gh auth refresh -h github.com -s admin:ssh_signing_key
gh ssh-key add ~/.ssh/id_ed25519.pub --title debian --type signing

git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
git config --global tag.gpgsign true
echo "malirouad@gmail.com $(cat ~/.ssh/id_ed25519.pub)" > ~/.ssh/allowed_signers
git config --global gpg.ssh.allowedSignersFile ~/.ssh/allowed_signers
ssh -T git@github.com
```

#### Résultats

```
$ ssh -T git@github.com
Hi malirouad-arch! You've successfully authenticated, but GitHub does not provide shell access.

$ gh ssh-key list
TITLE   ID         KEY                      TYPE            ADDED
debian  166169690  ssh-ed2551...kTPXBacQlP  authentication  about 1 hour ago
debian  1237173    ssh-ed2551...kTPXBacQlP  signing         about 1 hour ago

$ git config --global --list
user.name=Marouane Aliouche
user.email=malirouad@gmail.com
user.signingkey=/home/user1/.ssh/id_ed25519.pub
init.defaultbranch=main
pull.rebase=true
gpg.format=ssh
commit.gpgsign=true
tag.gpgsign=true
gpg.ssh.allowedsignersfile=/home/user1/.ssh/allowed_signers
```

#### Adaptation à trois

Chaque membre ajoute aussi les clés publiques des deux autres à son fichier `allowed_signers`, sinon Git ne peut pas vérifier leurs commits ni le tag :

```
echo "edivasco.dossantos@edu.igensia.com $(curl -s https://github.com/edossantos1.keys | head -1)" >> ~/.ssh/allowed_signers
echo "qmessili@gmail.com $(curl -s https://github.com/qassimMessili.keys | head -1)" >> ~/.ssh/allowed_signers
```

> **[À COMPLÉTER]** ajouter la clé de Qassim une fois son étape 1 terminée (sa clé n'était pas encore publiée sur GitHub pendant la séance).

**Question :** *que contient ~/.ssh/allowed_signers et à quoi sert-il pour git log --show-signature ?*

Le fichier liste des paires « identité (e-mail) → clé publique » auxquelles on fait confiance. `git log --show-signature` s'en sert, via `ssh-keygen -Y verify`, pour vérifier qu'une signature SSH a bien été produite par une clé autorisée pour l'e-mail de l'auteur. Sans ce fichier, Git affiche une erreur au lieu de « Good "git" signature ».

## 4. Étape 2 — Création du dépôt et premiers tests

Edivasco (A) a créé le dépôt `edossantos1/visites-MarEdiQas`, puis a ajouté Marouane et Qassim comme collaborateurs. La structure du projet (app/, tests/, pyproject.toml) a été posée dans un commit signé « chore: structure initiale du projet ». Chaque membre a ensuite cloné le dépôt, créé son environnement virtuel et lancé les tests.

```
git clone git@github.com:edossantos1/visites-MarEdiQas.git && cd visites-MarEdiQas
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
docker run -d --name redis -p 6379:6379 redis:8-alpine
pytest -q
uvicorn app.main:app --reload &
curl -s localhost:8000/ ; curl -s localhost:8000/
```

#### Résultats

```
$ pytest -q
...                                                                  [100%]
3 passed, 1 warning in 0.46s
```

Les tests utilisent `fakeredis` via une fixture pytest : ils tournent sans dépendre du conteneur Redis. L'avertissement (DeprecationWarning sur `anyio.abc.BlockingPortal`) vient de la bibliothèque Starlette, pas de notre code.

> **[À COMPLÉTER]** coller la sortie des deux appels `curl -s localhost:8000/` (attendu : {"visites": 2} au second) et un extrait de `/metrics`.

**Question :** *qu'est-ce qui distingue « créer depuis un modèle » d'un fork ?*

Un dépôt créé depuis un modèle est indépendant : son historique repart d'un seul commit initial et il n'a aucun lien avec le modèle. Un fork copie tout l'historique et reste rattaché au dépôt d'origine (réseau de forks) : il sert à proposer des PR à ce dépôt ou à se resynchroniser avec lui.

## 5. Étape 3 — Une fonctionnalité par membre

Chaque membre est parti de `main` à jour, a créé sa branche, a codé sa fonctionnalité avec un test, puis a ouvert une pull request au titre conventionnel.

| Membre | Branche / PR | Fonctionnalité |
| --- | --- | --- |
| Edivasco (A) | feat/version-header — #3 | En-tête X-Visites-Version: 0.1.0 sur la réponse de GET / |
| Marouane (B) | feat/reset — #2 | POST /reset remet le compteur à zéro et renvoie {"visites": 0} |
| Qassim (C) | feat/lecture — n° de PR **[À COMPLÉTER]** | GET /visites lit le compteur sans l'incrémenter (ajout pour le trinôme) |

#### Fonctionnalité de Marouane : POST /reset

```
# app/main.py
@app.post("/reset")
def reset():
    r.set("visites", 0)
    return {"visites": 0}

# tests/test_api.py
def test_reset(client):
    client.get("/")
    resp = client.post("/reset")
    assert resp.status_code == 200
    assert resp.json() == {"visites": 0}
    assert client.get("/").json() == {"visites": 1}
```

```
git switch main && git pull
git switch -c feat/reset
pytest -q
git add -p
git commit -m "feat(api): ajouter POST /reset pour remettre le compteur à zéro"
git commit -m "test(api): vérifier POST /reset"
git push -u origin feat/reset
gh pr create --base main --title "feat(api): ajouter POST /reset pour remettre le compteur à zéro"
```

> **[À COMPLÉTER]** ajouter le code de la fonctionnalité d'Edivasco (en-tête) et de Qassim (GET /visites), ou une capture de leurs PR.

## 6. Étape 4 — Revue croisée et fusion par squash

### 6.1 PR #3 (feat/version-header), relue par Marouane

Marouane a récupéré la branche, relancé les tests et demandé l'ajout d'un test vérifiant que l'en-tête ne casse pas le compteur. Edivasco a répondu par un nouveau commit (sans amend ni force push) :

```
def test_version_header_et_compteur(client):
    r1 = client.get("/")
    r2 = client.get("/")
    assert r2.headers["X-Visites-Version"] == "0.1.0"
    assert r2.json()["visites"] == r1.json()["visites"] + 1
```

```
$ gh pr checkout 3 && git pull && pytest -q
5 passed, 1 warning in 0.45s
$ gh pr review 3 --approve
✓ Approved pull request edossantos1/visites-MarEdiQas#3
$ gh pr merge 3 --squash --delete-branch
✓ Squashed and merged pull request edossantos1/visites-MarEdiQas#3
✓ Deleted local branch feat/version-header and switched to branch main
✓ Deleted remote branch feat/version-header
```

> **[À COMPLÉTER]** vérifier que la demande de changement est bien tracée sur GitHub : `gh pr view 3 --json reviews` doit montrer CHANGES_REQUESTED avant APPROVED.

### 6.2 PR #2 (feat/reset) : mise à jour par rebase et premier conflit réel

Après la fusion de la #3, `main` avait avancé. Marouane a rebasé sa branche sur le nouveau `main`. Les deux PR ajoutaient leurs tests au même endroit de `tests/test_api.py`, d'où un conflit.

```
git switch feat/reset
git fetch origin
git rebase origin/main
# CONFLICT : modifié des deux côtés : tests/test_api.py
# résolution : conserver les tests d'Edivasco ET test_reset, retirer les marqueurs
git add tests/test_api.py
git rebase --continue
pytest -q                     # 6 passed
git push --force-with-lease
```

```
$ git log --oneline --show-signature -3
a79cf2a Good "git" signature for malirouad@gmail.com with ED25519 key SHA256:XEW2a5/...
        test(api): vérifier POST /reset
8635ceb Good "git" signature for malirouad@gmail.com with ED25519 key SHA256:XEW2a5/...
        feat(api): ajouter POST /reset pour remettre le compteur à zéro
9624907 feat(api): exposer la version dans X-Visites-Version (#3)
```

L'historique reste linéaire : les commits de la branche sont rejoués au-dessus du commit squashé de la #3, sans commit de fusion.

> **[À COMPLÉTER]** confirmer la fusion de la PR #2 (relecteur, demande de changement, squash) avec `gh pr view 2 --json state,reviews`. Le commit e91432a (test du code HTTP 200) a été poussé après la fusion : le passer dans une petite PR `test/reset-http` ou le documenter.

### 6.3 Observation sur les signatures

Avant ce rebase, Edivasco avait rebasé la branche de Marouane sur son propre poste. Les commits portaient alors l'auteur « Marouane Aliouche » mais la signature d'Edivasco :

```
commit d8ba921
Good "git" signature for edivasco.dossantos@edu.igensia.com with ED25519 key SHA256:EJfTXNau...
Author: Marouane Aliouche <malirouad@gmail.com>
```

Un rebase recrée les commits : la signature est celle de la personne qui réécrit, pas celle de l'auteur d'origine. Marouane a refait le rebase lui-même, et ses commits sont de nouveau signés avec sa clé. Règle retenue pour la suite : on ne réécrit pas la branche d'un autre sans le prévenir.

**Question :** *après le squash, que devient la branche locale feat/… et pourquoi git branch -d peut refuser de la supprimer ?*

Le squash crée sur `main` un commit neuf, avec un autre hash. Les commits de la branche locale ne sont donc pas ancêtres de `main`, et `git branch -d` refuse (« not fully merged ») par sécurité, alors que leur contenu est bien dans `main`. On supprime avec `git branch -D`. Avec `gh pr merge --delete-branch`, gh supprime directement la branche locale et la branche distante.

## 7. Étape 5 — Conflit volontaire en cascade sur le README

Adaptation à trois : les trois membres modifient la même ligne du README depuis le même `main`. A fusionne en premier ; B rebase, résout et fusionne ; C rebase à son tour et résout contre la version déjà réconciliée par B.

```
# Les trois, AVANT toute fusion
git switch main && git pull
git switch -c docs/titre-a          # B : docs/titre-b · C : docs/titre-c
git commit -am "docs: reformuler le titre du README"
git push -u origin docs/titre-a
gh pr create --base main --title "docs: reformuler le titre du README" --body "Conflit volontaire"

# B, après la fusion de A (puis C, après la fusion de B)
git switch docs/titre-b && git fetch origin && git rebase origin/main
# corriger README.md, retirer <<<<<<< ======= >>>>>>>
git add README.md                   # git add --resolved si Git >= 2.56
git rebase --continue
git push --force-with-lease
```

> **[À COMPLÉTER]** coller la sortie du conflit, le titre réconcilié final et `git log --oneline --graph -6` montrant l'historique linéaire.

**Question :** *pourquoi --force-with-lease et pas --force ? Que vérifie-t-il ?*

`--force-with-lease` n'écrase la branche distante que si elle pointe encore sur le commit vu lors du dernier fetch (la branche de suivi `origin/<branche>`). Si quelqu'un a poussé entre-temps, le push est refusé au lieu d'effacer son travail. `--force` écrase sans rien vérifier. Le cas s'est présenté pendant la séance : la branche feat/reset avait été réécrite depuis un autre poste, et seul un fetch préalable permet de le voir.

## 8. Étape 6 — pre-commit, CONTRIBUTING.md, modèle de PR et tag v0.1.0

| Membre | Branche | Livrable |
| --- | --- | --- |
| Edivasco (A) | chore/pre-commit | .pre-commit-config.yaml (hooks de base + ruff) |
| Marouane (B) | docs/contributing | CONTRIBUTING.md (flux, conventions, tests) |
| Qassim (C) | docs/pr-template | .github/PULL_REQUEST_TEMPLATE.md |

#### .pre-commit-config.yaml

```
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0          # mis à jour par pre-commit autoupdate
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0          # mis à jour par pre-commit autoupdate
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

#### Tag signé

```
# A, après fusion des trois PR
git switch main && git pull
git tag -s v0.1.0 -m "Première version : API, tests, pre-commit"
git push origin v0.1.0
# B et C
git fetch --tags && git tag -v v0.1.0
```

> **[À COMPLÉTER]** coller la sortie de `pre-commit run --all-files` (tout en Passed) et celle de `git tag -v v0.1.0` chez B et chez C.

**Question :** *que se passe-t-il si on commite un fichier Python mal formaté ? Et avec git commit --no-verify ?*

Le hook `ruff-format` échoue, reformate le fichier et le commit est annulé : il faut refaire `git add` puis `git commit`. Avec `--no-verify`, les hooks sont sautés et le commit passe tel quel. pre-commit est donc un garde-fou local contournable, d'où l'intérêt de rejouer les mêmes contrôles en intégration continue dans les TP suivants.

## 9. Étape 7 — Journal et questions d'observation

### Q1. Délai entre premier commit et fusion sur main

| Membre | PR | Premier commit | Fusion | Délai |
| --- | --- | --- | --- | --- |
| Edivasco | #3 | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** |
| Marouane | #2 | 12/10/2026 14:06 | **[À COMPLÉTER]** | **[À COMPLÉTER]** |
| Qassim | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** | **[À COMPLÉTER]** |

Mesure : `gh pr list --state merged --json number,title,createdAt,mergedAt` et `gh pr view <n> --json commits`.

### Q2. Ce qui ne dépend pas de GitHub

- **Indépendant de la forge** : configuration Git, clé et signature SSH, `allowed_signers`, branches, Conventional Commits, rebase et résolution de conflit, `--force-with-lease`, tag signé, pre-commit. Tout cela fonctionnerait tel quel sur GitLab, Gitea ou Forgejo.
- **Spécifique à GitHub** : les commandes `gh` (création de dépôt, ajout de collaborateurs via l'API, PR, revue, fusion), le badge « Verified », la signature des commits squashés par la clé web-flow de GitHub et le dossier `.github/`. Sur GitLab, on utiliserait `glab` et des merge requests ; sur Gitea ou Forgejo, `tea` ou l'interface web.

### Q3. Pourquoi signer si la forge vérifie déjà qui pousse ?

- La forge authentifie la personne qui pousse, pas l'auteur des commits : `user.name` et `user.email` sont du texte libre.
- Dans notre trinôme, Edivasco a poussé des commits dont l'auteur affiché était Marouane. Seule la signature montrait qui avait réellement produit ces commits.
- La signature voyage avec le commit : elle reste vérifiable hors ligne, dans n'importe quel clone, et après migration vers une autre forge.

### Ce qui nous a pris le plus de temps

Pour Marouane, l'essentiel du temps est passé dans la préparation du poste plutôt que dans Git lui-même (détail en section 10).

> **[À COMPLÉTER]** ajouter les points d'Edivasco et de Qassim.

## 10. Difficultés rencontrées et solutions

| Problème | Cause | Solution |
| --- | --- | --- |
| git et gh introuvables | Debian minimale, outils non installés | apt install git ; gh depuis le dépôt officiel cli.github.com |
| Clé SSH refusée (Permission denied) | Configuration lancée en root : clé dans /root/.ssh, pas dans /home/user1 | Tout refaire en user1 ; suppression de la clé « root » ajoutée par erreur au compte GitHub |
| gh auth login bloqué | Pas de navigateur ni de presse-papier dans la VM | GH_BROWSER=echo puis saisie du code sur github.com/login/device depuis le PC |
| gh ssh-key add --type signing refusé | Scope admin:ssh_signing_key manquant | gh auth refresh -s admin:ssh_signing_key |
| Docker : permission denied | user1 absent des groupes docker et sudo | su - -c "usermod -aG docker,sudo user1" puis reconnexion |
| Commandes collées non exécutées | Le mot « bash » (étiquette du bloc) collé ouvrait des shells imbriqués | Ne copier que les commandes ; fermer la fenêtre plutôt que taper exit |
| Commits signés par un autre membre | Branche de Marouane rebasée sur le poste d'Edivasco | Rebase refait par l'auteur ; règle : ne pas réécrire la branche d'un autre |
| Conflit sur tests/test_api.py | Deux PR ajoutant des tests au même endroit | Rebase sur main, conservation des deux blocs de tests |

## 11. Grille « Acquis si » — état d'avancement

| Critère | État | Preuve |
| --- | --- | --- |
| Trois fonctionnalités, trois PR revues et squashées | En cours | #3 fusionnée ; #2 à confirmer ; PR de Qassim à ouvrir |
| Historique linéaire | OK à ce stade | git log --merges --oneline main : vide |
| Commits conventionnels et signés | OK à ce stade | feat:, test:, chore: ; Good "git" signature |
| Conflit résolu par rebase, sans commit de fusion | Partiel | Conflit réel sur test_api.py résolu ; conflit README à faire |
| pre-commit (hooks de base + ruff) installé et vert | À faire | Étape 6 |
| CONTRIBUTING.md, README.md, docs/cartographie.md, docs/journal.md | À faire | Étapes 3, 6 et 7 |
| Tag v0.1.0 signé et poussé | À faire | Étape 6 |

## Annexe — Historique du dépôt

```
$ git log --oneline origin/main
9624907 feat(api): exposer la version dans X-Visites-Version (#3)
7738b5f chore: structure initiale du projet (app, tests, config)
f5cdf43 Initial commit
```

`f5cdf43` et `9624907` sont créés par GitHub (création du dépôt, fusion squash) et signés avec la clé GPG web-flow de GitHub (`B5690EEEBB952194`). Pour les vérifier en local : `curl -s https://github.com/web-flow.gpg | gpg --import`.

> **[À COMPLÉTER]** remplacer par l'historique final après l'étape 7 : `git log --oneline --graph` et `git log --show-signature -5`.
