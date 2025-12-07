import time
import machine
import lib.logging as logging

logger = logging.getLogger("ft6x36")

class Ft6x36:
    SLAVE_ADDR = 0x38
    
    STATUS_REG = 0x02
    P1_XH_REG  = 0x03
    
    def __init__( self, i2c, ax=1, bx=0, ay=1, by=0, swap_xy=False ):
        """
        Inicializa el controlador táctil FT6x36.
        
        Para modo vertical (320x480):
        - swap_xy=False (ya que la orientación cambia)
        - Los coeficientes ax, bx, ay, by ajustan la calibración
        
        La transformación aplicada es:
        x_final = ax * x_raw + bx
        y_final = ay * y_raw + by
        
        Si swap_xy=True, primero se intercambian x e y antes de la transformación.
        """
        logger.debug("Initializing FT6x36 touch controller...")
        self.i2c = i2c
        self.ax = ax
        self.bx = bx
        self.ay = ay
        self.by = by
        self.swap_xy = swap_xy
        self.read_buffer1 = bytearray(1)
        self.read_buffer4 = bytearray(4)
        logger.info(f"FT6x36 initialized: addr=0x{self.SLAVE_ADDR:02X}, swap_xy={swap_xy}")
        logger.debug(f"Calibration: ax={ax}, bx={bx}, ay={ay}, by={by}")
    
    def read( self ):
        self.i2c.readfrom_mem_into( self.SLAVE_ADDR, self.STATUS_REG, self.read_buffer1 )
        points = self.read_buffer1[0] & 0x0F
        if( points == 1 ):
            time.sleep_ms(1)
            # Read again to avoid glitches
            self.i2c.readfrom_mem_into( self.SLAVE_ADDR, self.STATUS_REG, self.read_buffer1 )
            points = self.read_buffer1[0] & 0x0F
            if( points == 1 ):
                self.i2c.readfrom_mem_into( self.SLAVE_ADDR, self.P1_XH_REG, self.read_buffer4 )
                x = (self.read_buffer4[0] << 8 | self.read_buffer4[1]) & 0x0FFF
                y = (self.read_buffer4[2] << 8 | self.read_buffer4[3]) & 0x0FFF
                
                if( self.swap_xy ):
                    tmp = x
                    x = y
                    y = tmp
                
                x = int( self.ax*x + self.bx )
                y = int( self.ay*y + self.by )
                return 1, x, y
            else:
                return 0, 0, 0
        else:
            return 0, 0, 0