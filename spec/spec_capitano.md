# Specifica Requisiti: Capitano Sprite Module

## 1. Panoramica del Modulo (Overview)
* **ID Requisito:** SPEC-CAP-001
* **Obiettivo:** Definire l'architettura e il comportamento della classe `Capitano` per la gestione, l'animazione e la fisica del personaggio giocatore nel gioco.
* **Paradigma:** Spec-Driven Development (SDD)

---

## 2. Requisiti Funzionali (Requirements)

### REQ-01: Caricamento e Gestione Sprite Sheet
Il personaggio `Capitano` utilizza **10 sprite sheet separati**, uno per ogni azione visiva completa.

* **Sorgente Asset:** `sprites/sprite_capitano_{action}.png`
* **Dimensioni Frame:** $100 \times 110$ pixel per ciascun frame.
* **Layout Grid:** 1 riga e 10 colonne ($1 \times 10 = 10$ frame totali per ogni sprite sheet).
* **Azioni Disponibili:**
  | Azione | File | FPS |
  | :--- | :--- | :--- |
  | `idle` | `sprite_capitano_idle.png` | 6.0 |
  | `idle_shot` | `sprite_capitano_idle_shot.png` | 12.0 |
  | `walk` | `sprite_capitano_walk.png` | 10.0 |
  | `walk_shot` | `sprite_capitano_walk_shot.png` | 12.0 |
  | `run` | `sprite_capitano_run.png` | 15.0 |
  | `run_shot` | `sprite_capitano_run_shot.png` | 12.0 |
  | `jump` | `sprite_capitano_jump.png` | 10.0 |
  | `jump_shot` | `sprite_capitano_jump_shot.png` | 12.0 |
  | `crouch` | `sprite_capitano_crouch.png` | 6.0 |
  | `crouch_shot` | `sprite_capitano_crouch_shot.png` | 12.0 |
* **Comportamento Animazione:** Riproduzione ciclica (loop) dei frame per ogni sprite sheet.

### REQ-02: Fisica del Personaggio
* **Gravità:** `GRAVITY = 0.6` applicata ad ogni frame.
* **Velocità Orizzontale:**
  * **Camminata:** `WALK_SPEED = 1.5` pixel/frame.
  * **Corsa:** `RUN_SPEED = 3.0` pixel/frame.
  * **Accovacciamento:** Velocità ridotta del 50%.
* **Salto:** `JUMP_SPEED = 14.0` (applicato a `change_y` quando `on_ground == True`).
* **Pavimento:** `GROUND_Y = 250`. Il personaggio non può scendere al di sotto di questa coordinata $Y$.

### REQ-03: Azione di Sparo
* **Durata Sparo:** `SHOOT_DURATION = 0.35` secondi.
* **Stato `is_shooting`:** Impostato su `True` quando il giocatore preme il tasto di sparo (tastiera `Z` o trigger destro del controller).
* **Transizione:** Dopo `SHOOT_DURATION`, lo stato torna automaticamente a `False` e l'animazione rientra nella variante non-sparo della stessa azione.
* **Proiettile:** Viene generato un oggetto `Bullet` alla posizione $(center_x \pm 35, center_y)$ diretto nella direzione in cui il personaggio guarda.

### REQ-04: Direzione dello Sprite
* **Proprietà `facing_right`:** Booleano che indica la direzione corrente.
* **Cambio Direzione:**
  * Se `facing_right == True`, `scale_x = 1` (sprite originale).
  * Se `facing_right == False`, `scale_x = -1` (sprite riflesso orizzontalmente).

---

## 3. Architettura e Design della Classe (Class Specification)

### Struttura Modello (Capitano Class Diagram Spec)

```text
+-------------------------------------------------------+
|                      Capitano                         |
+-------------------------------------------------------+
| - all_textures: Dict[str, Array[10] of Texture]       |
| - current_action: String                              |
| - time_counter: Float                                 |
| - facing_right: Boolean                               |
| - change_x: Float                                     |
| - change_y: Float                                     |
| - on_ground: Boolean                                  |
| - is_shooting: Boolean                                |
| - shoot_timer: Float                                  |
+-------------------------------------------------------+
| + __init__(center_x, center_y)                        |
| + _load_textures() -> Dict                            |
| + set_action(action: String)                          |
| + set_facing(facing_right: Boolean)                   |
| + start_shoot()                                       |
| + jump()                                              |
| + create_bullet() -> Bullet                           |
| + update_animation(delta_time: Float)                 |
| + update(delta_time: Float)                           |
+-------------------------------------------------------+
```

---

## 4. Criteri di Accettazione e Test (Acceptance Criteria / BDD)

### Scenario 1: Caricamento corretto dei Frame
* **GIVEN** i file `sprite_capitano_{action}.png` in `sprites/`
* **WHEN** la classe `Capitano` viene inizializzata
* **THEN** devono essere caricate esattamente 10 sprite sheet, ciascuno con una griglia $1 \times 10$ di $100 \times 110$ px (10 frame per sheet).

### Scenario 2: Transizione Azione Idle -> Walk
* **GIVEN** il Capitano in stato `idle` senza input
* **WHEN** il giocatore preme il tasto di movimento orizzontale
* **THEN** `set_action("walk")` (o `"run"` se `run == True`) deve cambiare la texture e resettare il `time_counter`.

### Scenario 3: Sparo e Durata Timer
* **GIVEN** il Capitano a terra (`on_ground == True`)
* **WHEN** il giocatore preme il tasto di sparo
* **THEN** `is_shooting` diventa `True` e per `SHOOT_DURATION` (0.35s) l'azione corrente assume la variante `_shot`.

### Scenario 4: Salto dal Terreno
* **GIVEN** il Capitano a terra (`on_ground == True`)
* **WHEN** viene chiamato `jump()`
* **THEN** `change_y` viene impostato a `JUMP_SPEED` e `on_ground` diventa `False`.

### Scenario 5: Cambio Direzione
* **GIVEN** il Capitano che guarda a destra (`facing_right == True`)
* **WHEN** il giocatore preme il tasto di movimento a sinistra
* **THEN** `set_facing(False)` deve impostare `scale_x = -1`.

### Scenario 6: Blocco ai Bordi dello Schermo
* **GIVEN** il Capitano in movimento verso un bordo dello schermo
* **WHEN** `self.player.left < 0` o `self.player.right > WINDOW_WIDTH`
* **THEN** la posizione deve essere bloccata rispettivamente a `left = 0` o `right = WINDOW_WIDTH`.

---

## 5. Tracciabilità (Traceability Matrix)

| Requisito ID | Componente | Test Associato | Stato |
| :--- | :--- | :--- | :--- |
| **REQ-01** | `_load_textures()` | `test_capitano_sheet_loading()` | Draft |
| **REQ-02** | `update()` | `test_capitano_physics_gravity()` | Draft |
| **REQ-03** | `start_shoot()`, `update()` | `test_capitano_shoot_duration()` | Draft |
| **REQ-04** | `set_facing()` | `test_capitano_facing_flip()` | Draft |
