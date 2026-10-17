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

    event ProductRegistered(bytes32 indexed key, string productId, string manufacturer);
    event ManufacturerAuthorized(address indexed account);
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
    }

    function authorizeManufacturer(address account) external onlyOwner {
        authorizedManufacturers[account] = true;
        emit ManufacturerAuthorized(account);
    }

    function revokeManufacturer(address account) external onlyOwner {
        authorizedManufacturers[account] = false;
        emit ManufacturerRevoked(account);
    }

    function registerProduct(
        string calldata productId,
        string calldata name,
        string calldata manufacturer,
        uint256 manufacturedAt
    ) external onlyAuthorized {
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
