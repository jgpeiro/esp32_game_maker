# config.py - Configuración de la Game Maker Console

# ===== Logging =====
from lib.logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = DEBUG  # Change to INFO, WARNING, ERROR, or CRITICAL in production

# ===== WiFi =====
WIFI_SSID = b"..."
WIFI_PASSWORD = b"..."
WIFI_TIMEOUT = 10  # segundos

# ===== Claude API =====
CLAUDE_API_KEY = "..."
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
CLAUDE_MAX_TOKENS = 8192

# ===== Pines SPI (LCD ST7796S) =====
SPI_ID = 2
SPI_BAUDRATE = 20_000_000  # 20MHz max for ST7796S
SPI_SCK = 14
SPI_MOSI = 13
SPI_MISO = None

LCD_CS = 15
LCD_DC = 21
LCD_RST = 22
LCD_BL = 23

# ===== Pines I2C (Touch FT6x36) =====
I2C_ID = 1
I2C_FREQ = 400_000
I2C_SDA = 18
I2C_SCL = 19

# ===== Touch Calibración (Modo Vertical) =====
TOUCH_SWAP_XY = False  # En modo vertical, no intercambiamos X e Y
TOUCH_AX = 0.956   # Escala X (antes era AY)
TOUCH_BX = 6.533   # Offset X (antes era BY)
TOUCH_AY = 1.000   # Escala Y (antes era AX)
TOUCH_BY = 0.000   # Offset Y (antes era BX)

# ===== Display (Modo Vertical) =====
DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 480
DISPLAY_ROTATION = 0  # 0 para modo vertical

# ===== Colores RGB565 =====
COLOR_BLACK = 0x0000
COLOR_WHITE = 0xFFFF
COLOR_BACKGROUND = 0x1082      # Azul muy oscuro
COLOR_PRIMARY = 0x07FF         # Cyan brillante
COLOR_SECONDARY = 0x4FE6       # Verde azulado
COLOR_ACCENT = 0xF986          # Rojo coral
COLOR_SUCCESS = 0x07E0         # Verde
COLOR_WARNING = 0xFD20         # Naranja
COLOR_DANGER = 0xF800          # Rojo
COLOR_TEXT = 0xFFFF            # Blanco
COLOR_TEXT_SECONDARY = 0x8410  # Gris
COLOR_BUTTON_BG = 0x2945       # Azul oscuro
COLOR_BUTTON_BORDER = 0x4A69   # Azul medio

# ===== Storage =====
GAMES_DIR = "/games"
MAX_GAMES = 20

# ===== UI Timings =====
SPLASH_DURATION = 3000  # ms
TOUCH_DEBOUNCE = 20     # ms
FRAME_RATE = 30         # FPS

# ===== Template para Claude =====
GAME_TEMPLATE = """Crea un juego MicroPython COMPLETO y VISUALMENTE ATRACTIVO para ESP32.

=== HARDWARE ===
- Display: 320x480 pixels (vertical/portrait), RGB565
- Touch: capacitivo, detecta toques simples
- ESP32: memoria limitada, optimiza para FPS alto

=== PALETA DE COLORES RGB565 (usar variedad) ===
BLACK=0x0000, WHITE=0xFFFF, RED=0xF800, GREEN=0x07E0, BLUE=0x001F
CYAN=0x07FF, MAGENTA=0xF81F, YELLOW=0xFFE0, ORANGE=0xFD20
PINK=0xFE19, PURPLE=0x8010, LIME=0x87E0, SKYBLUE=0x867D
DARKGRAY=0x4208, LIGHTGRAY=0xC618, GOLD=0xFEA0, BROWN=0x8200

=== API DEL RENDERER (usa todas) ===
r = self.renderer
r.fill(color)                              # Rellenar pantalla (fondo con color, no solo negro!)
r.rect(x, y, w, h, color, fill=True/False) # Rectangulos
r.circle(cx, cy, radius, color, fill=True/False)  # Circulos
r.ellipse(cx, cy, rx, ry, color, fill=True/False)  # Elipses
r.rounded_rect(x, y, w, h, radius, color, fill=True/False)  # Rectangulos redondeados (botones, UI)
r.triangle(x0, y0, x1, y1, x2, y2, color, fill=True/False)  # Triangulos (naves, flechas)
r.line(x0, y0, x1, y1, color)              # Lineas
r.hline(x, y, width, color)                # Linea horizontal (rapida)
r.vline(x, y, height, color)               # Linea vertical (rapida)
r.pixel(x, y, color)                       # Pixel individual
r.text(x, y, "texto", color, scale=1/2/3)  # Texto con escala
r.text_centered(y, "texto", color, scale=1/2/3)  # Texto centrado horizontalmente
r.progress_bar(x, y, w, h, progress, bg_color, fg_color)  # Barra de progreso (0.0-1.0)
r.flush()  # SIEMPRE al final de draw()

=== ESTRUCTURA OBLIGATORIA ===
class Game:
    def __init__(self, renderer, touch):
        self.renderer = renderer
        self.touch = touch
        self.frame = 0  # Contador para animaciones
        
        # === ESTADO DEL JUEGO ===
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.level = 1
        
        # === OBJETOS DEL JUEGO (minimo 5-10 elementos) ===
        self.player = {{"x": 160, "y": 400, "w": 40, "h": 40, "color": 0xFE19, "speed": 8}}
        self.enemies = []
        self.projectiles = []
        self.items = []
        self.particles = []  # Para efectos visuales
        
        # Inicializar enemigos/elementos
        self._spawn_initial_objects()
    
    def _spawn_initial_objects(self):
        # Crear 5-10 objetos iniciales con propiedades variadas
        pass
    
    def update(self):
        if self.game_over:
            return
        
        self.frame += 1
        
        # Leer touch
        touched, x, y = self.touch.read()
        if touched:
            self.handle_touch(x, y)
        
        # === ACTUALIZAR TODOS LOS OBJETOS ===
        self._update_player()
        self._update_enemies()
        self._update_projectiles()
        self._update_items()
        self._update_particles()
        
        # === DETECTAR COLISIONES ===
        self._check_collisions()
        
        # === SPAWN NUEVOS ELEMENTOS ===
        if self.frame % 60 == 0:  # Cada ~2 segundos
            self._spawn_enemy()
    
    def _update_player(self):
        pass
    
    def _update_enemies(self):
        # Mover enemigos, usar self.frame para animaciones
        # Ejemplo: enemy["y"] += enemy["speed"]
        pass
    
    def _update_projectiles(self):
        pass
    
    def _update_items(self):
        pass
    
    def _update_particles(self):
        # Actualizar particulas, remover las que expiran
        pass
    
    def _check_collisions(self):
        # Colision rectangulo: if abs(a.x-b.x) < (a.w+b.w)/2 and abs(a.y-b.y) < (a.h+b.h)/2
        pass
    
    def _spawn_enemy(self):
        pass
    
    def _add_particle(self, x, y, color):
        # Agregar efecto visual
        if len(self.particles) < 20:
            self.particles.append({{"x": x, "y": y, "life": 15, "color": color}})
    
    def draw(self):
        r = self.renderer
        
        # === FONDO CON COLOR (no negro!) ===
        r.fill(0x1082)  # Azul oscuro, o gradiente simulado
        
        # === DECORACIONES DE FONDO (estrellas, nubes, etc) ===
        for i in range(10):
            x = (i * 37 + self.frame) % 320
            y = (i * 51) % 400
            r.pixel(x, y, 0xFFFF)
        
        # === DIBUJAR TODOS LOS OBJETOS ===
        self._draw_items()
        self._draw_projectiles()
        self._draw_enemies()
        self._draw_player()
        self._draw_particles()
        
        # === HUD (siempre visible, arriba) ===
        r.rect(0, 0, 320, 35, 0x0000, fill=True)
        r.text(10, 10, f"Score: {{self.score}}", 0xFFE0, scale=2)
        r.text(200, 10, f"Vidas: {{self.lives}}", 0xF800, scale=2)
        r.progress_bar(10, 28, 100, 6, self.lives/3, 0x4208, 0x07E0)
        
        # === GAME OVER ===
        if self.game_over:
            r.rect(40, 180, 240, 120, 0x0000, fill=True)
            r.rect(40, 180, 240, 120, 0xF800, fill=False)
            r.text_centered(210, "GAME OVER", 0xF800, scale=3)
            r.text_centered(260, f"Score: {{self.score}}", 0xFFFF, scale=2)
        
        r.flush()
    
    def _draw_player(self):
        p = self.player
        r = self.renderer
        # Dibujar jugador con multiples formas y colores
        r.rounded_rect(p["x"]-p["w"]//2, p["y"]-p["h"]//2, p["w"], p["h"], 8, p["color"], fill=True)
        # Detalles adicionales (ojos, sombra, etc)
    
    def _draw_enemies(self):
        for e in self.enemies:
            # Cada enemigo con forma unica, animacion basada en self.frame
            pass
    
    def _draw_projectiles(self):
        for p in self.projectiles:
            self.renderer.circle(p["x"], p["y"], 4, 0xFFE0, fill=True)
    
    def _draw_items(self):
        for item in self.items:
            # Dibujar items coleccionables con animacion de pulso
            scale = 1.0 + 0.2 * ((self.frame % 20) / 20)  # Efecto pulso
            pass
    
    def _draw_particles(self):
        for p in self.particles:
            alpha = p["life"] / 15
            self.renderer.circle(int(p["x"]), int(p["y"]), int(3 * alpha), p["color"], fill=True)
    
    def handle_touch(self, x, y):
        if self.game_over:
            # Reiniciar juego al tocar
            self.__init__(self.renderer, self.touch)
            return
        
        # Mover jugador hacia el toque o disparar
        pass

=== REQUISITOS OBLIGATORIOS ===
1. MINIMO 5 tipos de objetos diferentes en pantalla
2. COLORES VARIADOS (minimo 6 colores distintos)
3. ANIMACIONES usando self.frame (movimiento, pulso, parpadeo)
4. SISTEMA DE PUNTUACION visible en HUD
5. VIDAS o energia con barra de progreso
6. PARTICULAS para efectos (explosiones, estelas)
7. FONDO con color y decoraciones (no negro plano)
8. GAME OVER con opcion de reiniciar
9. COLISIONES funcionales entre objetos
10. SPAWN dinamico de enemigos/items

=== OPTIMIZACIONES PARA FPS ===
- Limitar listas a maximo 20-30 elementos (usar len() < max)
- Usar diccionarios simples para objetos, no clases
- Calculos simples: evitar sqrt(), usar comparacion de cuadrados
- Remover objetos fuera de pantalla: if y > 500: lista.remove(obj)
- Evitar crear strings en cada frame (precalcular textos fijos)

=== PROHIBIDO ===
- NO imports externos (solo lo que esta disponible)
- NO threading, NO async
- NO time.sleep() (bloquea el render)
- NO variables globales fuera de la clase
- Coordenadas: x en 0-319, y en 0-479

Descripcion del juego: {description}

Genera un juego COMPLETO, COLORIDO y DIVERTIDO. Responde SOLO con el codigo Python."""

# ===== Prompts para Claude =====
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

# ===== Debug =====
DEBUG = True
