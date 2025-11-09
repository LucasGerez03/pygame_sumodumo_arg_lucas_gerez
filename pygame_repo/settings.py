import pygame
import random
import sys
import csv
import os

# --- Configuración de la Ventana ---
ANCHO, ALTO = 800, 500
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("SUMO DUMO ARG")

# --- Colores ---
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS = (100, 100, 100)
# Colores del juego
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
# Colores de Power-ups
VIOLETA = (148, 0, 211)
AZUL = (0, 150, 255)
NARANJA = (255, 165, 0)
# Colores de Botones
VERDE_CLARO = (0, 200, 0)
AMARILLO = (255, 255, 0)
AMARILLO_CLARO = (200, 200, 0)
ROJO_CLARO = (200, 0, 0)

# --- Configuración del Juego (Base) ---
JUGADOR_ANCHO = 40
JUGADOR_ALTO = 40
ENEMIGO_ANCHO = 30
ENEMIGO_ALTO = 30
POWERUP_SIZE = 20
POWERUP_VEL = 2

# --- Constantes de Efectos ---
INMORTAL_DURATION = 5000
SLOWMO_DURATION = 5000
POWERUP_SPAWN_RATE = 420

# --- Archivo de Puntajes ---
PUNTAJES_FILE = 'puntajes.csv'

