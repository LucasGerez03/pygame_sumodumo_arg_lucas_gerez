import pygame
import csv
import os
from settings import PUNTAJES_FILE

# Funciones Auxiliar 
def mostrar_mensaje(surface, texto: str, fuente_render: pygame.font.Font, color: tuple, pos_centro: tuple):
    """Dibuja texto centrado en la superficie dada."""
    render = fuente_render.render(texto, True, color)
    surface.blit(render, render.get_rect(center=pos_centro))

def inicializar_csv():
    """Crea el archivo CSV con cabeceras si no existe."""
    if not os.path.exists(PUNTAJES_FILE):
        try:
            with open(PUNTAJES_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['INICIALES', 'PUNTAJE'])
        except IOError as e: print(f"Error al inicializar el archivo CSV: {e}")

    
def guardar_y_ordenar_puntaje(iniciales, puntaje):
    """Añade un puntaje y reescribe el CSV ordenado."""
    puntajes = []
    try:
        with open(PUNTAJES_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            cabecera = next(reader) 
            for fila in reader:
                try: puntajes.append((fila[0], int(fila[1])))
                except (ValueError, IndexError): continue
        
        puntajes.append((iniciales, puntaje))
        puntajes.sort(key=lambda x: x[1], reverse=True)
        
        with open(PUNTAJES_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(cabecera)
            writer.writerows(puntajes)
    except IOError as e: print(f"Error al guardar y ordenar puntajes: {e}")
    except FileNotFoundError:
        inicializar_csv()
        guardar_y_ordenar_puntaje(iniciales, puntaje)
            
    
def leer_puntajes():
    """Lee y devuelve la lista de puntajes."""
    puntajes_leidos = []
    try:
        with open(PUNTAJES_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # Saltar cabecera
            for fila in reader:
                try: puntajes_leidos.append((fila[0], int(fila[1])))
                except (ValueError, IndexError): continue
    except FileNotFoundError:
        inicializar_csv()
    return puntajes_leidos
