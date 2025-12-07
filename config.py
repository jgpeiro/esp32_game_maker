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
SPI_BAUDRATE = 20_000_000
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

# ===== Colores RGB565 (byte swapped) =====
COLOR_BLACK = 0x0000
COLOR_WHITE = 0xFFFF
COLOR_BACKGROUND = 0x8210      # Azul muy oscuro
COLOR_PRIMARY = 0xFF07         # Cyan brillante
COLOR_SECONDARY = 0xE64F       # Verde azulado
COLOR_ACCENT = 0x86F9          # Rojo coral
COLOR_SUCCESS = 0xE007         # Verde
COLOR_WARNING = 0x20FD         # Naranja
COLOR_DANGER = 0x00F8          # Rojo
COLOR_TEXT = 0xFFFF            # Blanco
COLOR_TEXT_SECONDARY = 0x1084  # Gris
COLOR_BUTTON_BG = 0x4529       # Azul oscuro
COLOR_BUTTON_BORDER = 0x694A   # Azul medio

# ===== Storage =====
GAMES_DIR = "/games"
MAX_GAMES = 20

# ===== UI Timings =====
SPLASH_DURATION = 3000  # ms
TOUCH_DEBOUNCE = 200    # ms
FRAME_RATE = 30         # FPS

# ===== Template para Claude =====
GAME_TEMPLATE = """Tu tarea: crear un juego MicroPython simple.

Hardware: Display 320x480 (vertical/portrait) RGB565, touch capacitivo.
Primitivas: fill(), rect(), circle(), text(), line(), pixel().
Colores: BLACK=0x0000, WHITE=0xFFFF, RED=0xF800, GREEN=0x07E0, BLUE=0x001F, CYAN=0x07FF.

Estructura requerida:

class Game:
    def __init__(self, renderer, touch):
        self.renderer = renderer
        self.touch = touch
        # Tu inicializacion
    
    def update(self):
        touched, x, y = self.touch.read()
        if touched:
            self.handle_touch(x, y)
        # Tu logica aqui
    
    def draw(self):
        self.renderer.fill(0x0000)
        # Dibuja tu juego
        self.renderer.flush()
    
    def handle_touch(self, x, y):
        pass

Ejemplo renderer:
- self.renderer.rect(x, y, w, h, color, fill=True)
- self.renderer.circle(x, y, radius, color, fill=False)
- self.renderer.text(x, y, texto, color)
- self.renderer.line(x0, y0, x1, y1, color)

Reglas:
- NO imports externos
- NO threading/async
- NO time.sleep()
- Clase llamada Game
- Coordenadas validas: x:0-319, y:0-479 (pantalla vertical)

Descripcion del juego: {description}

Responde SOLO con el codigo Python, sin explicaciones."""

# ===== Prompts para Claude =====
SUGGESTION_PROMPT = """Contexto: {context}

Genera 10 palabras cortas (2-12 caracteres) que continuen naturalmente esta frase.
Palabras apropiadas para ninos y relacionadas con videojuegos.

Responde SOLO con las palabras separadas por comas, sin numeros ni explicaciones.
Ejemplo: aventura,plataforma,carreras,puzzle,arcade,shooter,estrategia,deportes,simulador,retro"""

# ===== Debug =====
DEBUG = True
