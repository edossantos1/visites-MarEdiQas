# TP01

## Délai de changement
- Le temps écoulé entre notre premier commit et sa fusion sur main a été d'environ 24 heures (travail réparti sur deux jours).
- Ce qui nous a pris le plus de temps : L'organisation et la synchronisation à trois personnes sur un TP initialement prévu pour un binôme, ainsi que la configuration des clés GPG au tout début.

## Indépendance vis-à-vis de GitHub
- Ce qui marcherait tel quel sur GitLab ou Gitea : Toutes les commandes `git` natives (commit, push, pull, rebase, tag) et le fonctionnement en local des hooks `pre-commit`[cite: 18].
- Ce qui changerait : L'utilisation de l'outil en ligne de commande `gh` (GitHub CLI) qui est exclusif à GitHub pour créer, lister ou approuver des Pull Requests depuis le terminal[cite: 18].

## Signature des commits
Nous signons les commits car la forge vérifie seulement qui possède les droits d'accès pour pousser le code, mais pas qui l'a réellement écrit[cite: 18]. La signature garantit de façon cryptographique l'identité de l'auteur du commit, ce qui reste valable même si le dépôt est cloné par quelqu'un d'autre ou migré vers une autre plateforme (contrairement à un simple `git config user.name` qui peut être usurpé)[cite: 18].

## TP02 — Protéger le dépôt

### Règles mises en place
- Ruleset « main » : PR obligatoire avec 1 approbation et « dismiss stale approvals », historique linéaire, commits signés, suppression et force push bloqués.
- Tests : push direct sur main refusé (GH013) ; PR avec commit non signé affichée « Unverified », fusion bloquée.
- CODEOWNERS : la PR Dependabot (#16), qui touche .github/, a demandé automatiquement la revue d'edossantos1.
- Dependabot : pip, github-actions et docker, en hebdomadaire, préfixe chore(deps).

### gitleaks
- Faux secret AWS_SECRET_ACCESS_KEY planté dans app/config.py : commit refusé par le hook (RuleID generic-api-key, entropie 4.68, ligne 11).
- Variable renommée en MA_VARIABLE avec la même valeur : commit accepté. La règle generic-api-key s'appuie sur le nom de la variable ; la valeur seule ne suffit pas.
- Scan de l'historique (gitleaks git, toutes branches) : aucune fuite. Notre dépôt n'a pas été créé depuis le modèle du formateur : le commit piégé n'a jamais été copié. Rapport : docs/gitleaks.json (code retour 0), donc pas de .gitleaksignore nécessaire.
- Rotation : si un vrai jeton avait été trouvé, il serait considéré comme compromis dès le push. On le révoquerait chez le fournisseur et on en générerait un nouveau, que l'historique soit réécrit ou non.

### Q1. Quelles règles auraient empêché le secret d'arriver sur main ?
- Humaine : la revue obligatoire (faillible, un secret passe facilement inaperçu dans un diff).
- Automatiques : gitleaks en pre-commit (local, contournable avec --no-verify) et un contrôle gitleaks requis en CI (imposé côté serveur, prévu au TP03).
- La plus fiable : le contrôle requis côté serveur, ou la push protection de GitHub, qui refuse le push lui-même.

### Q2. gitleaks en pre-commit protège-t-il un collègue qui ne l'a pas installé ?
- Non : les hooks restent locaux, ils ne sont pas transmis par git clone. Il faut lancer gitleaks dans le pipeline CI et en faire un contrôle requis dans le ruleset.

### Q3. Combien de temps un secret poussé sur une forge publique reste-t-il privé ?
- Quasiment pas : des robots scrutent les dépôts publics en continu, en quelques secondes ou minutes. GitHub Secret Scanning prévient les fournisseurs partenaires (AWS, GitHub, Slack, etc.), qui peuvent révoquer leurs jetons automatiquement.

### Réponses aux questions des étapes
- Dismiss stale approvals : sans cette option, on pourrait faire approuver une PR inoffensive puis pousser du code malveillant avant la fusion.
- Code owner absent : la PR reste bloquée. Il faut au moins deux propriétaires par chemin sensible, ou un administrateur autorisé à contourner la règle de façon tracée.
- PR Dependabot : un humain doit l'approuver (et un code owner si elle touche .github/). C'est une bonne chose : une mise à jour peut être compromise (attaque de la chaîne d'approvisionnement), un robot ne doit pas faire entrer seul une dépendance dans main.
