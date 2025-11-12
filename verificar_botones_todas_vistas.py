"""
Script para verificar todos los botones en todas las vistas del proyecto
"""

import os
import re
from pathlib import Path

# Directorio de las vistas
VIEWS_DIR = "somacor_cmms/frontend/src/pages"

def extract_buttons_from_file(filepath):
    """Extrae todos los botones de un archivo"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar todos los componentes Button
    button_pattern = r'<Button[^>]*>(.*?)</Button>'
    buttons = re.findall(button_pattern, content, re.DOTALL)
    
    # Buscar onClick handlers
    onclick_pattern = r'onClick=\{([^}]+)\}'
    onclicks = re.findall(onclick_pattern, content)
    
    # Buscar funciones definidas
    function_pattern = r'const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>'
    functions = re.findall(function_pattern, content)
    
    return {
        'buttons': len(buttons),
        'onclicks': len(onclicks),
        'functions': functions,
        'has_buttons': len(buttons) > 0
    }

def main():
    print("\n" + "="*80)
    print("VERIFICACIÓN DE BOTONES EN TODAS LAS VISTAS")
    print("="*80 + "\n")
    
    views_path = Path(VIEWS_DIR)
    view_files = sorted(views_path.glob("*.tsx"))
    
    total_views = 0
    views_with_buttons = 0
    total_buttons = 0
    total_handlers = 0
    
    results = []
    
    for view_file in view_files:
        if view_file.name.endswith('.test.tsx'):
            continue
            
        total_views += 1
        view_name = view_file.name
        
        try:
            data = extract_buttons_from_file(view_file)
            
            if data['has_buttons']:
                views_with_buttons += 1
            
            total_buttons += data['buttons']
            total_handlers += data['onclicks']
            
            results.append({
                'name': view_name,
                'buttons': data['buttons'],
                'handlers': data['onclicks'],
                'functions': len(data['functions']),
                'status': '✅' if data['onclicks'] >= data['buttons'] else '⚠️'
            })
            
        except Exception as e:
            results.append({
                'name': view_name,
                'buttons': 0,
                'handlers': 0,
                'functions': 0,
                'status': '❌',
                'error': str(e)
            })
    
    # Ordenar por número de botones
    results.sort(key=lambda x: x['buttons'], reverse=True)
    
    # Mostrar resultados
    print(f"{'Vista':<40} {'Botones':<10} {'Handlers':<10} {'Funciones':<10} {'Estado':<10}")
    print("-" * 80)
    
    for result in results:
        print(f"{result['name']:<40} {result['buttons']:<10} {result['handlers']:<10} {result['functions']:<10} {result['status']:<10}")
    
    print("\n" + "="*80)
    print("RESUMEN")
    print("="*80)
    print(f"Total de vistas: {total_views}")
    print(f"Vistas con botones: {views_with_buttons}")
    print(f"Total de botones: {total_buttons}")
    print(f"Total de handlers: {total_handlers}")
    print(f"Cobertura: {(total_handlers/total_buttons*100) if total_buttons > 0 else 0:.1f}%")
    print()
    
    # Vistas que necesitan atención
    needs_attention = [r for r in results if r['status'] == '⚠️' and r['buttons'] > 0]
    if needs_attention:
        print("\n⚠️  VISTAS QUE NECESITAN ATENCIÓN:")
        for result in needs_attention:
            print(f"   - {result['name']}: {result['buttons']} botones, {result['handlers']} handlers")
    else:
        print("\n✅ TODAS LAS VISTAS CON BOTONES TIENEN HANDLERS")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
