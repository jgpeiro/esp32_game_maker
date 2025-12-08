# app.py - Controlador principal de la aplicación

import time
import network
import config
import lib.logging as logging
from core.renderer import Renderer
from core.claude_api import ClaudeAPI
from core.storage import Storage
from core.settings import Settings
from ui.splash_screen import SplashScreen
        
logger = logging.getLogger("app")

class App:
    def __init__(self, display, touch):
        logger.debug("Initializing App...")
        self.display = display
        self.touch = touch
        self.renderer = Renderer(display)
        self.api = ClaudeAPI()
        self.storage = Storage()
        self.settings = Settings()
        
        self.current_screen = None
        self.running = True
        self.last_frame_time = time.ticks_ms()
        self.target_frame_time = 1000 // config.FRAME_RATE
        
        self.wlan = network.WLAN(network.STA_IF)
        logger.debug(f"App initialized with target frame time: {self.target_frame_time}ms")
    
    def _connect_wifi(self):
        """Conecta a WiFi usando la configuración guardada"""
        # Verificar si WiFi está habilitado en settings
        if not self.settings.wifi_enabled:
            logger.info("WiFi disabled in settings, skipping connection")
            return
        
        logger.info("Activating WLAN interface...")
        self.wlan.active(True)
        
        if not self.wlan.isconnected():
            # Usar credenciales de settings si están disponibles
            ssid = self.settings.wifi_ssid
            password = self.settings.wifi_password
            
            if not ssid:
                # Fallback a config.py si no hay credenciales guardadas
                ssid = config.WIFI_SSID
                password = config.WIFI_PASSWORD
                logger.info("Using WiFi credentials from config.py (no saved settings)")
            
            logger.info(f"Connecting to WiFi SSID: {ssid}...")
            
            self.wlan.connect(ssid, password)
            
            # Espera conexión con timeout
            timeout = config.WIFI_TIMEOUT
            while not self.wlan.isconnected() and timeout > 0:
                time.sleep(1)
                timeout -= 1
                logger.debug(f"WiFi connection attempt... {config.WIFI_TIMEOUT - timeout}/{config.WIFI_TIMEOUT}s")
            
            if self.wlan.isconnected():
                ip = self.wlan.ifconfig()[0]
                logger.info(f"WiFi connected! IP: {ip}")
            else:
                logger.error("WiFi connection failed!")
        else:
            logger.info(f"WiFi already connected. IP: {self.wlan.ifconfig()[0]}")
    
    def change_screen(self, new_screen):
        """Cambia a una nueva pantalla"""
        old_screen_name = type(self.current_screen).__name__ if self.current_screen else "None"
        new_screen_name = type(new_screen).__name__
        logger.info(f"Screen transition: {old_screen_name} -> {new_screen_name}")
        
        if self.current_screen:
            logger.debug(f"Exiting screen: {old_screen_name}")
            self.current_screen.exit()
        
        self.current_screen = new_screen
        logger.debug(f"Entering screen: {new_screen_name}")
        self.current_screen.enter()
    
    def run(self):
        """Loop principal de la aplicación"""
        logger.info("Starting main application loop...")
        
        # Inicia con splash screen
        logger.debug("Loading SplashScreen...")
        self.change_screen(SplashScreen(self))
        self.current_screen.update()
        self.current_screen.draw()
        
        # Conecta WiFi
        self._connect_wifi()
        
        frame_count = 0
        while self.running:
            frame_start = time.ticks_ms()
            
            # Lee touch
            touched, x, y = self.touch.read()
            if touched and self.current_screen:
                logger.debug(f"Touch detected at ({x}, {y})")
                self.current_screen.handle_touch(x, y)
            
            # Actualiza pantalla actual
            if self.current_screen:
                self.current_screen.update()
                self.current_screen.draw()
            
            # Control de frame rate
            frame_time = time.ticks_diff(time.ticks_ms(), frame_start)
            if frame_time < self.target_frame_time:
                time.sleep_ms(self.target_frame_time - frame_time)
            
            self.last_frame_time = frame_start
            
            frame_count += 1
            if frame_count % 300 == 0:  # Log every 300 frames (~10 seconds at 30fps)
                logger.debug(f"Frame {frame_count}, last frame time: {frame_time}ms")


