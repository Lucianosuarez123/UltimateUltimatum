#!/usr/bin/env python3
"""
Convierte banderas TGA con compresión RLE a formato sin compresión
para compatibilidad con Victoria 2
"""
from PIL import Image
import os
import sys

def convert_tga_to_uncompressed(input_path, output_path):
    """Convierte un TGA RLE a TGA sin compresión compatible con Victoria 2"""
    try:
        img = Image.open(input_path)
        # Convertir a RGB si es necesario (Victoria 2 prefiere 24-bit)
        if img.mode == 'RGBA':
            # Crear fondo blanco para el canal alpha
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Guardar como TGA sin compresión, orientación bottom-left (origin=bottom-left)
        img.save(output_path, format='TGA', compression='raw')
        return True
    except Exception as e:
        print(f"Error procesando {input_path}: {e}")
        return False

def main():
    flags_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"\nDirectorio: {flags_dir}\n")
    
    # Listar archivos TGA con RLE
    rle_files = []
    for filename in os.listdir(flags_dir):
        if not filename.endswith('.tga') or filename.startswith('flagfiles'):
            continue
        
        filepath = os.path.join(flags_dir, filename)
        try:
            with open(filepath, 'rb') as f:
                f.seek(2)
                image_type = ord(f.read(1))
                # Type 10 = RLE TrueColor, 9 = RLE ColorMapped, 11 = RLE BW
                if image_type in [9, 10, 11]:
                    rle_files.append(filename)
        except:
            continue
    
    print(f"Encontradas {len(rle_files)} banderas con RLE\n")
    
    if len(rle_files) == 0:
        print("No hay archivos para convertir.")
        return
    
    # Crear backup directory
    backup_dir = os.path.join(flags_dir, '_backup_rle')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Creado directorio de backup: {backup_dir}\n")
    
    converted = 0
    failed = 0
    
    for i, filename in enumerate(rle_files, 1):
        input_path = os.path.join(flags_dir, filename)
        backup_path = os.path.join(backup_dir, filename)
        
        # Hacer backup
        try:
            with open(input_path, 'rb') as src:
                with open(backup_path, 'wb') as dst:
                    dst.write(src.read())
        except Exception as e:
            print(f"Error haciendo backup de {filename}: {e}")
            failed += 1
            continue
        
        # Convertir
        if convert_tga_to_uncompressed(input_path, input_path):
            converted += 1
            if i % 100 == 0:
                print(f"Progreso: {i}/{len(rle_files)} archivos procesados...")
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"CONVERSIÓN COMPLETADA")
    print(f"{'='*60}")
    print(f"Convertidos exitosamente: {converted}")
    print(f"Errores: {failed}")
    print(f"Backups guardados en: {backup_dir}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
