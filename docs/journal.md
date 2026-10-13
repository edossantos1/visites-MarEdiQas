# TP01

## Délai de changement
- Le temps écoulé entre notre premier commit et sa fusion sur main a été d'environ 24 heures (travail réparti sur deux jours).
- Ce qui nous a pris le plus de temps : L'organisation et la synchronisation à trois personnes sur un TP initialement prévu pour un binôme, ainsi que la configuration des clés GPG au tout début.

## Indépendance vis-à-vis de GitHub
- Ce qui marcherait tel quel sur GitLab ou Gitea : Toutes les commandes `git` natives (commit, push, pull, rebase, tag) et le fonctionnement en local des hooks `pre-commit`[cite: 18].
- Ce qui changerait : L'utilisation de l'outil en ligne de commande `gh` (GitHub CLI) qui est exclusif à GitHub pour créer, lister ou approuver des Pull Requests depuis le terminal[cite: 18].

## Signature des commits
Nous signons les commits car la forge vérifie seulement qui possède les droits d'accès pour pousser le code, mais pas qui l'a réellement écrit[cite: 18]. La signature garantit de façon cryptographique l'identité de l'auteur du commit, ce qui reste valable même si le dépôt est cloné par quelqu'un d'autre ou migré vers une autre plateforme (contrairement à un simple `git config user.name` qui peut être usurpé)[cite: 18].
