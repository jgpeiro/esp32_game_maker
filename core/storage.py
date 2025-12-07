# storage.py - Gestión de almacenamiento de juegos

import os
import ujson as json
import config
import lib.logging as logging

logger = logging.getLogger("storage")

class Storage:
    def __init__(self):
        logger.debug("Initializing Storage...")
        self.games_dir = config.GAMES_DIR
        self._ensure_directory()
        self.metadata_file = f"{self.games_dir}/metadata.json"
        self.metadata = self._load_metadata()
        logger.info(f"Storage initialized. Games directory: {self.games_dir}, {len(self.metadata)} games in metadata")
    
    def _ensure_directory(self):
        """Crea el directorio de juegos si no existe"""
        try:
            os.stat(self.games_dir)
            logger.debug(f"Games directory exists: {self.games_dir}")
        except OSError:
            logger.info(f"Creating games directory: {self.games_dir}")
            os.mkdir(self.games_dir)
    
    def _load_metadata(self):
        """Carga metadata de los juegos"""
        try:
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
                logger.debug(f"Loaded metadata: {len(metadata)} entries")
                return metadata
        except Exception as e:
            logger.debug(f"No metadata file found or error loading: {e}")
            return {}
    
    def _save_metadata(self):
        """Guarda metadata"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f)
            logger.debug(f"Metadata saved: {len(self.metadata)} entries")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
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
            filename = self._sanitize_filename(name)
            filepath = f"{self.games_dir}/{filename}.py"
            logger.debug(f"Sanitized filename: {filename}, path: {filepath}")
            
            # Guarda el código
            with open(filepath, 'w') as f:
                f.write(code)
            logger.debug(f"Game code written: {len(code)} bytes")
            
            # Actualiza metadata
            import time
            timestamp = time.time()
            self.metadata[filename] = {
                "name": name,
                "description": description,
                "created": timestamp,
                "played": 0
            }
            self._save_metadata()
            
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
        for filename, meta in self.metadata.items():
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
            
            if filename in self.metadata:
                del self.metadata[filename]
                self._save_metadata()
                logger.debug("Metadata updated")
            
            logger.info(f"Game '{filename}' deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting game: {e}")
            return False
    
    def increment_played(self, filename):
        """Incrementa el contador de veces jugado"""
        if filename in self.metadata:
            old_count = self.metadata[filename].get("played", 0)
            self.metadata[filename]["played"] = old_count + 1
            self._save_metadata()
            logger.debug(f"Play count for '{filename}': {old_count} -> {old_count + 1}")
    
    def _sanitize_filename(self, name):
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
        #while os.path.exists(f"{self.games_dir}/{filename}.py"):
        #    filename = f"{base}_{counter}"
        #    counter += 1
        existing_files = [f[:-3] for f in os.listdir(self.games_dir) if f.endswith('.py')]
        while filename in existing_files:
            filename = f"{base}_{counter}"
            counter += 1        
        return filename
