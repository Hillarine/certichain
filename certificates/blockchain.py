import os
from web3 import Web3
from django.conf import settings

CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "_certId", "type": "string"},
            {"internalType": "bytes32", "name": "_certHash", "type": "bytes32"},
            {"internalType": "string", "name": "_recipientName", "type": "string"},
            {"internalType": "string", "name": "_title", "type": "string"},
            {"internalType": "string", "name": "_issuerName", "type": "string"}
        ],
        "name": "issueCertificate",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_certId", "type": "string"},
            {"internalType": "string", "name": "_reason", "type": "string"}
        ],
        "name": "revokeCertificate",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_certId", "type": "string"}
        ],
        "name": "verifyCertificate",
        "outputs": [
            {"internalType": "bool", "name": "exists", "type": "bool"},
            {"internalType": "bytes32", "name": "certHash", "type": "bytes32"},
            {"internalType": "string", "name": "recipientName", "type": "string"},
            {"internalType": "string", "name": "title", "type": "string"},
            {"internalType": "string", "name": "issuerName", "type": "string"},
            {"internalType": "address", "name": "issuer", "type": "address"},
            {"internalType": "uint256", "name": "issuedAt", "type": "uint256"},
            {"internalType": "bool", "name": "isRevoked", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_certId", "type": "string"}
        ],
        "name": "certificateExists",
        "outputs": [
            {"internalType": "bool", "name": "", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

class BlockchainService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_RPC_URL))
        self.contract_address = settings.CONTRACT_ADDRESS
        self.private_key = settings.DEPLOYER_PRIVATE_KEY
        self.chain_id = getattr(settings, 'CHAIN_ID', 31337)

        if self.contract_address and self.w3.is_address(self.contract_address):
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contract_address),
                abi=CONTRACT_ABI
            )
        else:
            self.contract = None

    @property
    def is_connected(self):
        try:
            return self.w3.is_connected()
        except Exception:
            return False

    @property
    def account(self):
        if self.private_key:
            return self.w3.eth.account.from_key(self.private_key)
        return None

    def issue_certificate(self, cert_id, cert_hash, recipient_name, title, issuer_name):
        if not self.contract:
            raise Exception("Smart contract non configuré ou adresse invalide.")

        if not self.is_connected:
            raise Exception("Connexion au nœud RPC impossible.")

        account = self.account
        if not account:
            raise Exception("Clé privée non trouvée dans .env.")

        # Convertir cert_hash en exactement 32 bytes
        clean_hash = cert_hash.replace("0x", "")
        if len(clean_hash) < 64:
            clean_hash = clean_hash.ljust(64, '0')
        elif len(clean_hash) > 64:
            clean_hash = clean_hash[:64]
        cert_hash_bytes = bytes.fromhex(clean_hash)

        nonce = self.w3.eth.get_transaction_count(account.address)

        # Construire la transaction
        tx = self.contract.functions.issueCertificate(
            cert_id,
            cert_hash_bytes,
            recipient_name,
            title,
            issuer_name
        ).build_transaction({
            'from': account.address,
            'chainId': self.chain_id,
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': nonce,
        })

        # Signer et envoyer
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        
        # Compatibilité versions Web3.py (raw_transaction vs rawTransaction)
        raw_tx = getattr(signed_tx, 'raw_transaction', None) or getattr(signed_tx, 'rawTransaction', None)
        tx_hash = self.w3.eth.send_raw_transaction(raw_tx)

        # Attendre confirmation du bloc
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

        return {
            'tx_hash': receipt.transactionHash.hex(),
            'block_number': receipt.blockNumber,
            'gas_used': receipt.gasUsed,
            'status': receipt.status,
            'from': account.address,
        }

    def verify_certificate(self, cert_id):
        if not self.contract:
            return {'exists': False, 'error': 'Contrat non configuré'}

        try:
            result = self.contract.functions.verifyCertificate(cert_id).call()
            return {
                'exists': result[0],
                'cert_hash': '0x' + result[1].hex() if result[1] else '',
                'recipient_name': result[2],
                'title': result[3],
                'issuer_name': result[4],
                'issuer_address': result[5],
                'issued_at': result[6],
                'is_revoked': result[7],
            }
        except Exception as e:
            return {'exists': False, 'error': str(e)}

    def revoke_certificate(self, cert_id, reason):
        if not self.contract:
            raise Exception("Smart contract non configuré")

        account = self.account
        nonce = self.w3.eth.get_transaction_count(account.address)

        tx = self.contract.functions.revokeCertificate(
            cert_id,
            reason
        ).build_transaction({
            'from': account.address,
            'chainId': self.chain_id,
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': nonce,
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        raw_tx = getattr(signed_tx, 'raw_transaction', None) or getattr(signed_tx, 'rawTransaction', None)
        tx_hash = self.w3.eth.send_raw_transaction(raw_tx)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

        return {
            'tx_hash': receipt.transactionHash.hex(),
            'block_number': receipt.blockNumber,
            'status': receipt.status,
        }

def get_blockchain_service():
    return BlockchainService()