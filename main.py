# main.py - Punto de entrada de Game Maker Console

import machine
import config
import lib.logging as logging
from hal.st7796s import St7796s
from hal.ft6x36 import Ft6x36
from core.app import App

# Configure root logger
logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
)
logger = logging.getLogger("main")


def main():
    logger.info("Starting Game Maker Console...")
    
    # Inicializa SPI para LCD
    logger.debug("Initializing SPI for LCD...")
    spi = machine.SPI(
        config.SPI_ID,
        baudrate=config.SPI_BAUDRATE,
        sck=machine.Pin(config.SPI_SCK),
        mosi=machine.Pin(config.SPI_MOSI),
        miso=None #machine.Pin(config.SPI_MISO)
    )
    logger.debug(f"SPI initialized: ID={config.SPI_ID}, baudrate={config.SPI_BAUDRATE}")
    
    # Inicializa LCD
    logger.debug("Initializing LCD display...")
    display = St7796s(
        spi=spi,
        rst=machine.Pin(config.LCD_RST, machine.Pin.OUT),
        cs=machine.Pin(config.LCD_CS, machine.Pin.OUT),
        dc=machine.Pin(config.LCD_DC, machine.Pin.OUT),
        bl=machine.Pin(config.LCD_BL, machine.Pin.OUT)
    )
    logger.info(f"LCD initialized: {display.WIDTH}x{display.HEIGHT}")
    
    # Inicializa I2C para Touch
    logger.debug("Initializing I2C for Touch...")
    i2c = machine.I2C(
        config.I2C_ID,
        scl=machine.Pin(config.I2C_SCL),
        sda=machine.Pin(config.I2C_SDA),
        freq=config.I2C_FREQ
    )
    logger.debug(f"I2C initialized: ID={config.I2C_ID}, freq={config.I2C_FREQ}")
    
    # Inicializa Touch
    logger.debug("Initializing Touch controller...")
    touch = Ft6x36(
        i2c=i2c,
        ax=config.TOUCH_AX,
        bx=config.TOUCH_BX,
        ay=config.TOUCH_AY,
        by=config.TOUCH_BY,
        swap_xy=config.TOUCH_SWAP_XY
    )
    logger.info("Touch controller initialized")
    
    # Crea y ejecuta la aplicación
    logger.info("Creating App instance...")
    app = App(display, touch)
    
    try:
        logger.info("Starting main application loop")
        app.run()
    except KeyboardInterrupt:
        logger.warning("Application stopped by user (KeyboardInterrupt)")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        if config.DEBUG:
            import sys
            sys.print_exception(e)

if __name__ == "__main__":
    main()

