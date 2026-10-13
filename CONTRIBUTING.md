# Contribuer au projet

## Flux de travail (GitHub Flow)
1. Partir de `main` à jour : `git switch main && git pull`
2. Créer une branche courte : `git switch -c feat/ma-fonctionnalite`
3. Faire des commits petits, conventionnels et signés
4. Pousser la branche et ouvrir une pull request : `gh pr create --fill --base main`
5. Revue par un autre membre du binôme (au moins un commentaire, puis approbation)
6. Fusion par squash et suppression de la branche : `gh pr merge <num> --squash --delete-branch`

Règles :
- jamais de push direct sur `main`
- jamais de commit de fusion : on met à jour sa branche avec `git rebase origin/main`
- après un rebase, pousser avec `git push --force-with-lease` (jamais `--force`)

## Convention de commits
Format [Conventional Commits](https://www.conventionalcommits.org/fr/v1.0.0/) : `type(portée): description`

| Type | Usage |
|---|---|
| `feat` | nouvelle fonctionnalité |
| `fix` | correction de bug |
| `test` | ajout ou modification de tests |
| `docs` | documentation |
| `chore` | maintenance, configuration |

Exemple : `feat(api): ajouter POST /reset`

## Lancer les tests
    python3 -m venv .venv && source .venv/bin/activate
    pip install -e ".[dev]"
    docker run -d --name redis -p 6379:6379 redis:8-alpine
    pytest -q

## pre-commit
    pip install pre-commit
    pre-commit install
    pre-commit run --all-files
