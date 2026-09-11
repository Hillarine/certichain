import { network } from "hardhat";

const { viem } = await network.connect();

async function main() {
  console.log("Déploiement de CertiChain...");

  const certiChain = await viem.deployContract("CertiChain");

  console.log("=========================================");
  console.log("Smart Contract déployé avec succès !");
  console.log("Adresse :", certiChain.address);
  console.log("=========================================");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
