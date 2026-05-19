# Fixtures

## sample_vault

A minimal Obsidian vault used by integration tests:

```
sample_vault/
├── 学习路线图 - 平台战略.md                    # Outline roadmap
├── 学习路线图（完整版） - 平台战略.md          # Complete roadmap with source_range
└── 01. 平台战略/
    ├── 网络效应/
    │   ├── 网络效应 MOC.md
    │   ├── 网络效应类型.md                     # Contains derivation lexemes (因此)
    │   └── 网络效应与平台增长.md               # Contains analogy lexemes (类似于)
    └── 生态治理/
        ├── 生态治理 MOC.md
        └── 平台治理机制.md                     # Contains contradiction lexemes (然而)
```

### Fixture design principles

- Atomic notes use explicit logical-relation language to trigger heuristic rules
- Roadmap files include `source_range` annotations for context-extractor tests
- MOC files are present for roadmap-MOC bidirectional link tests
- All notes have `status: filled` frontmatter to skip draft-only filters

### Usage

Tests build temporary vaults from these patterns at runtime. No test mutates fixture content on disk.
