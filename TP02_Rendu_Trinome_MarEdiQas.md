*Introduction au DevOps*

# TP02 — Protéger le dépôt

Compte-rendu du trinôme

| Élément | Valeur |
| --- | --- |
| Membres | Marouane Aliouche · Edivasco Dos Santos · Qassim Messili |
| Dépôt GitHub | github.com/edossantos1/visites-MarEdiQas |
| Date de la séance | 13 octobre 2026 |
| Point de départ | TP01 terminé, tag v0.1.0 signé sur main |

## 1. Objectif et organisation

Le TP02 verrouille la branche `main` pour que plus aucun changement n'y arrive sans pull request, revue, signature et historique linéaire. Il ajoute des responsables par dossier (CODEOWNERS), une veille automatique des dépendances (Dependabot) et une détection des secrets (gitleaks), avant de chercher un jeton planté par le formateur dans l'historique.

| Rôle | Membre | Tâches TP02 |
| --- | --- | --- |
| A | Edivasco (edossantos1) | Administrateur du dépôt : ruleset sur main, CODEOWNERS, alertes Dependabot |
| B | Marouane (malirouad-arch) | Dependabot, gitleaks dans pre-commit, test du faux secret, journal |
| C | Qassim (qassimMessili) | Tests de protection (push direct, commit non signé), relectures |
| Tous | — | Chasse au secret dans l'historique, relectures croisées |

## 2. Étape 1 — Règles de protection de main

Edivasco a créé un ruleset « main » ciblant la branche par défaut, via l'API GitHub :

```
{
  "name": "main", "target": "branch", "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_linear_history" },
    { "type": "required_signatures" },
    { "type": "pull_request", "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": true } }
  ]
}
```

Commande : `gh api -X POST repos/edossantos1/visites-MarEdiQas/rulesets --input ruleset.json`. La revue des code owners a été activée en second temps, après la fusion du fichier CODEOWNERS, pour éviter qu'Edivasco ne se bloque sur sa propre PR.

| Règle | Effet |
| --- | --- |
| deletion | Interdit de supprimer main |
| non_fast_forward | Bloque le force push |
| required_linear_history | Interdit les commits de fusion |
| required_signatures | N'accepte que des commits signés |
| pull_request | PR obligatoire, 1 approbation, approbation annulée en cas de nouveau push |

```
$ gh api repos/edossantos1/visites-MarEdiQas/rulesets --jq '.[] | .name + " " + .enforcement'
main active
```

#### Test 1 : push direct sur main

![Push direct refusé : GH013, « Changes must be made through a pull request »](TP02_images/capture-1.png)

*Push direct refusé : GH013, « Changes must be made through a pull request »*

Le commit local passe les hooks pre-commit, mais le serveur le refuse. Le commit de test est ensuite annulé avec `git reset --hard origin/main`.

#### Test 2 : commit non signé dans une PR

Qassim a poussé un commit créé avec `git -c commit.gpgsign=false` dans les PR #11 et #13 : le commit est marqué « Unverified » et la fusion est bloquée. Les deux PR ont ensuite été fermées et leurs branches supprimées.

![PR approuvée et checks verts, mais fusion bloquée : « Commits must have verified signatures »](TP02_images/capture-2.png)

*PR approuvée et checks verts, mais fusion bloquée : « Commits must have verified signatures »*

Même approuvée, la PR ne peut pas être fusionnée : la règle de signature s'applique indépendamment de la revue.

**Question :** *pourquoi « dismiss stale approvals » ? Quel scénario évite-t-il ?*

Sans cette option, une approbation reste valable même si le code change après coup : on peut faire approuver une PR inoffensive, puis pousser du code malveillant et fusionner. Avec l'option, tout nouveau push annule l'approbation. Nous l'avons constaté : une correction poussée sur une PR déjà relue a dû être réapprouvée.

## 3. Étape 2 — CODEOWNERS

Edivasco a ajouté `.github/CODEOWNERS` (PR #12, relue par Marouane). Les derniers motifs l'emportent :

```
*               @edossantos1 @malirouad-arch @qassimMessili
/.github/       @edossantos1
/infra/         @edossantos1
/app/           @malirouad-arch
/monitoring/    @malirouad-arch
/tests/         @qassimMessili @malirouad-arch
/docs/          @edossantos1 @malirouad-arch @qassimMessili
```

> **[À COMPLÉTER]** vérifier avec `cat .github/CODEOWNERS` que ce contenu correspond à la version fusionnée (un second propriétaire a pu être ajouté sur /.github/ suite à la revue).

Test : la PR #16 de Marouane modifie `.github/dependabot.yml`. GitHub a automatiquement demandé la revue d'edossantos1 en tant que code owner, et la PR n'a pu être fusionnée qu'après son approbation.

![PR #16 : « requested a review from edossantos1 as a code owner », commit Verified, PR fusionnée](TP02_images/capture-3.png)

*PR #16 : « requested a review from edossantos1 as a code owner », commit Verified, PR fusionnée*

**Question :** *que se passe-t-il si un propriétaire de code est le seul à pouvoir approuver et qu'il est absent ? Quelle règle prévoir ?*

La PR reste bloquée : personne d'autre ne peut fournir la revue requise. Il faut au moins deux propriétaires pour chaque chemin sensible, ou un rôle d'administration autorisé à contourner la règle de façon exceptionnelle et tracée. Dans notre fichier, `/.github/` n'a qu'Edivasco comme propriétaire : c'est précisément ce risque.

## 4. Étape 3 — Dependabot

```
version: 2
updates:
  - package-ecosystem: pip
    directory: /
    schedule: { interval: weekly }
    commit-message: { prefix: "chore(deps)" }
  - package-ecosystem: github-actions
    directory: /
    schedule: { interval: weekly }
    commit-message: { prefix: "chore(deps)" }
  - package-ecosystem: docker
    directory: /
    schedule: { interval: weekly }
    commit-message: { prefix: "chore(deps)" }
```

Fichier fusionné via la PR #16. Les alertes de sécurité Dependabot ont été activées par Edivasco (`gh api -X PUT repos/.../vulnerability-alerts`).

![Insights → Dependency graph → Dependabot : pip, actions et docker surveillés](TP02_images/capture-4.png)

*Insights → Dependency graph → Dependabot : pip, actions et docker surveillés*

Les trois écosystèmes sont reconnus ; leurs premières vérifications étaient en cours au moment de la capture. Les écosystèmes actions et docker n'ont encore rien à surveiller (pas de workflow ni de Dockerfile) : ils serviront à partir du TP03.

#### Premières PR Dependabot

Lors de son premier passage, Dependabot a ouvert cinq PR de mise à jour pip (à partir de la #19) :

| Branche Dependabot | Mise à jour proposée |
| --- | --- |
| dependabot/pip/fastapi-0.143.0 | fastapi → 0.143.0 |
| dependabot/pip/httpx-gte-0.28.1 | httpx >= 0.28.1 |
| dependabot/pip/pre-commit-gte-4.6.2 | pre-commit >= 4.6.2 |
| dependabot/pip/pytest-gte-9.1.1 | pytest >= 9.1.1 |
| dependabot/pip/setuptools-gte-84.0.0 | setuptools >= 84.0.0 |

![Le passage suivant s'arrête : « Dependabot cannot open any more pull requests »](TP02_images/capture-5.png)

*Le passage suivant s'arrête : « Dependabot cannot open any more pull requests »*

Ce message n'est pas une panne : Dependabot limite par défaut à 5 le nombre de ses PR ouvertes simultanément (open-pull-requests-limit). Il en ouvrira d'autres une fois les premières traitées. Pour éviter cette accumulation, nous regroupons les mises à jour pip en une seule PR avec l'option groups :

```
- package-ecosystem: pip

    directory: /
    schedule: { interval: weekly }
    commit-message: { prefix: "chore(deps)" }
    groups:
      dependances-pip:
        patterns: ["*"]
```

Chaque PR Dependabot reste soumise au ruleset : tests verts, approbation d'un membre, et revue d'Edivasco si elle touche .github/. Les commits créés par Dependabot sont signés par GitHub, donc acceptés par la règle de signature.

> **[À COMPLÉTER]** indiquer comment les 5 PR ont été traitées (fusionnées une à une ou remplacées par la PR groupée).

**Question :** *une PR Dependabot est ouverte par un robot ; avec nos règles, qui doit l'approuver et pourquoi est-ce une bonne chose ?*

Un membre de l'équipe doit l'approuver, et un code owner si elle touche `.github/` (mises à jour d'Actions). C'est une bonne chose : une nouvelle version de dépendance peut être compromise (attaque de la chaîne d'approvisionnement). Un robot ne doit pas pouvoir faire entrer seul du code tiers dans main.

## 5. Étape 4 — gitleaks en pre-commit

gitleaks 8.30.1 a été installé depuis le binaire officiel, puis ajouté aux hooks pre-commit (PR #14) :

```
- repo: https://github.com/gitleaks/gitleaks

    rev: v8.30.1
    hooks:
      - id: gitleaks
```

#### Faux secret planté

Sur la branche `chore/gitleaks`, une ligne `AWS_SECRET_ACCESS_KEY = "..."` avec une valeur aléatoire de 40 caractères a été ajoutée à `app/config.py`. Le commit a été refusé :

```
Detect hardcoded secrets.................................................Failed
- hook id: gitleaks
- exit code: 1

Finding:     AWS_SECRET_ACCESS_KEY = "REDACTED"
Secret:      REDACTED
RuleID:      generic-api-key
Entropy:     4.684184
File:        app/config.py
Line:        11
Fingerprint: app/config.py:generic-api-key:11
WRN leaks found: 1
```

#### Variable renommée

Même valeur, variable renommée en `MA_VARIABLE` : le commit est accepté (« Detect hardcoded secrets...Passed »). Ce commit local a été annulé immédiatement (`git reset --soft HEAD~1`), et `app/config.py` restauré : le faux secret n'a jamais été poussé. Seul le hook a été commité.

**Question :** *gitleaks a-t-il détecté le secret grâce au nom de la variable ou grâce à la valeur ?*

Grâce au nom. La règle `generic-api-key` exige d'abord un mot-clé dans l'identifiant (secret, key, token, access…), puis vérifie l'entropie de la valeur (4,68 ici, signe d'une chaîne aléatoire). Sans mot-clé, la même valeur passe. gitleaks est donc un filet, pas une garantie : un secret mal nommé lui échappe. Les jetons au format reconnaissable (AKIA…, ghp_…) sont en revanche détectés par des règles dédiées, quel que soit le nom.

## 6. Étape 5 — Secret dans l'historique et rotation

```
$ gitleaks git --verbose --redact --log-opts="--all" .
INF 27 commits scanned.
INF scanned ~24376 bytes (24.38 KB) in 248ms
INF no leaks found

$ gitleaks git --log-opts="--all" --report-path docs/gitleaks.json . ; echo $?
0
```

Aucun secret n'a été trouvé dans l'historique de notre dépôt. Explication : le dépôt n'a pas été créé depuis le modèle du formateur, Edivasco a posé la structure du projet à la main au TP01. Le commit piégé du dépôt modèle n'a donc jamais été copié chez nous. Le rapport `docs/gitleaks.json` est vide (`[]`, code retour 0) ; aucun faux positif n'existant, un fichier `.gitleaksignore` n'était pas nécessaire.

> **[À COMPLÉTER]** si l'URL du dépôt modèle est récupérée : lancer gitleaks sur un clone de celui-ci et noter ici le commit, l'auteur, la date et le fichier du jeton planté.

#### Décision de rotation

Un secret poussé sur une forge doit être considéré comme compromis dès le push, qu'on réécrive l'historique ou non : des copies peuvent déjà exister (clones, forks, robots). La procédure retenue : révoquer le jeton chez le fournisseur, en générer un nouveau stocké hors du dépôt (variable d'environnement ou gestionnaire de secrets), supprimer le fichier par PR et ajouter l'empreinte de l'ancien finding à `.gitleaksignore`. La réécriture de l'historique (git filter-repo) est optionnelle : elle oblige tous les membres à recloner et ne remplace jamais la révocation.

## 7. Questions d'observation (docs/journal.md)

### Q1. Quelles règles auraient empêché le secret d'arriver sur main ?

- **Humaine** : la revue obligatoire. Faillible, un secret passe facilement inaperçu dans un long diff.
- **Automatiques** : gitleaks en pre-commit (local, contournable avec `--no-verify`) et un contrôle gitleaks requis en CI (imposé côté serveur, prévu au TP03).
- **La plus fiable** : le contrôle automatique côté serveur, ou la push protection de GitHub qui refuse le push lui-même.

### Q2. gitleaks en pre-commit protège-t-il un collègue qui ne l'a pas installé ?

Non : les hooks sont locaux et ne sont pas transmis par `git clone`. Pour que la règle s'applique vraiment, il faut lancer gitleaks dans le pipeline CI et ajouter ce contrôle aux « status checks » requis du ruleset.

### Q3. Combien de temps un secret poussé sur une forge publique reste-t-il privé ?

Quasiment pas : des robots scrutent les dépôts publics en continu, l'exploitation peut commencer en quelques secondes ou minutes. GitHub Secret Scanning signale les jetons reconnus aux fournisseurs partenaires (AWS, GitHub, Slack, etc.), qui peuvent les révoquer automatiquement.

## 8. Pull requests du TP02

| PR | Titre | Auteur | Résultat |
| --- | --- | --- | --- |
| #11, #13 | chore: non signé (tests) | Qassim | Bloquées (Unverified), fermées |
| #12 | chore: ajouter CODEOWNERS | Edivasco | Relue par Marouane, fusionnée |
| #14 | chore: ajouter gitleaks au pre-commit | Marouane | Approuvée, fusionnée |
| #15 | Doublon de #14 (branche créée au mauvais endroit) | Marouane | Fermée |
| #16 | chore: configurer Dependabot pour pip, Actions et Docker | Marouane | Revue code owner (Edivasco), fusionnée |
| #17 | docs(journal): ajouter la section TP02 | Marouane | Fusionnée |
| #18 | docs(journal): préciser l'état de Dependabot | Marouane | état à confirmer **[À COMPLÉTER]** |

## 9. Difficultés et enseignements

| Problème | Cause | Solution / leçon |
| --- | --- | --- |
| PR #12 fermée par erreur | Clic sur « Close pull request » au lieu de « Review changes » | PR rouverte ; valider = onglet Files changed → Review changes → Approve |
| PR #15 en doublon | Branche chore/dependabot créée depuis chore/gitleaks, avant la fusion de CODEOWNERS | PR fermée, branche recréée depuis main à jour |
| « pre-commit configuration is unstaged » | La config modifiée n'était pas indexée | git add .pre-commit-config.yaml avant le commit |
| Ligne de journal absente de main | PR #17 fusionnée avant le dernier push | Nouvelle petite PR #18 |
| Approbation annulée après un push | dismiss stale approvals | Comportement voulu : réapprobation nécessaire |
| « Dependabot cannot open any more pull requests » | Limite par défaut de 5 PR ouvertes atteinte | Traiter les PR ou les regrouper avec groups |

## 10. Grille « Acquis si »

| Critère | État | Preuve |
| --- | --- | --- |
| Ruleset actif : PR + revue, historique linéaire, signature, force push bloqué | Acquis | main active ; push refusé GH013 ; PR non signées bloquées |
| CODEOWNERS valide et revue des propriétaires requise | Acquis | PR #16 : revue demandée à edossantos1 as a code owner |
| dependabot.yml fusionné pour pip, Actions et Docker | Acquis | PR #16 ; onglet Dependabot ; 5 premières PR pip ouvertes |
| gitleaks refuse le faux secret | Acquis | Hook Failed, generic-api-key, ligne 11 |
| Rapport historique propre | Acquis | 27 commits, code retour 0, docs/gitleaks.json |
| Journal : commit fautif identifié, rotation expliquée | Partiel | Rotation expliquée ; secret absent de notre dépôt (non créé depuis le modèle) |
