# Übersicht über Demonstrator

## Backend
```
uvicorn app.main:app --reload

python example_case.py 
#lädt die Beispielfälle in die DB

```

## Frontend
```
npm run dev
#Frontend auf Port 5173
```

Zur Bedienung: +

Neuen Call Starten, dafür Case auswählen

Regler Auto-Run (default = off) startet den ABCDE Agenten nach jeder Nachricht 

Wenn man den Call in der Menüleiste abschließt, öffnet sich ein Feedbackfenster, also gerne auch Probanden die Calls selbst durchspielen und evaluieren lassen 

Super wäre es, wenn ich im Anschluss deine sim.db bekommen kann, für Calls und Feedback