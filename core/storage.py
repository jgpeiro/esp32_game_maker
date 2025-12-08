# storage.py - Gestión de almacenamiento de juegos y aplicaciones

import os
import ujson as json
import config
import lib.logging as logging

logger = logging.getLogger("storage")

class Storage:
    def __init__(self):
        logger.debug("Initializing Storage...")
        self.games_dir = config.GAMES_DIR
        self.apps_dir = config.APPS_DIR
        self._ensure_directory(self.games_dir)
        self._ensure_directory(self.apps_dir)
        self.games_metadata_file = f"{self.games_dir}/metadata.json"
        self.apps_metadata_file = f"{self.apps_dir}/metadata.json"
        self.games_metadata = self._load_metadata(self.games_metadata_file)
        self.apps_metadata = self._load_metadata(self.apps_metadata_file)
        logger.info(f"Storage initialized. Games: {len(self.games_metadata)}, Apps: {len(self.apps_metadata)}")
    
    def _ensure_directory(self, dir_path):
        """Crea el directorio si no existe"""
        try:
            os.stat(dir_path)
            logger.debug(f"Directory exists: {dir_path}")
        except OSError:
            logger.info(f"Creating directory: {dir_path}")
            os.mkdir(dir_path)
    
    def _load_metadata(self, filepath):
        """Carga metadata desde un archivo"""
        try:
            with open(filepath, 'r') as f:
                metadata = json.load(f)
                logger.debug(f"Loaded metadata from {filepath}: {len(metadata)} entries")
                return metadata
        except Exception as e:
            logger.debug(f"No metadata file found or error loading {filepath}: {e}")
            return {}
    
    def _save_metadata(self, filepath, metadata):
        """Guarda metadata en un archivo"""
        try:
            with open(filepath, 'w') as f:
                json.dump(metadata, f)
            logger.debug(f"Metadata saved to {filepath}: {len(metadata)} entries")
        except Exception as e:
            logger.error(f"Error saving metadata to {filepath}: {e}")
    
    def save_game(self, name, code, description=""):
        """
        Guarda un juego
        
        Args:
            name: Nombre del juego
            code: Código Python del juego
            description: Descripción opcional
        
        Returns:
            True si se guardó correctamente
        """
        logger.info(f"Saving game: '{name}'")
        try:
            # Sanitiza el nombre para usarlo como archivo
            filename = self._sanitize_filename(name, self.games_dir)
            filepath = f"{self.games_dir}/{filename}.py"
            logger.debug(f"Sanitized filename: {filename}, path: {filepath}")
            
            # Guarda el código
            with open(filepath, 'w') as f:
                f.write(code)
            logger.debug(f"Game code written: {len(code)} bytes")
            
            # Actualiza metadata
            import time
            timestamp = time.time()
            self.games_metadata[filename] = {
                "name": name,
                "description": description,
                "created": timestamp,
                "played": 0
            }
            self._save_metadata(self.games_metadata_file, self.games_metadata)
            
            logger.info(f"Game '{name}' saved successfully as '{filename}'")
            return True
        except Exception as e:
            logger.error(f"Error saving game: {e}")
            return False
    
    def load_game(self, filename):
        """
        Carga el código de un juego
        
        Args:
            filename: Nombre del archivo (sin extensión)
        
        Returns:
            Código del juego o None
        """
        logger.info(f"Loading game: {filename}")
        try:
            filepath = f"{self.games_dir}/{filename}.py"
            with open(filepath, 'r') as f:
                code = f.read()
            logger.debug(f"Game loaded: {len(code)} bytes")
            return code
        except Exception as e:
            logger.error(f"Error loading game: {e}")
            return None
    
    def list_games(self):
        """
        Lista todos los juegos guardados
        
        Returns:
            Lista de diccionarios con información de cada juego
        """
        logger.debug("Listing all games...")
        games = []
        for filename, meta in self.games_metadata.items():
            games.append({
                "filename": filename,
                "name": meta.get("name", filename),
                "description": meta.get("description", ""),
                "created": meta.get("created", 0),
                "played": meta.get("played", 0)
            })
        
        # Ordena por fecha de creación (más reciente primero)
        games.sort(key=lambda x: x["created"], reverse=True)
        logger.debug(f"Found {len(games)} games")
        return games
    
    def delete_game(self, filename):
        """
        Elimina un juego
        
        Args:
            filename: Nombre del archivo (sin extensión)
        
        Returns:
            True si se eliminó correctamente
        """
        logger.info(f"Deleting game: {filename}")
        try:
            filepath = f"{self.games_dir}/{filename}.py"
            os.remove(filepath)
            logger.debug(f"File removed: {filepath}")
            
            if filename in self.games_metadata:
                del self.games_metadata[filename]
                self._save_metadata(self.games_metadata_file, self.games_metadata)
                logger.debug("Metadata updated")
            
            logger.info(f"Game '{filename}' deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting game: {e}")
            return False
    
    def increment_played(self, filename):
        """Incrementa el contador de veces jugado"""
        if filename in self.games_metadata:
            old_count = self.games_metadata[filename].get("played", 0)
            self.games_metadata[filename]["played"] = old_count + 1
            self._save_metadata(self.games_metadata_file, self.games_metadata)
            logger.debug(f"Play count for '{filename}': {old_count} -> {old_count + 1}")
    
    # ===== Métodos para Apps =====
    
    def save_app(self, name, code, description=""):
        """
        Guarda una aplicación
        
        Args:
            name: Nombre de la app
            code: Código Python de la app
            description: Descripción opcional
        
        Returns:
            True si se guardó correctamente
        """
        logger.info(f"Saving app: '{name}'")
        try:
            filename = self._sanitize_filename(name, self.apps_dir)
            filepath = f"{self.apps_dir}/{filename}.py"
            logger.debug(f"Sanitized filename: {filename}, path: {filepath}")
            
            with open(filepath, 'w') as f:
                f.write(code)
            logger.debug(f"App code written: {len(code)} bytes")
            
            import time
            timestamp = time.time()
            self.apps_metadata[filename] = {
                "name": name,
                "description": description,
                "created": timestamp,
                "used": 0
            }
            self._save_metadata(self.apps_metadata_file, self.apps_metadata)
            
            logger.info(f"App '{name}' saved successfully as '{filename}'")
            return True
        except Exception as e:
            logger.error(f"Error saving app: {e}")
            return False
    
    def load_app(self, filename):
        """
        Carga el código de una app
        
        Args:
            filename: Nombre del archivo (sin extensión)
        
        Returns:
            Código de la app o None
        """
        logger.info(f"Loading app: {filename}")
        try:
            filepath = f"{self.apps_dir}/{filename}.py"
            with open(filepath, 'r') as f:
                code = f.read()
            logger.debug(f"App loaded: {len(code)} bytes")
            return code
        except Exception as e:
            logger.error(f"Error loading app: {e}")
            return None
    
    def list_apps(self):
        """
        Lista todas las apps guardadas
        
        Returns:
            Lista de diccionarios con información de cada app
        """
        logger.debug("Listing all apps...")
        apps = []
        for filename, meta in self.apps_metadata.items():
            apps.append({
                "filename": filename,
                "name": meta.get("name", filename),
                "description": meta.get("description", ""),
                "created": meta.get("created", 0),
                "used": meta.get("used", 0)
            })
        
        apps.sort(key=lambda x: x["created"], reverse=True)
        logger.debug(f"Found {len(apps)} apps")
        return apps
    
    def delete_app(self, filename):
        """
        Elimina una app
        
        Args:
            filename: Nombre del archivo (sin extensión)
        
        Returns:
            True si se eliminó correctamente
        """
        logger.info(f"Deleting app: {filename}")
        try:
            filepath = f"{self.apps_dir}/{filename}.py"
            os.remove(filepath)
            logger.debug(f"File removed: {filepath}")
            
            if filename in self.apps_metadata:
                del self.apps_metadata[filename]
                self._save_metadata(self.apps_metadata_file, self.apps_metadata)
                logger.debug("Metadata updated")
            
            logger.info(f"App '{filename}' deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting app: {e}")
            return False
    
    def increment_app_used(self, filename):
        """Incrementa el contador de veces usada"""
        if filename in self.apps_metadata:
            old_count = self.apps_metadata[filename].get("used", 0)
            self.apps_metadata[filename]["used"] = old_count + 1
            self._save_metadata(self.apps_metadata_file, self.apps_metadata)
            logger.debug(f"Use count for app '{filename}': {old_count} -> {old_count + 1}")
    
    def _sanitize_filename(self, name, directory):
        """Convierte un nombre en un nombre de archivo válido"""
        # Reemplaza espacios y caracteres especiales
        valid = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
        filename = ""
        for c in name:
            if c == " ":
                filename += "_"
            elif c in valid:
                filename += c
        
        # Limita longitud
        filename = filename[:30]
        
        # Evita duplicados
        base = filename
        counter = 1
        existing_files = [f[:-3] for f in os.listdir(directory) if f.endswith('.py')]
        while filename in existing_files:
            filename = f"{base}_{counter}"
            counter += 1        
        return filename
