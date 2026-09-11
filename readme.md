CertiChain 🔐⛓️

CertiChain est une application de certification numérique basée sur la blockchain Ethereum/EVM.
Elle permet à une institution d'émettre, vérifier et révoquer des certificats de manière transparente et infalsifiable grâce à un smart contract Solidity.

Le projet combine Django, Web3.py, Solidity et Hardhat afin de créer une application Web3 full-stack.

🎯 Problématique

Les diplômes et certificats numériques peuvent être falsifiés ou difficiles à vérifier.

Une institution qui souhaite vérifier un certificat doit généralement contacter l'organisme émetteur ou se fier à un document numérique qui peut avoir été modifié.

CertiChain propose une solution basée sur la blockchain :

chaque certificat possède un identifiant unique ;
son empreinte cryptographique est enregistrée sur la blockchain ;
l'existence et l'état du certificat peuvent être vérifiés ;
un certificat peut être révoqué par l'institution émettrice ;
les opérations importantes sont enregistrées dans des événements blockchain.
💡 Solution

CertiChain sépare les données sensibles du registre blockchain.

Le document ou les informations complètes du certificat peuvent être conservés hors chaîne, tandis que son hash cryptographique est enregistré dans le smart contract.

Lorsqu'un certificat doit être vérifié, son hash peut être comparé à celui enregistré sur la blockchain.

Architecture
                    ┌─────────────────────┐
                    │       Utilisateur   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       Django        │
                    │     Application     │
                    └──────────┬──────────┘
                               │
                               │ Web3.py
                               ▼
                    ┌─────────────────────┐
                    │     Smart Contract  │
                    │     CertiChain      │
                    │      Solidity       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     EVM Blockchain  │
                    │       Hardhat       │
                    │      / Sepolia      │
                    └─────────────────────┘

✨ Fonctionnalités
Émission d'un certificat

Une institution autorisée peut enregistrer un certificat avec :

un identifiant unique ;
le hash du certificat ;
le nom du bénéficiaire ;
le titre du certificat ;
le nom de l'institution émettrice ;
l'adresse Ethereum de l'émetteur ;
la date d'émission.
Vérification

Un utilisateur peut rechercher un certificat à partir de son identifiant.

Le smart contract retourne notamment :

existence du certificat ;
hash ;
bénéficiaire ;
titre ;
institution ;
adresse de l'émetteur ;
date d'émission ;
statut de révocation.
Révocation

L'institution propriétaire peut révoquer un certificat.

La révocation est enregistrée directement dans l'état du smart contract.

🔗 Smart Contract

Le contrat principal est :

contracts/CertiChain.sol

Fonctions principales
issueCertificate(...)


Permet d'émettre un nouveau certificat.

verifyCertificate(...)


Permet de vérifier un certificat.

revokeCertificate(...)


Permet de révoquer un certificat.

certificateExists(...)


Permet de vérifier l'existence d'un certificat.

🔐 Sécurité et contrôle d'accès

Le smart contract utilise un mécanisme Ownable.

Le compte ayant déployé le contrat devient le propriétaire.

Seul ce compte peut :

Émettre un certificat
        │
        ▼
issueCertificate()

Révoquer un certificat
        │
        ▼
revokeCertificate()


Les autres utilisateurs peuvent consulter les informations publiques du certificat.

🧱 Technologies
Blockchain
Ethereum / EVM
Solidity 0.8.20
Hardhat 3
Viem
Backend
Python
Django
Web3.py
Base de données
SQLite pour le développement
Django ORM
Développement
Node.js
npm
Git / GitHub
📁 Structure du projet
certichain/
│
├── contracts/
│   └── CertiChain.sol
│
├── scripts/
│   └── deploy.ts
│
├── test/
│   └── CertiChain.ts
│
├── certificates/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── blockchain.py
│
├── certichain/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── manage.py
├── hardhat.config.ts
├── package.json
├── requirements.txt
├── .env.example
└── README.md

🚀 Installation
Prérequis

Installer :

Node.js
npm
Python 3
Git

Vérifier les installations :

node --version
npm --version
python --version
git --version

1. Cloner le projet
git clone https://github.com/VOTRE-USERNAME/certichain.git
cd certichain

2. Installer les dépendances Node.js
npm install

3. Créer l'environnement Python

Linux/macOS :

python3 -m venv venv
source venv/bin/activate


Windows :

python -m venv venv
venv\Scripts\activate


Installer les dépendances :

pip install -r requirements.txt

⚙️ Configuration

Créer un fichier :

.env


à partir de :

.env.example


Exemple :

BLOCKCHAIN_RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=
DEPLOYER_PRIVATE_KEY=


Ne jamais publier .env sur GitHub.

⛓️ Utilisation avec Hardhat
1. Compiler le smart contract
npx hardhat compile

2. Démarrer la blockchain locale

Dans un premier terminal :

npx hardhat node


Hardhat démarre une blockchain EVM locale sur :

http://127.0.0.1:8545


Des comptes de développement sont automatiquement créés et financés en ETH de test.

3. Déployer CertiChain

Dans un deuxième terminal :

npx hardhat run scripts/deploy.ts --network localhost


Le script affiche l'adresse du contrat :

Smart Contract déployé avec succès !

Adresse :
0x...


Copier cette adresse dans .env :

CONTRACT_ADDRESS=0x...

🧪 Tests

Compiler les contrats :

npx hardhat compile


Lancer les tests :

npx hardhat test


Les tests doivent notamment vérifier :

émission d'un certificat ;
récupération d'un certificat ;
refus d'un identifiant déjà utilisé ;
révocation ;
refus d'une révocation multiple ;
contrôle d'accès du propriétaire.
🐍 Connexion Django → Blockchain

CertiChain utilise Web3.py pour communiquer avec le smart contract.

Architecture :

Django
   │
   │ Web3.py
   ▼
JSON-RPC
   │
   ▼
Hardhat
   │
   ▼
CertiChain.sol


Une opération de lecture, comme verifyCertificate, peut être effectuée sans signer une transaction.

Une opération d'écriture, comme issueCertificate, nécessite une transaction signée par le compte autorisé.

🔄 Exemple de flux d'émission
1. L'administrateur saisit les informations
                │
                ▼
2. Django calcule / récupère le hash
                │
                ▼
3. Django appelle issueCertificate()
                │
                ▼
4. Web3.py construit et signe la transaction
                │
                ▼
5. Hardhat exécute le smart contract
                │
                ▼
6. Certificat enregistré on-chain
                │
                ▼
7. Transaction Hash retourné à Django

🔎 Exemple de vérification
Utilisateur
    │
    │ ID du certificat
    ▼
Django
    │
    │ verifyCertificate()
    ▼
CertiChain
    │
    ├── Existe ?
    ├── Hash
    ├── Bénéficiaire
    ├── Institution
    ├── Date
    └── Révoqué ?
    │
    ▼
Résultat affiché à l'utilisateur

🌐 Déploiement sur Testnet

Pour la démonstration finale, CertiChain peut être déployé sur un réseau EVM de test tel que Sepolia.

La configuration utilise alors un endpoint RPC :

SEPOLIA_RPC_URL=
SEPOLIA_PRIVATE_KEY=


⚠️ Utiliser uniquement un portefeuille de test dédié au développement.

Ne jamais utiliser une clé privée contenant des fonds réels.

📊 État du projet
Fonctionnalité	État
Smart contract Solidity	✅
Émission de certificats	✅
Vérification	✅
Révocation	✅
Contrôle d'accès	✅
Backend Django	✅
Communication Web3.py	✅
Blockchain locale Hardhat	✅
Tests automatisés	🔄
Déploiement Sepolia	🔄
Vérification du contrat	🔄
Documentation	✅
🎓 Objectif du projet

CertiChain a été développé comme projet final pour démontrer la compréhension des technologies Ethereum et EVM.

Le projet met en pratique plusieurs concepts fondamentaux :

Smart contracts ;
Solidity ;
EVM ;
transactions blockchain ;
signatures cryptographiques ;
gas ;
adresses Ethereum ;
événements Solidity ;
lecture de données on-chain ;
écriture de données on-chain ;
hash cryptographique ;
contrôle d'accès ;
interaction entre une application Web2 et une blockchain EVM.
🎥 Démonstration

La démonstration du projet présente le flux suivant :

Créer un certificat
        ↓
Enregistrer sur la blockchain
        ↓
Afficher la transaction
        ↓
Vérifier le certificat
        ↓
Révoquer le certificat
        ↓
Vérifier à nouveau
        ↓
Afficher "Certificat révoqué"


La démonstration montre également le smart contract et son interaction avec l'application Django.

👨‍💻 Auteur

Votre nom

Projet : CertiChain

Technologies : Django · Web3.py · Solidity · Hardhat · Ethereum/EVM

📄 Licence

Ce projet est distribué sous licence MIT.