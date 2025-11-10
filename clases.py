import pygame
import random
from settings import *
from funciones_auxiliares import *


# -----------------------------------------------------------------
# --- CLASE: Boton ---
# --------------------------------------------------------------
class Boton:
    def __init__(self, rect, texto, color_base, color_hover, color_texto=NEGRO):
        self.rect = rect
        self.texto = texto
        self.color_base = color_base
        self.color_hover = color_hover
        self.color_texto = color_texto

    def draw(self, surface):
        """Dibuja el botón, cambiando de color si el mouse está encima."""
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, self.color_hover, self.rect, border_radius=10)
        else:
            pygame.draw.rect(surface, self.color_base, self.rect, border_radius=10)
        mostrar_mensaje(surface, self.texto, fuente, self.color_texto, self.rect.center)
    
    def is_clicked(self, event):
        """Comprueba si el evento de clic ocurrió en este botón."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                BOTON_SOUND.play()
                return True
        return False

# ----------------------------------------------------------------
# --- CLASE: Player ---
# -----------------------------------------------------------------
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, JUGADOR_SIZE[0], JUGADOR_SIZE[1])
        self.vel = 0
        self.lives = 0
        self.direction = 'down'
        self.inmortal = False
        self.inmortal_start_time = 0
        self.truco_input = ""
        self.truco_activado = False

    def move(self, keys):
        """Actualiza la dirección y posición del jugador basado en las teclas."""
        # 1. Determinar la dirección (prioriza vertical sobre horizontal para la imagen)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction = 'up'
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction = 'down'
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction = 'left'
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction = 'right'
            
        # 2. Aplicar el movimiento (permite diagonales)
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.rect.top > 0: 
            self.rect.y -= self.vel
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.rect.bottom < ALTO: 
            self.rect.y += self.vel
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0: 
            self.rect.x -= self.vel
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < ANCHO: 
            self.rect.x += self.vel
            
    def check_clown_truco(self, key_unicode):
        """Actualiza el input del truco y lo activa si coincide."""
        if key_unicode.isalpha():
            self.truco_input = (self.truco_input + key_unicode.lower())[-5:]
            if self.truco_input == "clown":
                self.truco_activado = True
                CLOWN_SOUND.play() #!se puede bugear el sonido
                self.lives += 20 #?dar vidas extra por el truco 
                self.rect = pygame.Rect(self.rect.x, self.rect.y, CLOWN_SIZE[0], CLOWN_SIZE[1]) # Ajustar hitbox al tamaño clown
                self.vel += -3 #? Reducir velocidad al activar truco
                
    def get_hit(self):
        """Procesa un golpe. Devuelve True si el jugador se queda sin vidas."""
        if not self.inmortal:
            self.lives -= 1
            HIT_SOUND.play()
            return self.lives <= 0
        return False

    def activate_shield(self, current_time):
        """Activa el estado de inmortalidad."""
        self.inmortal = True
        self.inmortal_start_time = current_time
        POWERUP_SOUND.play()
        
    def add_life(self):
        """Añade una vida."""
        self.lives += 1
        POWERUP_SOUND.play()

    def update_timers(self, current_time):
        """Desactiva power-ups si el tiempo ha expirado."""
        if self.inmortal and current_time - self.inmortal_start_time > INMORTAL_DURATION:
            self.inmortal = False

    def draw(self, surface, current_time):
        """Dibuja al jugador en la pantalla, manejando el parpadeo."""
        if self.truco_activado:
            current_image_set = JUGADOR_CLOWN_IMGS
        else:
            current_image_set = JUGADOR_IMGS    
        imagen_jugador_actual = current_image_set[self.direction]
        
        # Lógica de parpadeo (inmortalidad)
        if not (self.inmortal and (current_time // 150) % 2 == 0):
            surface.blit(imagen_jugador_actual, self.rect)
        
        # Dibuja el temporizador de inmortalidad
        if self.inmortal:
            tiempo_restante = (INMORTAL_DURATION - (current_time - self.inmortal_start_time)) // 1000 + 1
            mostrar_mensaje(surface, f"INMORTAL: {tiempo_restante}s", fuente_pequena, ROJO_TEXTO, (self.rect.centerx, self.rect.top - 20))

# -----------------------------------------------------------------
# CLASE: Enemigo 
# -----------------------------------------------------------------
class Enemigo:
    def __init__(self, vel_min, vel_max):
        """Genera un enemigo en un borde aleatorio con una dirección fija."""
        lado = random.randint(1, 4) 
        velocidad = random.randint(vel_min, vel_max)
        self.dx, self.dy = 0, 0

        if lado == 1: # Arriba
            x, y = random.randint(0, ANCHO - ENEMIGO_SIZE[0]), -ENEMIGO_SIZE[1]
            self.dy = velocidad
        elif lado == 2: # Abajo
            x, y = random.randint(0, ANCHO - ENEMIGO_SIZE[0]), ALTO
            self.dy = -velocidad
        elif lado == 3: # Izquierda
            x, y = -ENEMIGO_SIZE[0], random.randint(0, ALTO - ENEMIGO_SIZE[1])
            self.dx = velocidad
        else: # Derecha
            x, y = ANCHO, random.randint(0, ALTO - ENEMIGO_SIZE[1])
            self.dx = -velocidad
            
        self.rect = pygame.Rect(x, y, ENEMIGO_SIZE[0], ENEMIGO_SIZE[1])

    def move(self, speed_multiplier):
        """Mueve al enemigo, aplicando el multiplicador de slow-mo."""
        self.rect.x += self.dx * speed_multiplier
        self.rect.y += self.dy * speed_multiplier

    def draw(self, surface):
        surface.blit(ENEMIGO_IMG, self.rect)
        
    def is_offscreen(self):
        """Comprueba si está fuera de la pantalla para ser eliminado."""
        return not (-100 < self.rect.x < ANCHO + 100 and -100 < self.rect.y < ALTO + 100)

# ------------------------------------------------------------
# CLASE: PowerUp 
# ----------------------------------------------------------------
class PowerUp:
    def __init__(self):
        """Genera un power-up aleatorio en una posición aleatoria."""
        spawn_x = random.randint(50, ANCHO - 50)
        spawn_y = random.randint(50, ALTO - 50)
        self.type = random.choice(['health', 'shield', 'slowmo'])
        self.dx, self.dy = 0, 0
        
        if self.type == 'health':
            self.rect = pygame.Rect(spawn_x, spawn_y, POWERUP_SIZE_VIDA[0], POWERUP_SIZE_VIDA[1])
            self.image = VIDA_IMG
        elif self.type == 'shield':
            self.rect = pygame.Rect(spawn_x, spawn_y, POWERUP_SIZE_ESCUDO[0], POWERUP_SIZE_ESCUDO[1])
            self.image = ESCUDO_IMG
        else: # 'slowmo'
            self.rect = pygame.Rect(spawn_x, spawn_y, POWERUP_SIZE_SLOWMO[0], POWERUP_SIZE_SLOWMO[1])
            self.image = SLOWMO_IMG
            self.dx = random.choice([-POWERUP_VEL, POWERUP_VEL])
            self.dy = random.choice([-POWERUP_VEL, POWERUP_VEL])

    def move(self):
        """Mueve el power-up (solo si es 'slowmo') y rebota."""
        if self.type == 'slowmo':
            self.rect.x += self.dx
            self.rect.y += self.dy
            if self.rect.left <= 0 or self.rect.right >= ANCHO: self.dx *= -1
            if self.rect.top <= 0 or self.rect.bottom >= ALTO: self.dy *= -1
            
    def draw(self, surface):
        surface.blit(self.image, self.rect)
