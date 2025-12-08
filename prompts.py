# prompts.py - Prompts y templates para la generación de juegos y aplicaciones

# ===== Template para Claude (Juegos) =====
GAME_TEMPLATE = """Crea un juego MicroPython PROFESIONAL y COMPLETO para ESP32 con arquitectura robusta.

=== HARDWARE ===
- Display: 320x480 pixels (vertical/portrait), RGB565
- Touch: capacitivo, detecta toques simples
- ESP32: memoria limitada, optimiza para FPS alto

=== PALETA DE COLORES RGB565 ===
BLACK=0x0000, WHITE=0xFFFF, RED=0xF800, GREEN=0x07E0, BLUE=0x001F
CYAN=0x07FF, MAGENTA=0xF81F, YELLOW=0xFFE0, ORANGE=0xFD20
PINK=0xFE19, PURPLE=0x8010, LIME=0x87E0, SKYBLUE=0x867D
DARKGRAY=0x4208, LIGHTGRAY=0xC618, GOLD=0xFEA0, BROWN=0x8200
NAVY=0x0010, DARKGREEN=0x0320, MAROON=0x8000, OLIVE=0x8400, TEAL=0x0410

=== API DEL RENDERER ===
r.fill(color)
r.rect(x, y, w, h, color, fill=True/False)
r.circle(cx, cy, radius, color, fill=True/False)
r.ellipse(cx, cy, rx, ry, color, fill=True/False)
r.rounded_rect(x, y, w, h, radius, color, fill=True/False)
r.triangle(x0, y0, x1, y1, x2, y2, color, fill=True/False)
r.line(x0, y0, x1, y1, color)
r.hline(x, y, width, color)
r.vline(x, y, height, color)
r.pixel(x, y, color)
r.text(x, y, "texto", color, scale=1/2/3)
r.text_centered(y, "texto", color, scale=1/2/3)
r.progress_bar(x, y, w, h, progress, bg_color, fg_color)
r.flush()  # SIEMPRE al final de draw()

=== ARQUITECTURA OBLIGATORIA CON CLASES ===

# ============================================
# CLASE: GameState - Maquina de estados
# ============================================
class GameState:
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    LEVEL_COMPLETE = 4

# ============================================
# CLASE: Colors - Paleta del juego
# ============================================
class Colors:
    # Define aqui los colores tematicos del juego
    BG_PRIMARY = 0x1082
    BG_SECONDARY = 0x0841
    ACCENT = 0x07FF
    TEXT = 0xFFFF
    TEXT_DIM = 0x8410
    PLAYER = 0xFE19
    ENEMY = 0xF800
    ITEM = 0xFFE0
    PARTICLE = 0x07E0
    UI_BG = 0x2104
    UI_BORDER = 0x4A69
    BUTTON = 0x3186
    BUTTON_HIGHLIGHT = 0x4A69

# ============================================
# CLASE: Entity - Clase base para entidades
# ============================================
class Entity:
    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.active = True
        self.vx = 0
        self.vy = 0
    
    def update(self, frame):
        self.x += self.vx
        self.y += self.vy
    
    def draw(self, r, frame):
        r.rect(int(self.x - self.w//2), int(self.y - self.h//2), 
               self.w, self.h, self.color, fill=True)
    
    def collides_with(self, other):
        return (abs(self.x - other.x) < (self.w + other.w) / 2 and
                abs(self.y - other.y) < (self.h + other.h) / 2)
    
    def is_on_screen(self):
        return -50 < self.x < 370 and -50 < self.y < 530

# ============================================
# CLASE: Player - Jugador controlable
# ============================================
class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40, Colors.PLAYER)
        self.speed = 8
        self.max_health = 100
        self.health = self.max_health
        self.invincible_frames = 0
        self.power_level = 1
        self.target_x = x
        self.target_y = y
    
    def update(self, frame):
        # Movimiento suave hacia el objetivo
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist_sq = dx*dx + dy*dy
        if dist_sq > 16:
            factor = self.speed / (dist_sq ** 0.5) if dist_sq > 0 else 0
            self.x += dx * min(factor, 1)
            self.y += dy * min(factor, 1)
        
        # Mantener en pantalla
        self.x = max(self.w//2, min(320 - self.w//2, self.x))
        self.y = max(60, min(460, self.y))
        
        # Reducir invencibilidad
        if self.invincible_frames > 0:
            self.invincible_frames -= 1
    
    def take_damage(self, amount):
        if self.invincible_frames <= 0:
            self.health -= amount
            self.invincible_frames = 60  # 2 segundos de invencibilidad
            return True
        return False
    
    def draw(self, r, frame):
        # Parpadeo cuando invencible
        if self.invincible_frames > 0 and frame % 6 < 3:
            return
        
        x, y = int(self.x), int(self.y)
        # Cuerpo principal
        r.rounded_rect(x - self.w//2, y - self.h//2, self.w, self.h, 8, self.color, fill=True)
        # Detalles (ojos, etc) - personaliza segun el juego
        r.circle(x - 8, y - 5, 5, Colors.TEXT, fill=True)
        r.circle(x + 8, y - 5, 5, Colors.TEXT, fill=True)
        r.circle(x - 8, y - 5, 2, Colors.BG_PRIMARY, fill=True)
        r.circle(x + 8, y - 5, 2, Colors.BG_PRIMARY, fill=True)

# ============================================
# CLASE: Enemy - Enemigos con comportamiento
# ============================================
class Enemy(Entity):
    TYPE_BASIC = 0
    TYPE_FAST = 1
    TYPE_TANK = 2
    TYPE_SHOOTER = 3
    
    def __init__(self, x, y, enemy_type=0):
        sizes = {{0: (30, 30), 1: (24, 24), 2: (45, 45), 3: (35, 35)}}
        colors = {{0: 0xF800, 1: 0xFD20, 2: 0x8000, 3: 0xF81F}}
        speeds = {{0: 2, 1: 4, 2: 1, 3: 1.5}}
        healths = {{0: 1, 1: 1, 2: 3, 3: 2}}
        points = {{0: 10, 1: 15, 2: 30, 3: 25}}
        
        w, h = sizes.get(enemy_type, (30, 30))
        super().__init__(x, y, w, h, colors.get(enemy_type, 0xF800))
        
        self.enemy_type = enemy_type
        self.vy = speeds.get(enemy_type, 2)
        self.health = healths.get(enemy_type, 1)
        self.points = points.get(enemy_type, 10)
        self.shoot_cooldown = 0
    
    def update(self, frame):
        super().update(frame)
        
        # Movimiento segun tipo
        if self.enemy_type == Enemy.TYPE_FAST:
            self.vx = 2 * ((frame // 30) % 2 * 2 - 1)  # Zigzag
        elif self.enemy_type == Enemy.TYPE_SHOOTER:
            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= 1
        
        # Desactivar si sale de pantalla
        if self.y > 530:
            self.active = False
    
    def draw(self, r, frame):
        x, y = int(self.x), int(self.y)
        
        if self.enemy_type == Enemy.TYPE_BASIC:
            r.rect(x - self.w//2, y - self.h//2, self.w, self.h, self.color, fill=True)
            r.circle(x - 6, y - 4, 4, 0xFFFF, fill=True)
            r.circle(x + 6, y - 4, 4, 0xFFFF, fill=True)
        elif self.enemy_type == Enemy.TYPE_FAST:
            r.triangle(x, y - self.h//2, x - self.w//2, y + self.h//2, 
                      x + self.w//2, y + self.h//2, self.color, fill=True)
        elif self.enemy_type == Enemy.TYPE_TANK:
            r.rounded_rect(x - self.w//2, y - self.h//2, self.w, self.h, 5, self.color, fill=True)
            r.rect(x - self.w//2 + 5, y - self.h//2 + 5, self.w - 10, self.h - 10, 0x4000, fill=True)
        elif self.enemy_type == Enemy.TYPE_SHOOTER:
            r.circle(x, y, self.w//2, self.color, fill=True)
            # Indicador de disparo
            if self.shoot_cooldown < 15:
                r.circle(x, y + self.h//2 + 5, 3, 0xFFE0, fill=True)

# ============================================
# CLASE: Projectile - Proyectiles
# ============================================
class Projectile(Entity):
    def __init__(self, x, y, vy, color, damage=1, is_player=True):
        super().__init__(x, y, 8, 12, color)
        self.vy = vy
        self.damage = damage
        self.is_player = is_player
    
    def update(self, frame):
        super().update(frame)
        if not self.is_on_screen():
            self.active = False
    
    def draw(self, r, frame):
        x, y = int(self.x), int(self.y)
        r.ellipse(x, y, 4, 6, self.color, fill=True)
        # Estela
        r.ellipse(x, y + 8 * (1 if self.vy > 0 else -1), 2, 4, 
                 self.color & 0x7BEF, fill=True)

# ============================================
# CLASE: Particle - Efectos visuales
# ============================================
class Particle(Entity):
    def __init__(self, x, y, color, life=20):
        super().__init__(x, y, 4, 4, color)
        self.life = life
        self.max_life = life
        import random
        self.vx = random.randint(-3, 3)
        self.vy = random.randint(-3, 3)
    
    def update(self, frame):
        super().update(frame)
        self.life -= 1
        if self.life <= 0:
            self.active = False
        # Friccion
        self.vx *= 0.9
        self.vy *= 0.9
    
    def draw(self, r, frame):
        alpha = self.life / self.max_life
        size = max(1, int(4 * alpha))
        r.circle(int(self.x), int(self.y), size, self.color, fill=True)

# ============================================
# CLASE: Item - Coleccionables y power-ups
# ============================================
class Item(Entity):
    TYPE_COIN = 0
    TYPE_HEALTH = 1
    TYPE_POWER = 2
    TYPE_SHIELD = 3
    
    def __init__(self, x, y, item_type=0):
        colors = {{0: 0xFEA0, 1: 0x07E0, 2: 0x07FF, 3: 0xF81F}}
        super().__init__(x, y, 20, 20, colors.get(item_type, 0xFEA0))
        self.item_type = item_type
        self.vy = 1.5
    
    def update(self, frame):
        super().update(frame)
        if self.y > 520:
            self.active = False
    
    def draw(self, r, frame):
        x, y = int(self.x), int(self.y)
        # Animacion de pulso
        pulse = 1 + 0.2 * ((frame % 20) / 20)
        size = int(self.w * pulse / 2)
        
        if self.item_type == Item.TYPE_COIN:
            r.circle(x, y, size, self.color, fill=True)
            r.text(x - 4, y - 4, "$", Colors.BG_PRIMARY, scale=1)
        elif self.item_type == Item.TYPE_HEALTH:
            r.circle(x, y, size, self.color, fill=True)
            r.text(x - 4, y - 4, "+", 0xFFFF, scale=1)
        elif self.item_type == Item.TYPE_POWER:
            r.triangle(x, y - size, x - size, y + size//2, x + size, y + size//2, 
                      self.color, fill=True)
        elif self.item_type == Item.TYPE_SHIELD:
            r.circle(x, y, size, self.color, fill=False)
            r.circle(x, y, size - 3, self.color, fill=True)

# ============================================
# CLASE: Button - Botones para UI
# ============================================
class Button:
    def __init__(self, x, y, w, h, text, color=Colors.BUTTON, text_color=Colors.TEXT):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.color = color
        self.text_color = text_color
        self.pressed = False
    
    def draw(self, r, frame):
        color = Colors.BUTTON_HIGHLIGHT if self.pressed else self.color
        r.rounded_rect(self.x, self.y, self.w, self.h, 10, color, fill=True)
        r.rounded_rect(self.x, self.y, self.w, self.h, 10, Colors.UI_BORDER, fill=False)
        
        # Centrar texto
        text_x = self.x + (self.w - len(self.text) * 8) // 2
        text_y = self.y + (self.h - 8) // 2
        r.text(text_x, text_y, self.text, self.text_color, scale=1)
    
    def is_touched(self, tx, ty):
        return (self.x <= tx <= self.x + self.w and 
                self.y <= ty <= self.y + self.h)

# ============================================
# CLASE: HUD - Interfaz de usuario en juego
# ============================================
class HUD:
    def __init__(self):
        self.score_text = "Score: 0"
        self.level_text = "Nivel 1"
    
    def update(self, score, level, player_health, max_health):
        self.score_text = f"Score: {{score}}"
        self.level_text = f"Nivel {{level}}"
        self.health_ratio = player_health / max_health
    
    def draw(self, r, frame):
        # Fondo del HUD
        r.rect(0, 0, 320, 50, Colors.UI_BG, fill=True)
        r.hline(0, 50, 320, Colors.UI_BORDER)
        
        # Score
        r.text(10, 8, self.score_text, Colors.ACCENT, scale=2)
        
        # Nivel
        r.text(220, 8, self.level_text, Colors.TEXT_DIM, scale=1)
        
        # Barra de vida
        r.text(10, 32, "HP", Colors.TEXT_DIM, scale=1)
        r.progress_bar(35, 32, 120, 12, self.health_ratio, Colors.BG_SECONDARY, 0x07E0)
        
        # Decoracion
        r.circle(300, 25, 15, Colors.ACCENT, fill=False)

# ============================================
# CLASE: MenuScreen - Pantalla de menu
# ============================================
class MenuScreen:
    def __init__(self, game_title, instructions):
        self.title = game_title
        self.instructions = instructions
        self.btn_start = Button(60, 320, 200, 50, "JUGAR")
        self.btn_info = Button(110, 390, 100, 40, "Info")
        self.show_info = False
    
    def update(self, touched, tx, ty, frame):
        if touched:
            if self.show_info:
                self.show_info = False
                return None
            elif self.btn_start.is_touched(tx, ty):
                return GameState.PLAYING
            elif self.btn_info.is_touched(tx, ty):
                self.show_info = True
        return None
    
    def draw(self, r, frame):
        # Fondo animado
        r.fill(Colors.BG_PRIMARY)
        
        # Estrellas/particulas de fondo
        for i in range(15):
            x = (i * 23 + frame) % 320
            y = (i * 37 + frame // 2) % 480
            r.pixel(x, y, Colors.TEXT_DIM)
        
        # Titulo con sombra
        r.text_centered(82, self.title, Colors.BG_SECONDARY, scale=3)
        r.text_centered(80, self.title, Colors.ACCENT, scale=3)
        
        # Subtitulo
        r.text_centered(130, "ESP32 Game", Colors.TEXT_DIM, scale=1)
        
        # Decoracion
        r.rounded_rect(40, 160, 240, 140, 15, Colors.UI_BG, fill=True)
        r.rounded_rect(40, 160, 240, 140, 15, Colors.UI_BORDER, fill=False)
        
        # Instrucciones resumidas
        y = 175
        for line in self.instructions[:4]:
            r.text(55, y, line[:28], Colors.TEXT, scale=1)
            y += 20
        
        # Animacion del titulo
        pulse = (frame % 60) / 60
        r.circle(160, 260, int(5 + 3 * pulse), Colors.ACCENT, fill=True)
        
        # Botones
        self.btn_start.draw(r, frame)
        self.btn_info.draw(r, frame)
        
        # Panel de info
        if self.show_info:
            r.rect(20, 100, 280, 280, Colors.BG_PRIMARY, fill=True)
            r.rect(20, 100, 280, 280, Colors.ACCENT, fill=False)
            r.text_centered(120, "INSTRUCCIONES", Colors.ACCENT, scale=2)
            y = 160
            for line in self.instructions:
                r.text(35, y, line[:32], Colors.TEXT, scale=1)
                y += 22
            r.text_centered(360, "Toca para cerrar", Colors.TEXT_DIM, scale=1)
        
        r.flush()

# ============================================
# CLASE: PauseScreen - Pantalla de pausa
# ============================================
class PauseScreen:
    def __init__(self):
        self.btn_resume = Button(60, 200, 200, 50, "CONTINUAR")
        self.btn_menu = Button(60, 270, 200, 50, "MENU")
    
    def update(self, touched, tx, ty, frame):
        if touched:
            if self.btn_resume.is_touched(tx, ty):
                return GameState.PLAYING
            elif self.btn_menu.is_touched(tx, ty):
                return GameState.MENU
        return None
    
    def draw(self, r, frame):
        # Overlay semi-transparente simulado
        r.rect(0, 0, 320, 480, Colors.BG_PRIMARY, fill=True)
        
        r.text_centered(120, "PAUSA", Colors.ACCENT, scale=3)
        
        self.btn_resume.draw(r, frame)
        self.btn_menu.draw(r, frame)
        
        r.text_centered(400, "Toca esquina superior", Colors.TEXT_DIM, scale=1)
        r.text_centered(420, "derecha para pausar", Colors.TEXT_DIM, scale=1)
        
        r.flush()

# ============================================
# CLASE: GameOverScreen - Pantalla de fin
# ============================================
class GameOverScreen:
    def __init__(self):
        self.final_score = 0
        self.high_score = 0
        self.btn_retry = Button(60, 280, 200, 50, "REINTENTAR")
        self.btn_menu = Button(60, 350, 200, 50, "MENU")
    
    def set_score(self, score, high_score):
        self.final_score = score
        self.high_score = high_score
    
    def update(self, touched, tx, ty, frame):
        if touched:
            if self.btn_retry.is_touched(tx, ty):
                return "RETRY"
            elif self.btn_menu.is_touched(tx, ty):
                return GameState.MENU
        return None
    
    def draw(self, r, frame):
        r.fill(Colors.BG_PRIMARY)
        
        # Particulas tristes
        for i in range(8):
            x = 160 + int(80 * ((i * 0.785) % 1 - 0.5) * 2)
            y = 60 + (frame + i * 20) % 100
            r.circle(x, y, 2, Colors.TEXT_DIM, fill=True)
        
        r.text_centered(100, "GAME OVER", 0xF800, scale=3)
        
        # Score
        r.rounded_rect(50, 160, 220, 100, 10, Colors.UI_BG, fill=True)
        r.text_centered(180, f"Score: {{self.final_score}}", Colors.ACCENT, scale=2)
        r.text_centered(220, f"Record: {{self.high_score}}", Colors.TEXT_DIM, scale=1)
        
        if self.final_score >= self.high_score and self.final_score > 0:
            r.text_centered(250, "NUEVO RECORD!", Colors.ITEM, scale=1)
        
        self.btn_retry.draw(r, frame)
        self.btn_menu.draw(r, frame)
        
        r.flush()

# ============================================
# CLASE: LevelCompleteScreen - Nivel completado
# ============================================
class LevelCompleteScreen:
    def __init__(self):
        self.level = 1
        self.score = 0
        self.btn_next = Button(60, 320, 200, 50, "SIGUIENTE")
    
    def set_data(self, level, score):
        self.level = level
        self.score = score
    
    def update(self, touched, tx, ty, frame):
        if touched and self.btn_next.is_touched(tx, ty):
            return "NEXT_LEVEL"
        return None
    
    def draw(self, r, frame):
        r.fill(Colors.BG_PRIMARY)
        
        # Celebracion
        for i in range(12):
            angle = (frame * 3 + i * 30) % 360
            x = 160 + int(60 * ((angle % 180) / 180 - 0.5) * 2)
            y = 150 + int(40 * ((angle % 90) / 90))
            colors = [0xFEA0, 0x07FF, 0xFE19, 0x07E0]
            r.circle(x, y, 4, colors[i % 4], fill=True)
        
        r.text_centered(100, "NIVEL", Colors.ACCENT, scale=2)
        r.text_centered(140, "COMPLETADO!", Colors.ACCENT, scale=2)
        
        r.rounded_rect(60, 200, 200, 80, 10, Colors.UI_BG, fill=True)
        r.text_centered(220, f"Nivel {{self.level}}", Colors.TEXT, scale=2)
        r.text_centered(255, f"Score: {{self.score}}", Colors.ITEM, scale=1)
        
        self.btn_next.draw(r, frame)
        
        r.flush()

# ============================================
# CLASE PRINCIPAL: Game
# ============================================
class Game:
    # Informacion del juego (PERSONALIZAR)
    TITLE = "NOMBRE DEL JUEGO"  # Titulo del juego
    INSTRUCTIONS = [
        "Toca para mover",
        "Esquiva enemigos",
        "Recoge items",
        "Sobrevive!"
    ]
    
    def __init__(self, renderer, touch):
        self.renderer = renderer
        self.touch = touch
        self.frame = 0
        
        # Sistema de estados
        self.state = GameState.MENU
        
        # Pantallas
        self.menu_screen = MenuScreen(self.TITLE, self.INSTRUCTIONS)
        self.pause_screen = PauseScreen()
        self.game_over_screen = GameOverScreen()
        self.level_complete_screen = LevelCompleteScreen()
        self.hud = HUD()
        
        # Estado del juego
        self.score = 0
        self.high_score = 0
        self.level = 1
        
        # Entidades
        self.player = None
        self.enemies = []
        self.projectiles = []
        self.items = []
        self.particles = []
        
        # Spawn timers
        self.enemy_spawn_timer = 0
        self.item_spawn_timer = 0
    
    def _start_game(self):
        '''Inicializa o reinicia el juego'''
        self.score = 0
        self.level = 1
        self.player = Player(160, 400)
        self.enemies = []
        self.projectiles = []
        self.items = []
        self.particles = []
        self.enemy_spawn_timer = 0
        self.item_spawn_timer = 0
        self._spawn_initial_enemies()
    
    def _next_level(self):
        '''Avanza al siguiente nivel'''
        self.level += 1
        self.enemies = []
        self.projectiles = []
        self.items = []
        self.player.health = min(self.player.health + 30, self.player.max_health)
        self._spawn_initial_enemies()
    
    def _spawn_initial_enemies(self):
        '''Genera enemigos iniciales segun el nivel'''
        import random
        for i in range(3 + self.level):
            x = random.randint(30, 290)
            y = random.randint(-200, -50)
            enemy_type = random.randint(0, min(self.level, 3))
            self.enemies.append(Enemy(x, y, enemy_type))
    
    def _spawn_enemy(self):
        '''Genera un nuevo enemigo'''
        if len(self.enemies) < 10 + self.level * 2:
            import random
            x = random.randint(30, 290)
            enemy_type = random.randint(0, min(self.level, 3))
            self.enemies.append(Enemy(x, -40, enemy_type))
    
    def _spawn_item(self):
        '''Genera un item'''
        if len(self.items) < 5:
            import random
            x = random.randint(30, 290)
            item_type = random.choices([0, 1, 2, 3], weights=[60, 20, 15, 5])[0]
            self.items.append(Item(x, -30, item_type))
    
    def _create_explosion(self, x, y, color, count=8):
        '''Crea efecto de explosion'''
        for _ in range(min(count, 20 - len(self.particles))):
            self.particles.append(Particle(x, y, color, 15))
    
    def _check_collisions(self):
        '''Verifica colisiones entre entidades'''
        # Proyectiles del jugador vs enemigos
        for proj in self.projectiles:
            if not proj.active or not proj.is_player:
                continue
            for enemy in self.enemies:
                if not enemy.active:
                    continue
                if proj.collides_with(enemy):
                    proj.active = False
                    enemy.health -= proj.damage
                    if enemy.health <= 0:
                        enemy.active = False
                        self.score += enemy.points
                        self._create_explosion(enemy.x, enemy.y, enemy.color)
                    break
        
        # Enemigos vs jugador
        for enemy in self.enemies:
            if not enemy.active:
                continue
            if self.player.collides_with(enemy):
                if self.player.take_damage(20):
                    self._create_explosion(self.player.x, self.player.y, 0xF800, 5)
                    if self.player.health <= 0:
                        self.state = GameState.GAME_OVER
                        if self.score > self.high_score:
                            self.high_score = self.score
                        self.game_over_screen.set_score(self.score, self.high_score)
        
        # Items vs jugador
        for item in self.items:
            if not item.active:
                continue
            if self.player.collides_with(item):
                item.active = False
                self._create_explosion(item.x, item.y, item.color, 4)
                if item.item_type == Item.TYPE_COIN:
                    self.score += 25
                elif item.item_type == Item.TYPE_HEALTH:
                    self.player.health = min(self.player.health + 20, self.player.max_health)
                elif item.item_type == Item.TYPE_POWER:
                    self.player.power_level = min(self.player.power_level + 1, 3)
                elif item.item_type == Item.TYPE_SHIELD:
                    self.player.invincible_frames = 180
    
    def _player_shoot(self):
        '''El jugador dispara'''
        if len(self.projectiles) < 20:
            self.projectiles.append(
                Projectile(self.player.x, self.player.y - 25, -10, Colors.ACCENT, 
                          self.player.power_level, True)
            )
            # Disparo multiple segun power level
            if self.player.power_level >= 2:
                self.projectiles.append(
                    Projectile(self.player.x - 15, self.player.y - 20, -10, Colors.ACCENT, 1, True)
                )
                self.projectiles.append(
                    Projectile(self.player.x + 15, self.player.y - 20, -10, Colors.ACCENT, 1, True)
                )
    
    def _clean_inactive(self):
        '''Elimina entidades inactivas'''
        self.enemies = [e for e in self.enemies if e.active]
        self.projectiles = [p for p in self.projectiles if p.active]
        self.items = [i for i in self.items if i.active]
        self.particles = [p for p in self.particles if p.active]
    
    def update(self):
        '''Actualiza el juego segun el estado actual'''
        self.frame += 1
        touched, tx, ty = self.touch.read()
        
        if self.state == GameState.MENU:
            result = self.menu_screen.update(touched, tx, ty, self.frame)
            if result == GameState.PLAYING:
                self._start_game()
                self.state = GameState.PLAYING
        
        elif self.state == GameState.PLAYING:
            # Verificar pausa (esquina superior derecha)
            if touched and tx > 280 and ty < 50:
                self.state = GameState.PAUSED
                return
            
            # Input del jugador
            if touched:
                self.player.target_x = tx
                self.player.target_y = max(60, ty)
            
            # Disparo automatico
            if self.frame % 10 == 0:
                self._player_shoot()
            
            # Actualizar entidades
            self.player.update(self.frame)
            
            for enemy in self.enemies:
                enemy.update(self.frame)
            
            for proj in self.projectiles:
                proj.update(self.frame)
            
            for item in self.items:
                item.update(self.frame)
            
            for particle in self.particles:
                particle.update(self.frame)
            
            # Spawn
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= max(30, 90 - self.level * 10):
                self._spawn_enemy()
                self.enemy_spawn_timer = 0
            
            self.item_spawn_timer += 1
            if self.item_spawn_timer >= 150:
                self._spawn_item()
                self.item_spawn_timer = 0
            
            # Colisiones
            self._check_collisions()
            
            # Limpiar
            self._clean_inactive()
            
            # Actualizar HUD
            self.hud.update(self.score, self.level, self.player.health, self.player.max_health)
            
            # Verificar nivel completado (ejemplo: cada 500 puntos)
            if self.score >= self.level * 500:
                self.level_complete_screen.set_data(self.level, self.score)
                self.state = GameState.LEVEL_COMPLETE
        
        elif self.state == GameState.PAUSED:
            result = self.pause_screen.update(touched, tx, ty, self.frame)
            if result == GameState.PLAYING:
                self.state = GameState.PLAYING
            elif result == GameState.MENU:
                self.state = GameState.MENU
        
        elif self.state == GameState.GAME_OVER:
            result = self.game_over_screen.update(touched, tx, ty, self.frame)
            if result == "RETRY":
                self._start_game()
                self.state = GameState.PLAYING
            elif result == GameState.MENU:
                self.state = GameState.MENU
        
        elif self.state == GameState.LEVEL_COMPLETE:
            result = self.level_complete_screen.update(touched, tx, ty, self.frame)
            if result == "NEXT_LEVEL":
                self._next_level()
                self.state = GameState.PLAYING
    
    def draw(self):
        '''Dibuja el juego segun el estado actual'''
        r = self.renderer
        
        if self.state == GameState.MENU:
            self.menu_screen.draw(r, self.frame)
        
        elif self.state == GameState.PLAYING:
            # Fondo
            r.fill(Colors.BG_PRIMARY)
            
            # Fondo decorativo
            for i in range(20):
                x = (i * 17 + self.frame // 3) % 320
                y = (i * 31 + self.frame // 2) % 480
                r.pixel(x, y, Colors.TEXT_DIM)
            
            # Entidades (orden de dibujado: fondo a frente)
            for item in self.items:
                item.draw(r, self.frame)
            
            for proj in self.projectiles:
                proj.draw(r, self.frame)
            
            for enemy in self.enemies:
                enemy.draw(r, self.frame)
            
            self.player.draw(r, self.frame)
            
            for particle in self.particles:
                particle.draw(r, self.frame)
            
            # HUD
            self.hud.draw(r, self.frame)
            
            # Indicador de pausa
            r.rounded_rect(285, 10, 25, 25, 5, Colors.UI_BG, fill=True)
            r.rect(291, 16, 4, 13, Colors.TEXT, fill=True)
            r.rect(299, 16, 4, 13, Colors.TEXT, fill=True)
            
            r.flush()
        
        elif self.state == GameState.PAUSED:
            self.pause_screen.draw(r, self.frame)
        
        elif self.state == GameState.GAME_OVER:
            self.game_over_screen.draw(r, self.frame)
        
        elif self.state == GameState.LEVEL_COMPLETE:
            self.level_complete_screen.draw(r, self.frame)
    
    def handle_touch(self, x, y):
        '''Maneja toques (opcional, update() ya lo hace)'''
        pass

=== REQUISITOS OBLIGATORIOS ===
1. USAR TODAS LAS CLASES del template (GameState, Entity, Player, Enemy, etc.)
2. PERSONALIZAR Game.TITLE con nombre creativo del juego
3. PERSONALIZAR Game.INSTRUCTIONS con instrucciones especificas (4-6 lineas)
4. PERSONALIZAR la clase Player con apariencia unica (metodo draw)
5. CREAR AL MENOS 3 tipos de Enemy diferentes con comportamientos unicos
6. CREAR AL MENOS 2 tipos de Item diferentes
7. PERSONALIZAR Colors con paleta tematica del juego
8. IMPLEMENTAR mecanicas unicas en los metodos _spawn y _check_collisions
9. PANTALLA DE MENU funcional con instrucciones claras
10. SISTEMA DE NIVELES con dificultad progresiva

=== PERSONALIZACIONES REQUERIDAS ===
- Cambiar TITLE por nombre del juego
- Cambiar INSTRUCTIONS por instrucciones especificas
- Modificar Player.draw() para apariencia unica
- Modificar Enemy.draw() para enemigos tematicos
- Ajustar colores en clase Colors
- Implementar mecanica principal en update()

=== OPTIMIZACIONES PARA ESP32 ===
- Maximo 15 enemigos, 20 proyectiles, 10 items, 20 particulas
- Usar enteros para posiciones cuando sea posible
- Evitar crear objetos en cada frame
- Reutilizar listas, no crear nuevas

=== PROHIBIDO ===
- NO imports externos (solo random cuando sea necesario)
- NO threading, NO async
- NO time.sleep()
- NO variables globales fuera de las clases
- Coordenadas: x en 0-319, y en 0-479

Descripcion del juego: {description}

Genera un juego COMPLETO y PROFESIONAL personalizando las clases del template.
El juego debe ser UNICO y TEMATICO segun la descripcion.
Responde SOLO con el codigo Python completo."""


# ===== Template para Apps =====
APP_TEMPLATE = """Crea una aplicacion MicroPython PROFESIONAL y COMPLETA para ESP32 con arquitectura robusta.

=== HARDWARE ===
- Display: 320x480 pixels (vertical/portrait), RGB565
- Touch: capacitivo, detecta toques simples
- ESP32: memoria limitada, optimiza para buena experiencia

=== PALETA DE COLORES RGB565 ===
BLACK=0x0000, WHITE=0xFFFF, RED=0xF800, GREEN=0x07E0, BLUE=0x001F
CYAN=0x07FF, MAGENTA=0xF81F, YELLOW=0xFFE0, ORANGE=0xFD20
PINK=0xFE19, PURPLE=0x8010, LIME=0x87E0, SKYBLUE=0x867D
DARKGRAY=0x4208, LIGHTGRAY=0xC618, GOLD=0xFEA0, BROWN=0x8200
NAVY=0x0010, DARKGREEN=0x0320, MAROON=0x8000, OLIVE=0x8400, TEAL=0x0410

=== API DEL RENDERER ===
r.fill(color)
r.rect(x, y, w, h, color, fill=True/False)
r.circle(cx, cy, radius, color, fill=True/False)
r.ellipse(cx, cy, rx, ry, color, fill=True/False)
r.rounded_rect(x, y, w, h, radius, color, fill=True/False)
r.triangle(x0, y0, x1, y1, x2, y2, color, fill=True/False)
r.line(x0, y0, x1, y1, color)
r.hline(x, y, width, color)
r.vline(x, y, height, color)
r.pixel(x, y, color)
r.text(x, y, "texto", color, scale=1/2/3)
r.text_centered(y, "texto", color, scale=1/2/3)
r.progress_bar(x, y, w, h, progress, bg_color, fg_color)
r.flush()  # SIEMPRE al final de draw()

=== DESCRIPCION DE LA APLICACION ===
{description}

=== REQUISITOS ===
1. Debe ser una aplicacion util, no un juego
2. Interfaz clara y facil de usar
3. Debe responder a toques del usuario
4. Mostrar feedback visual de las acciones
5. Incluir un boton para volver al menu

=== ESTRUCTURA OBLIGATORIA ===
La aplicacion debe tener la siguiente estructura basica:

class App:
    def __init__(self):
        # Inicializa variables
        pass
    
    def update(self, frame):
        # Logica de actualizacion
        pass
    
    def draw(self, r, frame):
        # Dibuja la interfaz
        pass
    
    def on_touch(self, x, y):
        # Maneja toques
        pass

# Instancia global
app = App()

def update(frame):
    app.update(frame)

def draw(r, frame):
    app.draw(r, frame)

def on_touch(x, y):
    app.on_touch(x, y)

Responde SOLO con el codigo Python completo."""


# ===== Prompts para Sugerencias de Juegos =====
SUGGESTION_PROMPT = """Eres un disenador de videojuegos creativos para ninos.

Contexto actual: {context}

Genera 10 palabras/frases CORTAS (2-15 caracteres) que completen la descripcion del juego.
Las sugerencias deben ser:
- VARIADAS: mezcla generos, tematicas, mecanicas
- CREATIVAS: no solo lo obvio, incluye ideas originales
- VISUALES: palabras que evoquen graficos ricos (colores, animaciones, efectos)
- DIVERTIDAS: enfocadas en la jugabilidad

Ejemplos buenos: espacial, neon, pixelado, explosivo, magico, rapido, multijugador, boss, power-ups, combo

Responde SOLO las 10 palabras separadas por comas, sin numeros ni explicaciones."""


# ===== Prompts para Sugerencias de Apps (Paso inicial - tipos de apps) =====
APP_TYPE_SUGGESTION_PROMPT = """Eres un disenador de aplicaciones creativas y utiles para dispositivos portatiles ESP32 con pantalla tactil.

Genera 5 TIPOS de aplicaciones diferentes, creativos y variados.
Cada tipo debe ser una idea DISTINTA y UNICA de aplicacion.

Las sugerencias deben ser:
- MUY VARIADAS: diferentes categorias (productividad, utilidades, entretenimiento, educacion, salud, etc.)
- CREATIVAS: no solo las tipicas, incluye ideas originales e innovadoras
- PRACTICAS: aplicaciones que tengan sentido en un dispositivo portatil tactil
- CORTAS: maximo 25 caracteres cada una

Ejemplos creativos: Calculadora cientifica, Cronometro deportivo, Notas rapidas, Temporizador cocina, 
Conversor monedas, Lista compras, Dado virtual, Brujula digital, Contador de pasos, Monitor bateria,
Reloj mundial, Juego memoria, Diccionario offline, Generador passwords, Meditacion guiada,
Diario personal, Medidor ruido, Conversor unidades, Tabla periodica, Linterna morse

IMPORTANTE: Genera ideas DISTINTAS cada vez, se muy creativo.

Responde SOLO los 5 tipos separados por el caracter |, sin numeros ni explicaciones.
Ejemplo: Calculadora|Cronometro|Lista tareas|Temporizador|Conversor"""


# ===== Prompts para Sugerencias de Apps (Pasos siguientes - caracteristicas) =====
APP_FEATURE_SUGGESTION_PROMPT = """Eres un disenador de aplicaciones creativas y utiles para dispositivos portatiles.

Descripcion actual de la app: {context}

Genera 5 CARACTERISTICAS o FUNCIONALIDADES diferentes para esta aplicacion.
Cada caracteristica debe COMPLEMENTAR y MEJORAR la aplicacion descrita.

Las sugerencias deben ser:
- RELEVANTES: relacionadas con el tipo de app descrita
- UTILES: funcionalidades practicas que mejoren la experiencia
- VARIADAS: diferentes aspectos (interfaz, datos, interaccion, visualizacion)
- CREATIVAS: ideas originales que hagan la app mas interesante
- CORTAS: maximo 35 caracteres cada una

IMPORTANTE: Las caracteristicas deben ser ESPECIFICAS para esta app, no genericas.

Responde SOLO las 5 caracteristicas separadas por el caracter |, sin numeros ni explicaciones.
Ejemplo: con historial de calculos|modo cientfico|temas de colores|sonido al pulsar|exportar resultados"""


# ===== Fallbacks para cuando falla la API =====
# Múltiples listas para tener variedad cuando se piden "Nuevas"
FALLBACK_APP_TYPES_POOL = [
    # Grupo 1 - Productividad
    ["Calculadora", "Cronometro", "Temporizador", "Lista tareas", "Notas rapidas"],
    # Grupo 2 - Utilidades
    ["Conversor unidades", "Reloj mundial", "Calendario", "Alarma", "Contador"],
    # Grupo 3 - Entretenimiento
    ["Dado virtual", "Brujula", "Linterna", "Nivel burbuja", "Ruleta suerte"],
    # Grupo 4 - Salud/Bienestar
    ["Respiracion guiada", "Contador agua", "Pomodoro", "Habitos diarios", "Meditacion"],
    # Grupo 5 - Creatividad
    ["Pizarra dibujo", "Generador colores", "Patron ritmo", "Piano simple", "Pixel art"],
]

# Características por tipo de app para fallbacks inteligentes
FALLBACK_FEATURES_BY_TYPE = {
    "Calculadora": ["modo cientifico", "historial calculos", "memoria M+/M-", "temas colores", "vibracion teclas"],
    "Cronometro": ["vueltas/laps", "cuenta regresiva", "sonido alarma", "guardar tiempos", "pantalla grande"],
    "Temporizador": ["presets rapidos", "alarma sonora", "multiples timers", "modo cocina", "vibracion final"],
    "Lista tareas": ["marcar completado", "prioridades", "fechas limite", "categorias", "archivar tareas"],
    "Notas rapidas": ["guardar notas", "buscar texto", "colores notas", "ordenar fecha", "compartir nota"],
    "Conversor unidades": ["longitud/peso/temp", "monedas", "favoritos", "historial", "modo offline"],
    "Reloj mundial": ["multiples zonas", "diferencia horaria", "ciudades favoritas", "formato 12/24h", "alarmas"],
    "default": ["interfaz simple", "modo oscuro", "guardar datos", "animaciones", "boton reset"],
}

# Aplanar para compatibilidad
FALLBACK_APP_TYPES = FALLBACK_APP_TYPES_POOL[0]

FALLBACK_APP_FEATURES = [
    "con interfaz simple",
    "guarda los datos",
    "tiene modo oscuro",
    "animaciones suaves",
    "boton para reiniciar"
]

FALLBACK_GAME_SUGGESTIONS = [
    "aventura", "plataforma", "carreras", "puzzle", "arcade",
    "shooter", "estrategia", "deportes", "simulador", "retro"
]
