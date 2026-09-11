// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Implémentation légère de Ownable sans dépendance externe
abstract contract Ownable {
    address private _owner;

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    constructor(address initialOwner) {
        require(initialOwner != address(0), "Ownable: new owner is the zero address");
        _transferOwnership(initialOwner);
    }

    modifier onlyOwner() {
        _checkOwner();
        _;
    }

    function owner() public view virtual returns (address) {
        return _owner;
    }

    function _checkOwner() internal view virtual {
        require(owner() == msg.sender, "Ownable: caller is not the owner");
    }

    function _transferOwnership(address newOwner) internal virtual {
        address oldOwner = _owner;
        _owner = newOwner;
        emit OwnershipTransferred(oldOwner, newOwner);
    }
}

contract CertiChain is Ownable {
    struct Certificate {
        string certId;
        bytes32 certHash;
        string recipientName;
        string title;
        string issuerName;
        address issuer;
        uint256 issuedAt;
        bool isRevoked;
        string revocationReason;
        uint256 revokedAt;
    }

    mapping(string => Certificate) private certificates;
    mapping(string => bool) private certificateExists_;
    
    uint256 public totalCertificates;
    uint256 public totalRevoked;

    event CertificateIssued(
        string indexed certId,
        address indexed issuer,
        bytes32 certHash
    );

    event CertificateRevoked(
        string indexed certId,
        address indexed revokedBy,
        string reason
    );

    constructor() Ownable(msg.sender) {}

    modifier onlyCertificateExists(string memory _certId) {
        require(certificateExists_[_certId], "Certificate does not exist");
        _;
    }

    function issueCertificate(
        string memory _certId,
        bytes32 _certHash,
        string memory _recipientName,
        string memory _title,
        string memory _issuerName
    ) external onlyOwner {
        require(!certificateExists_[_certId], "Certificate ID already exists");
        require(bytes(_certId).length > 0, "Certificate ID cannot be empty");
        require(_certHash != bytes32(0), "Certificate hash cannot be empty");

        certificates[_certId] = Certificate({
            certId: _certId,
            certHash: _certHash,
            recipientName: _recipientName,
            title: _title,
            issuerName: _issuerName,
            issuer: msg.sender,
            issuedAt: block.timestamp,
            isRevoked: false,
            revocationReason: "",
            revokedAt: 0
        });

        certificateExists_[_certId] = true;
        totalCertificates++;

        emit CertificateIssued(_certId, msg.sender, _certHash);
    }

    function revokeCertificate(
        string memory _certId,
        string memory _reason
    ) external onlyOwner onlyCertificateExists(_certId) {
        Certificate storage cert = certificates[_certId];
        require(!cert.isRevoked, "Certificate is already revoked");

        cert.isRevoked = true;
        cert.revocationReason = _reason;
        cert.revokedAt = block.timestamp;
        totalRevoked++;

        emit CertificateRevoked(_certId, msg.sender, _reason);
    }

    function verifyCertificate(string memory _certId)
        external
        view
        returns (
            bool exists,
            bytes32 certHash,
            string memory recipientName,
            string memory title,
            string memory issuerName,
            address issuer,
            uint256 issuedAt,
            bool isRevoked
        )
    {
        if (!certificateExists_[_certId]) {
            return (false, bytes32(0), "", "", "", address(0), 0, false);
        }

        Certificate storage cert = certificates[_certId];
        return (
            true,
            cert.certHash,
            cert.recipientName,
            cert.title,
            cert.issuerName,
            cert.issuer,
            cert.issuedAt,
            cert.isRevoked
        );
    }

    function certificateExists(string memory _certId) external view returns (bool) {
        return certificateExists_[_certId];
    }
}