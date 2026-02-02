# 🤖 Multi-Agent Development Framework

Structure hiérarchique d'agents IA pour le développement du projet Expense Tracker.

## Hiérarchie

```
┌─────────────────────────────────────────────────────────┐
│  NIVEAU 0 : STAKEHOLDER (Thomas)                        │
│  → Valide le résultat final                             │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│  NIVEAU 1 : JARVIS (Agent 0 - Stratège)                 │
│  → Reçoit la vision, coordonne, livre                   │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│  NIVEAU 2 : PROJECT MANAGER (Agent 1)                   │
│  → Découpe, distribue, assemble                         │
└───┬─────────┬─────────┬─────────┬───────────────────────┘
    │         │         │         │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│Agent 2│ │Agent 3│ │Agent 4│ │Agent 5│
│Backend│ │Frontend│ │  QA   │ │ Docs  │
└───────┘ └───────┘ └───────┘ └───────┘
```

## Agents

| ID | Nom | Rôle | Focus |
|----|-----|------|-------|
| 0 | Jarvis | Stratège | Vision globale, validation |
| 1 | ProjectManager | Chef de Projet | Planning, coordination |
| 2 | BackendArchitect | Architecte Backend | API, DB, Sécurité |
| 3 | FrontendDev | Développeur Frontend | UI, UX, Intégration |
| 4 | QAController | Contrôleur Qualité | Tests, Bugs, Refactor |
| 5 | TechWriter | Documentaliste | README, API docs, Guides |

## Workflow

1. **Stakeholder** → Envoie le cahier des charges
2. **Jarvis** → Transmet au ProjectManager
3. **ProjectManager** → Découpe en tâches, distribue
4. **Agents 2-5** → Exécutent leurs tâches
5. **QAController** → Valide le code
6. **TechWriter** → Documente
7. **ProjectManager** → Assemble et rapporte
8. **Jarvis** → Valide et livre au Stakeholder
