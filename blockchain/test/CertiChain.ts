import { describe, it } from "node:test";
import assert from "node:assert/strict";
import hre from "hardhat";

describe("CertiChain", async () => {
  async function deployCertiChain() {
    const { viem } = await hre.network.connect();

    const [owner, otherAccount] = await viem.getWalletClients();
    const certiChain = await viem.deployContract("CertiChain");

    return {
      certiChain,
      owner,
      otherAccount,
    };
  }

  describe("Deployment", async () => {
    it("should set the deployer as owner", async () => {
      const { certiChain, owner } = await deployCertiChain();

      const contractOwner = await certiChain.read.owner();

      assert.equal(
        contractOwner.toLowerCase(),
        owner.account.address.toLowerCase()
        );
    });

    it("should start with zero certificates", async () => {
      const { certiChain } = await deployCertiChain();

      assert.equal(
        await certiChain.read.totalCertificates(),
        0n
      );

      assert.equal(
        await certiChain.read.totalRevoked(),
        0n
      );
    });
  });

  describe("Certificate issuance", async () => {
    it("should issue a certificate", async () => {
      const { certiChain } = await deployCertiChain();

      const certId = "CERT-001";

      const certHash =
        "0x1234567890123456789012345678901234567890123456789012345678901234";

      await certiChain.write.issueCertificate([
        certId,
        certHash as `0x${string}`,
        "Jean Dupont",
        "Bachelor en Informatique",
        "Université de Cotonou",
      ]);

      const result =
        await certiChain.read.verifyCertificate([certId]);

      assert.equal(result[0], true);
      assert.equal(result[1], certHash);
      assert.equal(result[2], "Jean Dupont");
      assert.equal(result[3], "Bachelor en Informatique");
      assert.equal(result[4], "Université de Cotonou");
      assert.equal(result[7], false);

      assert.equal(
        await certiChain.read.totalCertificates(),
        1n
      );
    });

    it("should reject duplicate certificate IDs", async () => {
      const { certiChain } = await deployCertiChain();

      const certId = "CERT-DUPLICATE";

      const certHash =
        "0x1111111111111111111111111111111111111111111111111111111111111111";

      await certiChain.write.issueCertificate([
        certId,
        certHash as `0x${string}`,
        "Jean Dupont",
        "Blockchain",
        "CertiChain",
      ]);

      await assert.rejects(
        async () => {
          await certiChain.write.issueCertificate([
            certId,
            certHash as `0x${string}`,
            "Another Person",
            "Another Title",
            "Another Institution",
          ]);
        },
        /Certificate ID already exists/
      );
    });

    it("should reject an empty certificate ID", async () => {
      const { certiChain } = await deployCertiChain();

      const certHash =
        "0x2222222222222222222222222222222222222222222222222222222222222222";

      await assert.rejects(
        async () => {
          await certiChain.write.issueCertificate([
            "",
            certHash as `0x${string}`,
            "Jean Dupont",
            "Blockchain",
            "CertiChain",
          ]);
        },
        /Certificate ID cannot be empty/
      );
    });

    it("should reject an empty certificate hash", async () => {
      const { certiChain } = await deployCertiChain();

      await assert.rejects(
        async () => {
          await certiChain.write.issueCertificate([
            "CERT-NO-HASH",
            "0x0000000000000000000000000000000000000000000000000000000000000000",
            "Jean Dupont",
            "Blockchain",
            "CertiChain",
          ]);
        },
        /Certificate hash cannot be empty/
      );
    });
  });

  describe("Certificate verification", async () => {
    it("should return false for a certificate that does not exist", async () => {
      const { certiChain } = await deployCertiChain();

      const result =
        await certiChain.read.verifyCertificate([
          "CERT-DOES-NOT-EXIST",
        ]);

      assert.equal(result[0], false);
      assert.equal(result[1], `0x${"0".repeat(64)}`);
      assert.equal(result[2], "");
      assert.equal(result[3], "");
      assert.equal(result[4], "");
      assert.equal(
        result[5],
        "0x0000000000000000000000000000000000000000"
      );
      assert.equal(result[6], 0n);
      assert.equal(result[7], false);
    });

    it("should confirm that an existing certificate exists", async () => {
      const { certiChain } = await deployCertiChain();

      const certId = "CERT-VERIFY";

      const certHash =
        "0x3333333333333333333333333333333333333333333333333333333333333333";

      await certiChain.write.issueCertificate([
        certId,
        certHash as `0x${string}`,
        "Marie Koffi",
        "Master Informatique",
        "CertiChain University",
      ]);

      assert.equal(
        await certiChain.read.certificateExists([certId]),
        true
      );
    });
  });

  describe("Certificate revocation", async () => {
    it("should revoke an existing certificate", async () => {
      const { certiChain } = await deployCertiChain();

      const certId = "CERT-REVOKE";

      const certHash =
        "0x4444444444444444444444444444444444444444444444444444444444444444";

      await certiChain.write.issueCertificate([
        certId,
        certHash as `0x${string}`,
        "Paul Doe",
        "Licence Informatique",
        "CertiChain University",
      ]);

      await certiChain.write.revokeCertificate([
        certId,
        "Certificate issued by mistake",
      ]);

      const result =
        await certiChain.read.verifyCertificate([certId]);

      assert.equal(result[0], true);
      assert.equal(result[7], true);

      assert.equal(
        await certiChain.read.totalRevoked(),
        1n
      );
    });

    it("should reject revocation of a certificate that does not exist", async () => {
      const { certiChain } = await deployCertiChain();

      await assert.rejects(
        async () => {
          await certiChain.write.revokeCertificate([
            "CERT-NOT-EXIST",
            "Unknown certificate",
          ]);
        },
        /Certificate does not exist/
      );
    });

    it("should reject double revocation", async () => {
      const { certiChain } = await deployCertiChain();

      const certId = "CERT-DOUBLE-REVOKE";

      const certHash =
        "0x6666666666666666666666666666666666666666666666666666666666666666";

      await certiChain.write.issueCertificate([
        certId,
        certHash as `0x${string}`,
        "Paul Doe",
        "Licence",
        "CertiChain",
      ]);

      await certiChain.write.revokeCertificate([
        certId,
        "First revocation",
      ]);

      await assert.rejects(
        async () => {
          await certiChain.write.revokeCertificate([
            certId,
            "Second revocation",
          ]);
        },
        /Certificate is already revoked/
      );
    });
  });

  describe("Access control", async () => {
    it("should reject certificate issuance from a non-owner account", async () => {
        const { viem } = await hre.network.connect();

      const { certiChain, otherAccount } =
        await deployCertiChain();

      const unauthorizedContract =
        await viem.getContractAt(
          "CertiChain",
          certiChain.address,
          {
            client: {
              wallet: otherAccount,
            },
          }
        );

      const certHash =
        "0x7777777777777777777777777777777777777777777777777777777777777777";

      await assert.rejects(
        async () => {
          await unauthorizedContract.write.issueCertificate([
            "CERT-UNAUTHORIZED",
            certHash as `0x${string}`,
            "Unauthorized User",
            "Blockchain",
            "Fake Institution",
          ]);
        },
        /Ownable: caller is not the owner/
      );
    });

    it("should reject certificate revocation from a non-owner account", async () => {
        const { viem } = await hre.network.connect();

      const { certiChain, otherAccount } =
        await deployCertiChain();

      await certiChain.write.issueCertificate([
        "CERT-UNAUTHORIZED-REVOKE",
        "0x8888888888888888888888888888888888888888888888888888888888888888",
        "Jean Dupont",
        "Blockchain",
        "CertiChain",
      ]);

      const unauthorizedContract =
        await viem.getContractAt(
          "CertiChain",
          certiChain.address,
          {
            client: {
              wallet: otherAccount,
            },
          }
        );

      await assert.rejects(
        async () => {
          await unauthorizedContract.write.revokeCertificate([
            "CERT-UNAUTHORIZED-REVOKE",
            "Unauthorized revocation",
          ]);
        },
        /Ownable: caller is not the owner/
      );
    });
  });
});