#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar las URLs disponibles en el backend
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver
from django.conf import settings

def show_urls(urlconf, prefix=''):
    """Muestra todas las URLs disponibles"""
    try:
        resolver = get_resolver(urlconf)
        urls = []
        
        for pattern in resolver.url_patterns:
            try:
                if isinstance(pattern, URLResolver):
                    urls.extend(show_urls(pattern.urlconf_name, prefix + str(pattern.pattern)))
                elif isinstance(pattern, URLPattern):
                    urls.append((prefix + str(pattern.pattern), pattern.name))
            except Exception as e:
                continue
        
        return urls
    except Exception as e:
        return []

def main():
    print("\n" + "="*80)
    print("URLS DISPONIBLES EN EL BACKEND".center(80))
    print("="*80 + "\n")
    
    try:
        urls = show_urls(settings.ROOT_URLCONF)
        
        # Filtrar URLs de API
        api_urls = [url for url in urls if 'api' in url[0].lower()]
        
        print(f"{'URL':<60} {'Nombre':<30}")
        print("-" * 90)
        
        for url, name in sorted(api_urls):
            print(f"{url:<60} {name or 'N/A':<30}")
        
        print(f"\nTotal de URLs de API: {len(api_urls)}\n")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

