# 🎭 Orchestration des Agents

## Comment utiliser le système multi-agents

### Lancer une tâche

Pour lancer une amélioration ou feature :

```
@jarvis lance le projet expense-tracker avec la tâche : [DESCRIPTION]
```

### Workflow automatique

1. **Jarvis (moi)** reçoit la demande
2. Je spawn le **ProjectManager** avec la tâche
3. Le PM découpe en sous-tâches
4. Je spawn les agents spécialisés en parallèle :
   - **BackendArchitect** pour les tâches API/DB
   - **FrontendDev** pour les tâches UI
5. Je spawn **QAController** pour valider
6. Je spawn **TechWriter** pour documenter
7. Je compile le tout et livre

### Labels des sessions

| Agent | Label session |
|-------|---------------|
| ProjectManager | `expense-pm` |
| BackendArchitect | `expense-backend` |
| FrontendDev | `expense-frontend` |
| QAController | `expense-qa` |
| TechWriter | `expense-docs` |

### Commandes Jarvis

- `status agents` → État des agents actifs
- `sync agents` → Récupère les outputs de tous les agents
- `kill agents` → Termine toutes les sessions agents

## Structure des tâches

```json
{
  "task_id": "TASK-001",
  "title": "Améliorer le parsing multi-TVA",
  "priority": "high",
  "assigned_to": ["backend"],
  "status": "in_progress",
  "subtasks": [
    {
      "agent": "backend",
      "description": "Parser plusieurs lignes TVA",
      "status": "pending"
    }
  ]
}
```
