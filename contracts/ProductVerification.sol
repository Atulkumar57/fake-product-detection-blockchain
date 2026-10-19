// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ProductVerification {
    struct Product {
        string productId;
        string name;
        string manufacturer;
        uint256 manufacturedAt;
        address registeredBy;
        bool exists;
    }

    address public owner;
    mapping(bytes32 => Product) private products;
    mapping(address => bool) public authorizedManufacturers;
    mapping(address => string) public manufacturerNames;

    event ProductRegistered(bytes32 indexed key, string productId, string manufacturer);
    event ManufacturerAuthorized(address indexed account, string manufacturerName);
    event ManufacturerRevoked(address indexed account);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier onlyAuthorized() {
        require(authorizedManufacturers[msg.sender], "Not authorized");
        _;
    }

    constructor() {
        owner = msg.sender;
        authorizedManufacturers[msg.sender] = true;
        manufacturerNames[msg.sender] = "Owner";
    }

    function authorizeManufacturer(address account, string calldata manufacturerName)
        external
        onlyOwner
    {
        require(account != address(0), "Invalid account");
        require(bytes(manufacturerName).length > 0, "Manufacturer name required");

        authorizedManufacturers[account] = true;
        manufacturerNames[account] = manufacturerName;
        emit ManufacturerAuthorized(account, manufacturerName);
    }

    function revokeManufacturer(address account) external onlyOwner {
        authorizedManufacturers[account] = false;
        manufacturerNames[account] = "";
        emit ManufacturerRevoked(account);
    }

    function registerProduct(
        string calldata productId,
        string calldata name,
        string calldata manufacturer,
        uint256 manufacturedAt
    ) external onlyAuthorized {
        require(bytes(productId).length > 0, "Product ID required");
        require(bytes(name).length > 0, "Product name required");
        require(bytes(manufacturer).length > 0, "Manufacturer required");
        require(manufacturedAt <= block.timestamp, "Manufactured-at cannot be in the future");
        require(
            keccak256(bytes(manufacturerNames[msg.sender])) == keccak256(bytes(manufacturer)),
            "Manufacturer name mismatch"
        );

        bytes32 key = keccak256(abi.encodePacked(productId));
        require(!products[key].exists, "Product already registered");

        products[key] = Product({
            productId: productId,
            name: name,
            manufacturer: manufacturer,
            manufacturedAt: manufacturedAt,
            registeredBy: msg.sender,
            exists: true
        });

        emit ProductRegistered(key, productId, manufacturer);
    }

    function verifyProduct(string calldata productId)
        external
        view
        returns (
            bool exists,
            string memory name,
            string memory manufacturer,
            uint256 manufacturedAt,
            address registeredBy
        )
    {
        bytes32 key = keccak256(abi.encodePacked(productId));
        Product storage p = products[key];
        return (p.exists, p.name, p.manufacturer, p.manufacturedAt, p.registeredBy);
    }
}
