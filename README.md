# Capitano Game 🚀

Un platform game 2D side-scroller sviluppato con **Python Arcade**, ambientato in una foresta aliena con effetto parallasse.

## 🎮 Caratteristiche

- **Grafica 1080p Fullscreen** con effetto parallasse a 7 strati
- **Supporto Controller Xbox** via XInput (Windows API)
- **Animazioni complete**: idle, walk, run, jump, crouch + varianti con sparo
- **Sistema di proiettili plasma** con animazione
- **Fisica**: gravità, salti e collisioni con il terreno
- **Input multipli**: Tastiera + Controller simultaneamente
- **FPS Counter** in tempo reale

## 🕹️ Controlli

### Tastiera
| Tasto | Azione |
|-------|--------|
| ← / → | Movimento sinistra/destra |
| Shift | Correre |
| Spazio | Salto |
| ↓ | Accovacciarsi |
| Z | Sparo |
| ESC | Chiudi gioco |

### Controller Xbox
| Pulsante | Azione |
|----------|--------|
| Stick sinistro | Movimento |
| A | Salto |
| RT (Grilletto destro) | Sparo |
| Stick sinistro ↓ | Accovacciarsi |

## 📁 Struttura del Progetto

```
C:\Users\rober\OneDrive\dev\py\arcade\
├── game.py                 # Entry point del gioco
├── README.md               # Questo file
├── classes/                # Moduli del gioco
│   ├── __init__.py         # Esportazioni principali
│   ├── config.py           # Costanti di gioco
│   ├── xinput_reader.py    # Lettura controller Xbox
│   ├── background_parallax.py  # Sfondo parallasse 7 strati
│   ├── bullet.py           # Proiettile plasma
│   ├── capitano.py         # Personaggio giocatore
│   └── game_view.py        # Logica principale (View Arcade)
├── sprites/                # Sprite sheet del personaggio
│   ├── captain_idle.png
│   ├── captain_idle_shot.png
│   ├── captain_walk.png
│   ├── captain_walk_shot.png
│   ├── captain_run.png
│   ├── captain_run_shot.png
│   ├── captain_jump.png
│   ├── captain_jump_shot.png
│   ├── captain_crouch.png
│   ├── captain_crouch_shot.png
│   └── sprite_bullet_plasma.png
└── images/                 # Sfondi parallasse
    ├── parallax_forest_1.png
    ├── parallax_forest_2.png
    ├── parallax_forest_3.png
    ├── parallax_forest_4.png
    ├── parallax_forest_5.png
    ├── parallax_forest_6.png
    └── parallax_forest_7.png
```

## ⚙️ Requisiti

- Python 3.12+
- Arcade Library
- Pyglet (dipendenza di Arcade)
- Windows (per il supporto XInput del controller)

## 🚀 Avvio

```bash
cd C:\Users\rober\OneDrive\dev\py\arcade
python game.py
```

Oppure esegui il file `run.bat`.

## 🛠️ Tecnologie

- **Arcade** — Game framework Python 2D
- **XInput API** — Lettura nativa controller Xbox via ctypes
- **Parallasse** — Scrolling a velocità diverse per profondità

## 📜 Licenza

Progetto personale per sviluppo e test.

---

*Creato con ❤️ e Python*
