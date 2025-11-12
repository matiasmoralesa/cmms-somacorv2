#!/usr/bin/env python
"""
Script para generar una SECRET_KEY segura para Django
"""
from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    secret_key = get_random_secret_key()
    print("=" * 80)
    print("🔐 SECRET_KEY GENERADA PARA DJANGO")
    print("=" * 80)
    print("\nCopia esta clave y agrégala a tu archivo .env:")
    print(f"\nDJANGO_SECRET_KEY={secret_key}")
    print("\n⚠️  IMPORTANTE:")
    print("   - Nunca compartas esta clave")
    print("   - Nunca la subas al repositorio")
    print("   - Usa una clave diferente para cada ambiente")
    print("=" * 80)
