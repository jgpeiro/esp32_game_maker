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
CLAUDE_MAX_TOKENS = 16000

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
APPS_DIR = "/apps"
MAX_GAMES = 20
MAX_APPS = 20

# ===== UI Timings =====
SPLASH_DURATION = 3000  # ms
TOUCH_DEBOUNCE = 20     # ms
FRAME_RATE = 30         # FPS

# ===== Prompts y Templates (importados desde prompts.py) =====
from prompts import (
    GAME_TEMPLATE,
    APP_TEMPLATE,
    SUGGESTION_PROMPT,
    APP_TYPE_SUGGESTION_PROMPT,
    APP_FEATURE_SUGGESTION_PROMPT,
    FALLBACK_APP_TYPES,
    FALLBACK_APP_TYPES_POOL,
    FALLBACK_FEATURES_BY_TYPE,
    FALLBACK_APP_FEATURES,
    FALLBACK_GAME_SUGGESTIONS,
)

# ===== Debug =====
DEBUG = True

