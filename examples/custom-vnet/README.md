This example shows you how to use custom vnet. Note it requires several steps:
1. `terraform init`
2. `terraform apply -target "azurerm_virtual_network.example"`
3. `terraform apply`

The reason of breaking the terraform operations into two targets is that 
Terraform needs to know at static time the value of 
`length(var.custom_network) > 0`, which is used in various `count` predicates.
However, in this example, the `custom_network` input variable can only be computed 
after `azurerm_virtual_network.example` is created. As such, Terraform won't be 
able to plan if we run `terraform plan/apply` to plan/create resources in one go.
Now we break it into step 2 and 3. Step 2 allows Terraform to create the vnet
resource first, and then Terraform will know that `length(custom_network) > 0` 
is true in step 3 at static time. 