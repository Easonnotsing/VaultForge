# Fixtures

Tests build temporary Obsidian vaults from these fixture patterns:

- a roadmap file named `学习路线图 - {主题}.md`
- H2/H3 folder structure
- MOC files under H3 folders
- atomic notes with explicit logical-relation language

The temporary vaults are created at test runtime so tests do not mutate example
content in this repository.
