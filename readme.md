CertiChain

CertiChain est une application Web3 permettant aux institutions de créer, vérifier et révoquer des certificats numériques grâce à la blockchain Ethereum/EVM.

Fonctionnalités
Émission de certificats
Vérification des certificats
Révocation des certificats
Contrôle d'accès avec smart contract
Enregistrement des preuves sur blockchain
Interface web avec Django
Technologies
Solidity
Hardhat
Viem
Web3.py
Django
Ethereum / EVM
SQLite
Structure
certichain/
├── contracts/       # Smart contracts Solidity
├── scripts/         # Scripts de déploiement
├── test/            # Tests blockchain
├── certificates/    # Application Django
├── certichain/      # Configuration Django
├── manage.py
├── hardhat.config.ts
└── README.md

Installation
git clone https://github.com/Hillarine/certichain.git
cd certichain

npm install

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Blockchain locale

Compiler le smart contract :

npx hardhat compile


Démarrer la blockchain :

npx hardhat node


Dans un autre terminal :

npx hardhat run scripts/deploy.ts --network localhost

Tests
npx hardhat test

Configuration

Créer un fichier .env :

BLOCKCHAIN_RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=
DEPLOYER_PRIVATE_KEY=


Ne jamais publier .env ou une clé privée sur GitHub.

Objectif

CertiChain est un projet démontrant l'utilisation de Solidity, des smart contracts, des chaînes EVM et l'intégration d'une application Django avec une blockchain.

Auteur

Hillarine