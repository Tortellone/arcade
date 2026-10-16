# Specifica Requisiti: UFO Sprite Module

## 1. Panoramica del Modulo (Overview)
* **ID Requisito:** SPEC-UFO-001
* **Obiettivo:** Definire l'architettura e il comportamento della classe `UFO` per la gestione, l'animazione e l'intelligenza artificiale (AI) del nemico UFO nel gioco.
* **Paradigma:** Spec-Driven Development (SDD)

---

## 2. Requisiti Funzionali (Requirements)

### REQ-01: Caricamento e Gestione Sprite Sheet
* **Sorgente Asset:** `sprites/sprite_ufo_96x96x20.png`
* **Dimensioni Frame:** $96 \times 96$ pixel per ciascun frame.
* **Layout Grid:** 5 righe e 4 colonne ($5 \times 4 = 20$ frame totali).
* **Indicizzazione:** 
  * Il frame `0` corrisponde all'angolo in alto a sinistra (Riga 1, Colonna 1).
  * Il frame `19` corrisponde all'angolo in basso a destra (Riga 5, Colonna 4).
* **Comportamento Animazione:** Riproduzione ciclica (loop) dei 20 frame.

### REQ-02: Comportamento AI e Movimento
* **Interfaccia:** La classe deve esporre un metodo pubblico `update_ai()` (o `AI()`).
* **Algoritmo di Movimento:**
  1. L'UFO si muove orizzontalmente sull'asse $X$.
  2. Direzione iniziale: Da sinistra a destra (oppure da destra a sinistra in base all'inizializzazione).
  3. **Rilevamento Confini (Collision Boundary):** Quando il margine dello sprite raggiunge il limite dello schermo (destro o sinistro), la direzione orizzontale viene invertita ($v_x = -v_x$).
  4. Il ciclo di pattugliamento orizzontale è infinito.

---

## 3. Architettura e Design della Classe (Class Specification)

### Struttura Modello (UFO Class Diagram Spec)

```text
+-------------------------------------------------------+
|                         UFO                           |
+-------------------------------------------------------+
| - image: Texture / Surface                            |
| - frames: Array[20] of Frame                          |
| - current_frame: Integer                              |
| - position: Vector2 (x, y)                            |
| - velocity: Vector2 (vx, vy)                          |
| - screen_bounds: Rect (min_x, max_x)                  |
+-------------------------------------------------------+
| + __init__(start_x, start_y, bounds)                  |
| + load_spritesheet(filepath: String)                  |
| + update(delta_time: Float)                           |
| + AI() : Void                                         |
| + render(canvas)                                      |
+-------------------------------------------------------+
```

---

## 4. Criteri di Accettazione e Test (Acceptance Criteria / BDD)

### Scenario 1: Caricamento corretto dei Frame
* **GIVEN** il file `sprites/sprite_ufo_96x96x20.png`
* **WHEN** la classe `UFO` viene inizializzata
* **THEN** la griglia $5 \times 4$ deve generare esattamente 20 ritagli di dimensione $96 \times 96$ px.

### Scenario 2: Inversione di rotta al confine Destro
* **GIVEN** un UFO in movimento verso destra ($v_x > 0$)
* **WHEN** la posizione `x + width` supera o eguaglia `screen_bounds.max_x`
* **THEN** l'algoritmo `AI()` deve invertire il segno della velocità ($v_x < 0$).

### Scenario 3: Inversione di rotta al confine Sinistro
* **GIVEN** un UFO in movimento verso sinistra ($v_x < 0$)
* **WHEN** la posizione `x` diventa minore o uguale a `screen_bounds.min_x`
* **THEN** l'algoritmo `AI()` deve invertire il segno della velocità ($v_x > 0$).

---

## 5. Tracciabilità (Traceability Matrix)

| Requisito ID | Componente | Test Associato | Stato |
| :--- | :--- | :--- | :--- |
| **REQ-01** | `load_spritesheet()` | `test_sprite_frame_extraction()` | Draft |
| **REQ-02** | `AI()` | `test_ufo_boundary_bounce()` | Draft |