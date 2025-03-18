provider "azurerm" {
  features {
  }
}

locals {
  region = "eastus"
}

/* create a resource group, a vnet, and a subnet within */
resource "azurerm_resource_group" "example" {
  name     = "example-rg"
  location = local.region
}

/* Ensure the subnet allows egress traffic on port 443 or the scanner will break */
resource "azurerm_network_security_group" "example" {
  depends_on          = [azurerm_resource_group.example]
  name                = "example-nsg"
  location            = local.region
  resource_group_name = azurerm_resource_group.example.name

  security_rule {
    name                       = "Outbound_443"
    priority                   = 100
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "Internet"
  }
}

resource "azurerm_virtual_network" "example" {
  depends_on          = [azurerm_network_security_group.lw]
  name                = "example-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = local.region
  resource_group_name = azurerm_resource_group.example.name

  subnet {
    name           = "example-subnet"
    address_prefix = "10.0.0.0/16"
    security_group = azurerm_network_security_group.lw.id
  }
}


/* Create Lacework agentless integration within the custom setup. Note that
the virtual network and other networking resources above must already exist for
this to succeed. */
module "lacework_azure_agentless_scanning_rg_and_vnet" {
  source = "../.."

  integration_level              = "TENANT"
  global                         = true
  custom_network                 = tolist(azurerm_virtual_network.example.subnet)[0].id
  create_log_analytics_workspace = true
  region                         = local.region

  // When using a custom vnet with the default NAT gateway (use_nat_gateway = true),
  // you must specify the network security group here:
  custom_network_security_group = azurerm_network_security_group.example.id
  
  // If you want to use public IPs instead of a NAT gateway, comment out the line above
  // and uncomment this line:
  // use_nat_gateway = false
}
