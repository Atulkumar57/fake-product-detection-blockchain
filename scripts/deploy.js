const fs = require("fs");
const path = require("path");
const hre = require("hardhat");

async function main() {
  const Factory = await hre.ethers.getContractFactory("ProductVerification");
  const contract = await Factory.deploy();
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log("ProductVerification deployed to:", address);

  const out = path.join(__dirname, "..", "deployment.json");
  const artifact = await hre.artifacts.readArtifact("ProductVerification");
  fs.writeFileSync(
    out,
    JSON.stringify({ address, abi: artifact.abi, network: hre.network.name }, null, 2)
  );
  console.log("Wrote deployment.json");
}

main().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
