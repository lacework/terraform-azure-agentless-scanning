# Release Notes
Another day, another release. These are the release notes for the version `v1.6.1`.

## Bug Fixes
* fix: use simple conditional instead of coalesce for subscription_id in azurerm config (Timothy Nguyen)([d2a1249](https://github.com/lacework/terraform-azure-agentless-scanning/commit/d2a124993fde2cf2422ef303787dd781c6a3fc18))
* fix: use fully qualified ids for service principal references (Timothy Nguyen)([87167f7](https://github.com/lacework/terraform-azure-agentless-scanning/commit/87167f7f55fef694f54d3b8a744f65365c68d26a))
* fix: use scanning_subscription_id from global module reference for regional modules (Timothy Nguyen)([0f318db](https://github.com/lacework/terraform-azure-agentless-scanning/commit/0f318db64dc75eb38f726ef527e8651bac986e3a))
## Documentation Updates
* docs: update readme (Timothy Nguyen)([e99b1d8](https://github.com/lacework/terraform-azure-agentless-scanning/commit/e99b1d8daaba4c2ab9e314c1ebb51e23f6fcbe3f))
## Other Changes
* chore: add var lacework_integration_guid to outputs and sleep for az role propogation (#62) (lokeshv-fortinet)([c2aaf66](https://github.com/lacework/terraform-azure-agentless-scanning/commit/c2aaf661eb7d2d1a6fbf15141f6cfbb047995de3))
* chore: make terraform-docs (Pengyuan Zhao)([74f348d](https://github.com/lacework/terraform-azure-agentless-scanning/commit/74f348d48d723405fa7ead553a8169b19d196e5b))
* chore: make terraform-docs (Pengyuan Zhao)([8602e82](https://github.com/lacework/terraform-azure-agentless-scanning/commit/8602e8244c1b3b8f52d346160006d61c33152d5e))
* chore: update provider versions to azuread 3.4 and azurerm 4.37 (Timothy Nguyen)([19fb1c2](https://github.com/lacework/terraform-azure-agentless-scanning/commit/19fb1c2800991f8aee4c7be9824b04b7fd19c6c8))
* chore: update provider versions azuread to 3.4.0 azurerm to 4.37.0 (Timothy Nguyen)([a9fe413](https://github.com/lacework/terraform-azure-agentless-scanning/commit/a9fe413e0e545354175bb9387137a2df0dfaddf5))
* ci: version bump to v1.6.1-dev (Lacework)([75e5cb6](https://github.com/lacework/terraform-azure-agentless-scanning/commit/75e5cb6cfdd1c4f6112581a6252b39e7c0bcae6b))
