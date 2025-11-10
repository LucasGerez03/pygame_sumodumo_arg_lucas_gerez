import pygame
import random
import sys
from settings import *
from funciones_auxiliares import *
from clases import Player, Enemigo, PowerUp, Boton

# -----------------------------------------------------------------
# CLASE Game (MAIN)

class Game:
    def __init__(self):
        """Inicializa el juego, la ventana, y los estados."""
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = 'MENU' # Estados: MENU, DIFFICULTY, SCORES, PLAYING, GAME_OVER
        
        # --- Variables de Volumen ---
        self.current_music_volume = 0.5
        self.volume_before_mute = 0.5
        
        # --- Inicializar Botones de Menús ---
        self.btn_jugar = Boton(pygame.Rect(ANCHO // 2 - 100, ALTO // 2 - 40, 200, 60), "Jugar", VERDE_CLARO, GRIS, NEGRO)
        self.btn_puntajes = Boton(pygame.Rect(ANCHO // 2 - 100, ALTO // 2 + 40, 200, 60), "Puntajes", VERDE_CLARO, GRIS, NEGRO)
        
        self.btn_facil = Boton(pygame.Rect(ANCHO // 2 - 100, ALTO // 2 - 100, 200, 50), "Bebe Lloron", VERDE_CLARO, GRIS)
        self.btn_normal = Boton(pygame.Rect(ANCHO // 2 - 100, ALTO // 2, 200, 50), "Normal", AMARILLO_TEXTO, AMARILLO_CLARO, NEGRO)
        self.btn_dificil = Boton(pygame.Rect(ANCHO // 2 - 100, ALTO // 2 + 100, 200, 50), "HARDCORE", ROJO_TEXTO, ROJO_CLARO, BLANCO)
        self.btn_volver_menu = Boton(pygame.Rect(20, ALTO - 70, 200, 50), "Volver",AMARILLO_CLARO, GRIS )
        
        self.btn_volver_scores = Boton(pygame.Rect(ANCHO - 220, ALTO - 70, 200, 50), "Volver", AMARILLO_CLARO, GRIS)
        
        # --- Variables de estado del juego (se reinician en start_new_game) ---
        self.player = Player(ANCHO // 2 - JUGADOR_SIZE[0] // 2, ALTO // 2 - JUGADOR_SIZE[1] // 2)
        self.enemies = []
        self.powerups = []
        self.score = 0
        self.difficulty_settings = {}
        
        # Timers
        self.contador_spawn_enemigo = 0
        self.contador_spawn_powerup = 0
        self.slow_mo = False
        self.slow_mo_start_time = 0
        
        # Variables de Game Over
        self.iniciales_input = ""
        self.input_rect = pygame.Rect(ANCHO // 2 - 75, ALTO // 2 + 50, 150, 50)
        self.btn_volver_gameover = Boton(pygame.Rect(ANCHO // 2 - 100, ALTO // 2 + 150, 200, 50), "Volver", GRIS, AMARILLO_CLARO)

    def start_new_game(self, dificultad: str):
        """Configura todas las variables para una nueva partida."""
        if dificultad == "facil":
            self.difficulty_settings = {'vidas': 4, 'max_spawn': 40, 'vel_min': 2, 'vel_max': 5, 'jugador_vel': 4, 'score_mult': 1}
        elif dificultad == "normal":
            self.difficulty_settings = {'vidas': 3, 'max_spawn': 35, 'vel_min': 4, 'vel_max': 7, 'jugador_vel': 6, 'score_mult': 3}
        else: # Dificil
            self.difficulty_settings = {'vidas': 2, 'max_spawn': 30, 'vel_min': 4, 'vel_max': 9, 'jugador_vel': 7, 'score_mult': 5}
            
        # Reiniciar jugador
        self.player = Player(ANCHO // 2 - JUGADOR_SIZE[0] // 2, ALTO // 2 - JUGADOR_SIZE[1] // 2)
        self.player.lives = self.difficulty_settings['vidas']
        self.player.vel += self.difficulty_settings['jugador_vel'] 
        
        # Reiniciar listas y puntaje
        self.enemies = []
        self.powerups = []
        self.score = 0
        
        # Reiniciar timers y estados
        self.contador_spawn_enemigo = 0
        self.contador_spawn_powerup = 0
        self.slow_mo = False
        self.slow_mo_start_time = 0
        
        # Empezar música del juego
        pygame.mixer.music.stop()
        try:
            pygame.mixer.music.load(MUSICA_JUEGO)
            pygame.mixer.music.set_volume(self.current_music_volume) 
            pygame.mixer.music.play(-1)
        except pygame.error as e: print(f"No se pudo cargar la música del juego: {e}")

    # --- Funciones de Volumen ---
    def dibujar_ui_volumen(self):
        pygame.draw.rect(self.screen, GRIS, VOL_MENOS_RECT, 2, 3)
        pygame.draw.rect(self.screen, GRIS, VOL_MUTE_RECT, 2, 3)
        pygame.draw.rect(self.screen, GRIS, VOL_MAS_RECT, 2, 3)
        mostrar_mensaje(self.screen, "-", fuente_pequena, BLANCO, VOL_MENOS_RECT.center)
        color_mute = ROJO_TEXTO if self.current_music_volume == 0 else BLANCO
        mostrar_mensaje(self.screen, "M", fuente_pequena, color_mute, VOL_MUTE_RECT.center)
        mostrar_mensaje(self.screen, "+", fuente_pequena, BLANCO, VOL_MAS_RECT.center)

    def manejar_clic_volumen(self, event_pos):
        vol_changed = False
        if VOL_MENOS_RECT.collidepoint(event_pos):
            self.current_music_volume = max(0.0, self.current_music_volume - 0.1)
            vol_changed = True
        elif VOL_MAS_RECT.collidepoint(event_pos):
            self.current_music_volume = min(1.0, self.current_music_volume + 0.1)
            vol_changed = True
        elif VOL_MUTE_RECT.collidepoint(event_pos):
            if self.current_music_volume > 0:
                self.volume_before_mute = self.current_music_volume 
                self.current_music_volume = 0.0
            else:
                self.current_music_volume = self.volume_before_mute 
            vol_changed = True
        
        if vol_changed:
            pygame.mixer.music.set_volume(round(self.current_music_volume, 2))

    # Bucles de Estado del Juego 
    
    def run_menu(self):
        """Bucle para el estado del Menú Principal."""
        # Cargar música de menú solo si no está ya sonando
        if not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.load(MUSICA_MENU)
                pygame.mixer.music.set_volume(self.current_music_volume) 
                pygame.mixer.music.play(-1)
            except pygame.error as e: print(f"No se pudo cargar la música del menú: {e}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.manejar_clic_volumen(event.pos)
                if self.btn_jugar.is_clicked(event):
                    self.game_state = 'DIFFICULTY'
                if self.btn_puntajes.is_clicked(event):
                    self.game_state = 'SCORES'
        
        self.screen.blit(FONDO_MENU_IMG, (0, 0))
        mostrar_mensaje(self.screen, "SUMO DUMO ARG", fuente_grande, AMARILLO_CLARO, (ANCHO // 2, ALTO // 2 - 240))
        self.btn_jugar.draw(self.screen)
        self.btn_puntajes.draw(self.screen)
        self.dibujar_ui_volumen()
        pygame.display.flip()
        self.clock.tick(15)

    def run_difficulty(self):
        """Bucle para la pantalla de selección de dificultad."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.manejar_clic_volumen(event.pos)
                
                if self.btn_volver_menu.is_clicked(event):
                    self.game_state = 'MENU'
                    return # Salir del bucle para cambiar de estado

                if self.btn_facil.is_clicked(event):
                    self.start_new_game("facil")                    
                elif self.btn_normal.is_clicked(event):
                    self.start_new_game("normal")  
                elif self.btn_dificil.is_clicked(event):
                    self.start_new_game("dificil")
                self.game_state = 'PLAYING'

        self.screen.blit(FONDO_MENU_IMG_DIFUMINADO, (0, 0))
        mostrar_mensaje(self.screen, "Selecciona Dificultad", fuente_grande, BLANCO, (ANCHO // 2, 100))
        self.btn_facil.draw(self.screen)
        self.btn_normal.draw(self.screen)
        self.btn_dificil.draw(self.screen)
        self.btn_volver_menu.draw(self.screen)
        self.dibujar_ui_volumen()
        pygame.display.flip()
        self.clock.tick(15)

    def run_scores(self):
        """Bucle para la pantalla de puntajes."""
        puntajes_leidos = leer_puntajes()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.manejar_clic_volumen(event.pos)
                if self.btn_volver_scores.is_clicked(event):
                    self.game_state = 'MENU'
                    return

        self.screen.blit(FONDO_MENU_IMG_DIFUMINADO, (0, 0)) 
        mostrar_mensaje(self.screen, "Mejores Puntajes", fuente_grande, BLANCO, (ANCHO // 2, 80))
        
        if not puntajes_leidos:
            mostrar_mensaje(self.screen, "Aún no hay puntajes guardados", fuente, GRIS, (ANCHO // 2, ALTO // 2))
        else:
            y_pos = 150 
            for i, (iniciales, puntaje) in enumerate(puntajes_leidos[:10]): 
                mostrar_mensaje(self.screen, f"{i + 1}.", fuente_puntaje, ROJO_CLARO, (ANCHO // 2 - 150, y_pos))
                mostrar_mensaje(self.screen, f"{iniciales}", fuente_puntaje, NEGRO, (ANCHO // 2, y_pos))
                mostrar_mensaje(self.screen, f"{puntaje}", fuente_puntaje, NEGRO, (ANCHO // 2 + 150, y_pos))
                y_pos += 40 

        self.btn_volver_scores.draw(self.screen)
        self.dibujar_ui_volumen() 
        pygame.display.flip()
        self.clock.tick(15)

    def run_game_over(self):
        """Bucle para la pantalla de Game Over y guardado de puntaje."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.manejar_clic_volumen(event.pos)
                    # Botón de volver (si no se han escrito 3 iniciales)
                    if self.btn_volver_gameover.is_clicked(event) and len(self.iniciales_input) != 3:
                        pygame.mixer.music.stop()
                        self.game_state = 'MENU'
                        return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: 
                    if len(self.iniciales_input) == 3:
                        BOTON_SOUND.play()
                        guardar_y_ordenar_puntaje(self.iniciales_input, self.score)
                        pygame.mixer.music.stop()
                        self.game_state = 'MENU'
                        return
                elif event.key == pygame.K_BACKSPACE:
                    self.iniciales_input = self.iniciales_input[:-1]
                elif len(self.iniciales_input) < 3 and event.unicode.isalpha():
                    self.iniciales_input += event.unicode.upper()
        
        self.screen.blit(FONDO_GAMEOVER_IMG, (0, 0))
        mostrar_mensaje(self.screen, ":( PERDISTE!", fuente_grande, ROJO_TEXTO, (ANCHO // 2, ALTO // 2 - 150))
        mostrar_mensaje(self.screen, f"Puntaje Final: {self.score}", fuente_grande, BLANCO, (ANCHO // 2, ALTO // 2 - 80))
        mostrar_mensaje(self.screen, "Ingresa tus 3 iniciales:", fuente, BLANCO, (ANCHO // 2, ALTO // 2 + 10))
        pygame.draw.rect(self.screen, BLANCO, self.input_rect, 2)
        mostrar_mensaje(self.screen, self.iniciales_input, fuente_grande, AMARILLO_CLARO, self.input_rect.center)
        
        if len(self.iniciales_input) == 3:
            mostrar_mensaje(self.screen, "Presiona ENTER para guardar", fuente_puntaje, NEGRO, (ANCHO // 2, ALTO // 2 + 140))
        else:
            self.btn_volver_gameover.draw(self.screen)
        
        self.dibujar_ui_volumen() 
        pygame.display.flip()
        self.clock.tick(30)
        
    def run_playing(self):
        """Bucle principal del juego"""
        current_time = pygame.time.get_ticks() 
        self.score += self.difficulty_settings['score_mult'] #!hay partidas q no toma el score_mult (dudoso)
        
        # eventos 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.manejar_clic_volumen(event.pos) 
            if event.type == pygame.KEYDOWN:
                self.player.check_clown_truco(event.unicode)

        # actualización de timers
        self.player.update_timers(current_time)
        if self.slow_mo and current_time - self.slow_mo_start_time > SLOWMO_DURATION:
            self.slow_mo = False

        # Movimiento 
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        
        speed_multiplier = 0.4 if self.slow_mo else 1.0
        for enemigo in self.enemies:
            enemigo.move(speed_multiplier)
            
        for powerup in self.powerups:
            powerup.move() # Solo se mueve si es 'slowmo'

        # Spawn de enemigos y power-ups 
        self.contador_spawn_enemigo += 1
        if self.contador_spawn_enemigo >= self.difficulty_settings['max_spawn']:
            self.contador_spawn_enemigo = 0
            for _ in range(random.randint(1, 2)):
                self.enemies.append(Enemigo(self.difficulty_settings['vel_min'], self.difficulty_settings['vel_max']))

        self.contador_spawn_powerup += 1
        if self.contador_spawn_powerup >= POWERUP_SPAWN_RATE:
            self.contador_spawn_powerup = 0
            self.powerups.append(PowerUp())

        # colisiones
        for enemigo in self.enemies[:]:
            if self.player.rect.colliderect(enemigo.rect):
                self.enemies.remove(enemigo) # El enemigo desaparece cuando choca
                if self.player.get_hit(): # si el jugador muere
                    pygame.mixer.music.stop()
                    try:
                        pygame.mixer.music.load(MUSICA_GAMEOVER)
                        pygame.mixer.music.set_volume(self.current_music_volume) 
                        pygame.mixer.music.play(-1)
                    except pygame.error as e: print(f"No se pudo cargar la música de game over: {e}")
                    
                    self.game_state = 'GAME_OVER'
                    self.iniciales_input = "" # Reiniciar el input
                    return
            elif enemigo.is_offscreen():
                self.enemies.remove(enemigo)

        for powerup in self.powerups[:]:
            if self.player.rect.colliderect(powerup.rect):
                if powerup.type == 'health':
                    self.player.add_life()
                elif powerup.type == 'shield':
                    self.player.activate_shield(current_time)
                elif powerup.type == 'slowmo':
                    self.slow_mo = True
                    self.slow_mo_start_time = current_time
                    POWERUP_SOUND.play()
                self.powerups.remove(powerup)

        # Renderizado 
        self.screen.blit(FONDO_JUEGO_IMG, (0, 0))
        
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        self.player.draw(self.screen, current_time)
        
        for enemigo in self.enemies:
            enemigo.draw(self.screen)
            
        # interfaz del Juego
        mostrar_mensaje(self.screen, f"Vidas: {self.player.lives}", fuente, BLANCO, (ANCHO - 100, 30))
        mostrar_mensaje(self.screen, f"Puntaje: {self.score}", fuente, BLANCO, (120, 30))
        self.dibujar_ui_volumen() 
        
        if self.slow_mo:
            tiempo_restante = (SLOWMO_DURATION - (current_time - self.slow_mo_start_time)) // 1000 + 1
            mostrar_mensaje(self.screen, f"SLOW-MO: {tiempo_restante}s", fuente_pequena, NARANJA_TEXTO, (120, 60))

        pygame.display.flip()
        self.clock.tick(60)

    # Bucle Principal 
    def run(self):
        """El bucle principal que maneja los estados del juego."""
        while self.running:
            if self.game_state == 'MENU':
                self.run_menu()
            elif self.game_state == 'DIFFICULTY':
                self.run_difficulty()
            elif self.game_state == 'SCORES':
                self.run_scores()
            elif self.game_state == 'PLAYING':
                self.run_playing()
            elif self.game_state == 'GAME_OVER':
                self.run_game_over()
        
        pygame.quit()
        sys.exit()

#!-------------------------------------------------------------
#!  Iniciar juego
#! ----------------------------------------------------------------
if __name__ == "__main__":
    inicializar_csv() 
    game = Game()
    game.run()