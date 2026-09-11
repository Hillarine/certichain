# test_blockchain.py
import os
import django
from dotenv import load_dotenv

# Charger l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certichain.settings')
django.setup()

from certificates.blockchain import get_blockchain_service
from django.conf import settings

print("=== DIAGNOSTIC BLOCKCHAIN ===")
print(f"1. RPC URL configurée : {settings.BLOCKCHAIN_RPC_URL}")
print(f"2. Adresse Contrat : {settings.CONTRACT_ADDRESS}")
print(f"3. Clé privée présente : {'OUI' if settings.DEPLOYER_PRIVATE_KEY else 'NON'}")

service = get_blockchain_service()
print(f"4. Nœud Hardhat connecté : {'✅ OUI' if service.is_connected else '❌ NON'}")

if service.is_connected and service.account:
    print(f"5. Compte émetteur (Wallet) : {service.account.address}")
    balance = service.w3.eth.get_balance(service.account.address)
    print(f"6. Solde du compte : {service.w3.from_wei(balance, 'ether')} ETH")

    # Test d'écriture on-chain
    try:
        print("\n⏳ Test d'enregistrement d'un certificat test...")
        res = service.issue_certificate(
            cert_id="TEST-001",
            cert_hash="0x" + "a" * 64,
            recipient_name="Jean Dupont",
            title="Diplôme Test",
            issuer_name="Université Test"
        )
        print(f"✅ SUCCÈS ! Tx Hash : {res['tx_hash']}")
        print(f"✅ Bloc numéro : {res['block_number']}")
        
        # Test de lecture
        verification = service.verify_certificate("TEST-001")
        print(f"✅ Vérification on-chain : {verification}")
    except Exception as e:
        print(f"❌ ERREUR lors de l'appel au contrat : {e}")