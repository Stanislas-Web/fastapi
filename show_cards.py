#!/usr/bin/env python3
"""
Script simple pour afficher toutes les cartes de test disponibles
"""
from app.utils.mock_data import MOCK_CARDS, MOCK_WEBHOOKS
import json

print("=" * 70)
print("🎴 CARTES DE TEST DISPONIBLES")
print("=" * 70)
print()

for i, card in enumerate(MOCK_CARDS, 1):
    print(f"📇 CARTE {i}")
    print(f"   cardId:        {card['cardId']}")
    print(f"   panAlias:     {card['panAlias']}")
    print(f"   status:       {card['status']}")
    print(f"   cardType:     {card['cardType']}")
    print(f"   accountId:    {card['accountId']}")
    print()

print("=" * 70)
print("📨 WEBHOOKS DE TEST DISPONIBLES")
print("=" * 70)
print()

for event_name, webhook in MOCK_WEBHOOKS.items():
    print(f"🔔 {event_name.upper().replace('_', ' ')}")
    print(f"   cardId:       {webhook['data']['cardId']}")
    print(f"   panAlias:     {webhook['data']['panAlias']}")
    print(f"   event:        {webhook['event']}")
    print(f"   webhookId:    {webhook['webhookId']}")
    print()

print("=" * 70)
print("📋 RÉSUMÉ RAPIDE")
print("=" * 70)
print()
for card in MOCK_CARDS:
    print(f"   • cardId={card['cardId']:5} | panAlias={card['panAlias']:20} | {card['status']:8} | {card['cardType']}")
print()
print("=" * 70)

