import pygame
import sys

# Inicializaciones de Audio y General
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()
pygame.font.init()
ICONO = pygame.image.load("./assets/img/icono.png")
pygame.display.set_icon(ICONO)
pygame.display.set_caption("SUMO-DUMO-ARG🍚")


#  Configuración y constantes 
ANCHO, ALTO = 900, 700
screen = pygame.display.set_mode((ANCHO, ALTO))
PUNTAJES_FILE = 'puntajes.csv'

# Colores 
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS = (100, 100, 100)
VERDE_CLARO = (0, 200, 0)
AMARILLO_TEXTO = (255, 255, 0)
AMARILLO_CLARO = (200, 200, 0)
ROJO_CLARO = (200, 0, 0)
AZUL_TEXTO = (0, 150, 255)
NARANJA_TEXTO = (255, 165, 0)
ROJO_TEXTO = (255, 0, 0)

# Colisiones de Hitbox 
CLOWN_SIZE = (80, 80)
JUGADOR_SIZE = (68, 68)
ENEMIGO_SIZE = (60, 60)
POWERUP_SIZE_VIDA = (60, 60)
POWERUP_SIZE_ESCUDO = (60, 60)
POWERUP_SIZE_SLOWMO = (60, 60)
POWERUP_VEL = 2

#  Constantes de Efectos 
INMORTAL_DURATION = 5000
SLOWMO_DURATION = 5000
POWERUP_SPAWN_RATE = 420 # Frames

# Carga de Imágenes (Global)

try:
    FONDO_MENU_IMG = pygame.transform.scale(pygame.image.load("./assets/img/fondo_menu.png"), (ANCHO, ALTO)).convert()
    FONDO_JUEGO_IMG = pygame.transform.scale(pygame.image.load("./assets/img/fondo_juego.png"), (ANCHO, ALTO)).convert()
    FONDO_GAMEOVER_IMG = pygame.transform.scale(pygame.image.load("./assets/img/fondo_game_over.jpg"), (ANCHO, ALTO)).convert()

    JUGADOR_IMGS = {
        'down': pygame.transform.scale(pygame.image.load("./assets/img/sumo_azul_down.png"), JUGADOR_SIZE).convert_alpha(),
        'up': pygame.transform.scale(pygame.image.load("./assets/img/sumo_azul_up.png"), JUGADOR_SIZE).convert_alpha(),
        'left': pygame.transform.scale(pygame.image.load("./assets/img/sumo_azul_left.png"), JUGADOR_SIZE).convert_alpha(),
        'right': pygame.transform.scale(pygame.image.load("./assets/img/sumo_azul_right.png"), JUGADOR_SIZE).convert_alpha()
    }
    JUGADOR_CLOWN_IMGS = {
        'down': pygame.transform.scale(pygame.image.load("./assets/img/clown_sumo_down.png"), CLOWN_SIZE).convert_alpha(), 
        'up': pygame.transform.scale(pygame.image.load("./assets/img/clown_sumo_up.png"), CLOWN_SIZE).convert_alpha(), 
        'left': pygame.transform.scale(pygame.image.load("./assets/img/clown_sumo_left.png"), CLOWN_SIZE).convert_alpha(),
        'right': pygame.transform.scale(pygame.image.load("./assets/img/clown_sumo_right.png"), CLOWN_SIZE).convert_alpha()
    }
    ENEMIGO_IMG = pygame.transform.scale(pygame.image.load("./assets/img/sumo_rojo_down.png"), ENEMIGO_SIZE).convert_alpha()
    VIDA_IMG = pygame.transform.scale(pygame.image.load("./assets/img/shield_power_up.png"), POWERUP_SIZE_VIDA).convert_alpha()
    ESCUDO_IMG = pygame.transform.scale(pygame.image.load("./assets/img/empanada_shield.png"), POWERUP_SIZE_ESCUDO).convert_alpha()
    SLOWMO_IMG = pygame.transform.scale(pygame.image.load("./assets/img/choripan_slowmo_power_up.png"), POWERUP_SIZE_SLOWMO).convert_alpha()
    
except FileNotFoundError as e:
    print(f"¡Error! No se pudo cargar una imagen: {e}")
    pygame.quit()
    sys.exit()

#  Carga de Sonidos (Global) 
try:
    BOTON_SOUND = pygame.mixer.Sound("./assets/sounds/button_sound.mp3")
    POWERUP_SOUND = pygame.mixer.Sound("./assets/sounds/power_up_sound.mp3")
    HIT_SOUND = pygame.mixer.Sound("./assets/sounds/hit_sound.mp3")
    CLOWN_SOUND = pygame.mixer.Sound("./assets/sounds/clown_sound.mp3")
    MUSICA_MENU = "./assets/sounds/menu_music.mp3"
    MUSICA_JUEGO = "./assets/sounds/game_music.mp3"
    MUSICA_GAMEOVER = "./assets/sounds/game_over_sound.mp3"
    BOTON_SOUND.set_volume(0.5)
    POWERUP_SOUND.set_volume(0.5)
    HIT_SOUND.set_volume(0.5)
    CLOWN_SOUND.set_volume(0.5)
    
except FileNotFoundError as e:
    print(f"¡Error! No se pudo cargar un archivo de sonido: {e}")
    pygame.quit()
    sys.exit()

#  Fuentes y Reloj (Global) 
try:
    fuente = pygame.font.Font("./assets/fonts/fuente_chica.ttf", 25)
    fuente_pequena = pygame.font.Font("./assets/fonts/fuente_media.ttf", 20)
    fuente_grande = pygame.font.Font("./assets/fonts/fuente_grande.ttf", 40)
    fuente_puntaje = pygame.font.Font("./assets/fonts/fuente_grande.ttf", 25)
except FileNotFoundError as e:
    print(f"¡Error! No se pudo cargar una fuente: {e}")
    pygame.quit()
    sys.exit()    
    
reloj = pygame.time.Clock()

#  Coordenadas de Volumen (Global)
VOL_Y_POS = 10 
VOL_BTN_WIDTH = 30
VOL_BTN_GAP = 5
TOTAL_VOL_WIDTH = (VOL_BTN_WIDTH * 3) + (VOL_BTN_GAP * 2) 
VOL_START_X = (ANCHO // 2) - (TOTAL_VOL_WIDTH // 2) 
VOL_MENOS_RECT = pygame.Rect(VOL_START_X, VOL_Y_POS, VOL_BTN_WIDTH, VOL_BTN_WIDTH)
VOL_MUTE_RECT = pygame.Rect(VOL_START_X + VOL_BTN_WIDTH + VOL_BTN_GAP, VOL_Y_POS, VOL_BTN_WIDTH, VOL_BTN_WIDTH)
VOL_MAS_RECT = pygame.Rect(VOL_START_X + (VOL_BTN_WIDTH + VOL_BTN_GAP) * 2, VOL_Y_POS, VOL_BTN_WIDTH, VOL_BTN_WIDTH)