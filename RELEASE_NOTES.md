# Release Notes
Another day, another release. These are the release notes for the version `v1.5.0`.

## Features
* feat: scan subscriptions created after deployment (Timothy Nguyen)([a409b00](https://github.com/lacework/terraform-azure-agentless-scanning/commit/a409b000679c8f6a971796ae33effc36bb3cd62e))
* feat(AWLS2-474): use service endpoints in Azure deployments (Joe Wilder)([831c9aa](https://github.com/lacework/terraform-azure-agentless-scanning/commit/831c9aa583b73dcb09e3234b751bfeb1b3e1ed34))
* feat(custom_roles): add permissions to read VMSS and VMSS VMs (Timothy Nguyen)([a3b2524](https://github.com/lacework/terraform-azure-agentless-scanning/commit/a3b25247f4f9ce033750f705bd1cd19f591cab65))
## Bug Fixes
* fix: separate included and excluded subscriptions as separate inputs (Timothy Nguyen)([92e87fe](https://github.com/lacework/terraform-azure-agentless-scanning/commit/92e87fef889dcabc84cf027703895d50e60dde4a))
* fix: set subscriptions_list to only scanning subscription for subscription-level integrations (Timothy Nguyen)([b4df43b](https://github.com/lacework/terraform-azure-agentless-scanning/commit/b4df43baaa1fb768994bee0442f4799617e020ab))
* fix: escape fwd slash in subscriptions prefix pattern string (Timothy Nguyen)([df8aefe](https://github.com/lacework/terraform-azure-agentless-scanning/commit/df8aefe96929045df9c5eaa966b8ce0418eafc45))
* fix(AWLS2-432): update readme (Joe Wilder)([8c28364](https://github.com/lacework/terraform-azure-agentless-scanning/commit/8c28364381cad8af043a0c8080b3e2cddb1d3bca))
* fix(AWLS2-462): syntax issue in nightly CI runs (Joe Wilder)([30a1de9](https://github.com/lacework/terraform-azure-agentless-scanning/commit/30a1de987a2bb882bd0ae75d5de5a3eeb479ea46))
## Documentation Updates
* docs: run terraform-docs (Pengyuan Zhao)([b4f53a0](https://github.com/lacework/terraform-azure-agentless-scanning/commit/b4f53a06b71b893bc14b3c626b454882cf8008dc))
* docs: run terraform-docs (Timothy Nguyen)([eee92cf](https://github.com/lacework/terraform-azure-agentless-scanning/commit/eee92cfde469d0621c2af7bfa67d94615f1b42d1))
## Other Changes
* chore(terraform-docs): update terraform-docs script (Timothy Nguyen)([dff9bea](https://github.com/lacework/terraform-azure-agentless-scanning/commit/dff9bea127b4bb10dfe2e9043b149c8247662d4c))
* ci: version bump to v1.4.3-dev (Lacework)([7f2afc7](https://github.com/lacework/terraform-azure-agentless-scanning/commit/7f2afc7c58fb67307df78136035ac24853bc30ba))
