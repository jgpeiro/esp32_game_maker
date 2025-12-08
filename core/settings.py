# settings.py - Gestión de configuración persistente

import ujson as json
import lib.logging as logging

logger = logging.getLogger("settings")

SETTINGS_FILE = "/settings.json"

DEFAULT_SETTINGS = {
    "wifi_enabled": False,
    "wifi_ssid": "",
    "wifi_password": "",
    "api_key": ""
}

class Settings:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        logger.debug("Initializing Settings...")
        self.data = DEFAULT_SETTINGS.copy()
        self.load()
        logger.info(f"Settings initialized. WiFi enabled: {self.data['wifi_enabled']}")
    
    def load(self):
        """Carga la configuración desde el archivo JSON"""
        try:
            with open(SETTINGS_FILE, 'r') as f:
                loaded = json.load(f)
                # Merge con defaults para asegurar que todas las claves existan
                for key in DEFAULT_SETTINGS:
                    if key in loaded:
                        self.data[key] = loaded[key]
                logger.info(f"Settings loaded from {SETTINGS_FILE}")
                logger.debug(f"Settings data: wifi_enabled={self.data['wifi_enabled']}, wifi_ssid={self.data['wifi_ssid']}")
        except OSError:
            logger.info("No settings file found, using defaults")
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
    
    def save(self):
        """Guarda la configuración en el archivo JSON"""
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.data, f)
            logger.info(f"Settings saved to {SETTINGS_FILE}")
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False
    
    @property
    def wifi_enabled(self):
        return self.data.get("wifi_enabled", False)
    
    @wifi_enabled.setter
    def wifi_enabled(self, value):
        self.data["wifi_enabled"] = value
        self.save()
    
    @property
    def wifi_ssid(self):
        return self.data.get("wifi_ssid", "")
    
    @wifi_ssid.setter
    def wifi_ssid(self, value):
        self.data["wifi_ssid"] = value
        self.save()
    
    @property
    def wifi_password(self):
        return self.data.get("wifi_password", "")
    
    @wifi_password.setter
    def wifi_password(self, value):
        self.data["wifi_password"] = value
        self.save()
    
    @property
    def api_key(self):
        return self.data.get("api_key", "")
    
    @api_key.setter
    def api_key(self, value):
        self.data["api_key"] = value
        self.save()
    
    def get_wifi_credentials(self):
        """Retorna las credenciales WiFi como tupla (ssid, password)"""
        return (self.data.get("wifi_ssid", ""), self.data.get("wifi_password", ""))
