# Release Notes
Another day, another release. These are the release notes for the version `v1.6.0`.

## Features
* feat(preflight): debug log cli args (Timothy Nguyen)([e1465ff](https://github.com/lacework/terraform-azure-agentless-scanning/commit/e1465ffb08b9300cb03952e598b42459a8f4e556))
* feat(preflight): count VMSS VMs in addition to VMs (Timothy Nguyen)([1f99589](https://github.com/lacework/terraform-azure-agentless-scanning/commit/1f995898bad4b01be98424a0e112091d3591eeb5))
* feat(preflight): add debug logging option (Timothy Nguyen)([d8b4415](https://github.com/lacework/terraform-azure-agentless-scanning/commit/d8b4415cba993fe83b0c9245f244e9bf445b58d6))
* feat(preflight): add option to disable emoji rendering (Timothy Nguyen)([ca17fff](https://github.com/lacework/terraform-azure-agentless-scanning/commit/ca17ffff5b2f48366a068812594b777aa0c5f1f1))
* feat(preflight): update cli options (Timothy Nguyen)([fa4a829](https://github.com/lacework/terraform-azure-agentless-scanning/commit/fa4a82990d396bec1f21c80be1675ecac62d4c0e))
* feat(preflight): infer integration type (Timothy Nguyen)([5800c28](https://github.com/lacework/terraform-azure-agentless-scanning/commit/5800c28948ed1b07a32d8651f0ea61d7f65b7602))
* feat: output results to json file (Timothy Nguyen)([415270c](https://github.com/lacework/terraform-azure-agentless-scanning/commit/415270cfdca6c61d578ec34c7db28b395721c626))
* feat(preflight): consider current quota usage in quota check (Timothy Nguyen)([868f9a4](https://github.com/lacework/terraform-azure-agentless-scanning/commit/868f9a44795ac3b6f06b9fc67da05a11a84576a1))
* feat(preflight): implement auth check (Timothy Nguyen)([07383f6](https://github.com/lacework/terraform-azure-agentless-scanning/commit/07383f68511224bddb476e5896071f2efa17ecb1))
* feat(preflight_check): implement usage quota checks (Timothy Nguyen)([36f413c](https://github.com/lacework/terraform-azure-agentless-scanning/commit/36f413c3086d9d66eb4a0a90c01995aac1482670))
* feat(preflight): improve quota readability (Timothy Nguyen)([bf76db7](https://github.com/lacework/terraform-azure-agentless-scanning/commit/bf76db74b15da49923aea45e2f7a10ceafe4e720))
* feat(preflight): interactively prompt for subscriptions, display subscriptions and vm counts in tables, compute quota requirements (Timothy Nguyen)([d8fd56c](https://github.com/lacework/terraform-azure-agentless-scanning/commit/d8fd56cc04c6ca9bcda166757f321fbe82670e99))
* feat(preflight): enumerate VMs and subscriptions to use as default values (Timothy Nguyen)([77b2670](https://github.com/lacework/terraform-azure-agentless-scanning/commit/77b2670a0d258dd024d0975bcc7644fb2066a65f))
* feat(preflight): scaffold project structure & script arguments (Timothy Nguyen)([79243aa](https://github.com/lacework/terraform-azure-agentless-scanning/commit/79243aab4451abfee38a3db3ef9e1994eaf50c10))
## Refactor
* refactor(preflight): remove unused fix_url property on UsageQuotaCheck classes (Timothy Nguyen)([c575648](https://github.com/lacework/terraform-azure-agentless-scanning/commit/c5756488286f75d925dcc62b66c299a803e33d10))
* refactor(preflight): clarify logic for computing required vcpu/ip (Timothy Nguyen)([5feeead](https://github.com/lacework/terraform-azure-agentless-scanning/commit/5feeeadde46218a4bd1da9c3ff575ce42e046f21))
* refactor(preflight): refactor preflight check and azure service (Timothy Nguyen)([0f0fbbe](https://github.com/lacework/terraform-azure-agentless-scanning/commit/0f0fbbe0a209420e5dd5720b9847ed7ade4dc378))
* refactor(preflight): refactor preflight script (Timothy Nguyen)([bd12067](https://github.com/lacework/terraform-azure-agentless-scanning/commit/bd12067251d77c0f13435e3d82f42adcee696c5b))
## Bug Fixes
* fix(custom-vnet): set proper resource name for nsg in custom-vnet example (Timothy Nguyen)([1130c98](https://github.com/lacework/terraform-azure-agentless-scanning/commit/1130c98ed0334ff52c5deb4ec7c71c05649315a9))
* fix(preflight): fix log level handling (Timothy Nguyen)([b31e90b](https://github.com/lacework/terraform-azure-agentless-scanning/commit/b31e90b331596c6afa55118802f6b48de34d0a38))
* fix(preflight): don't check nat gateway value when deciding between interactive and non-interactive mode (Timothy Nguyen)([f774e8d](https://github.com/lacework/terraform-azure-agentless-scanning/commit/f774e8d97f8760e7dcc9628e69c772b984d8be7c))
* fix(preflight): use objectID instead of appID as principal ID for SP (Timothy Nguyen)([de1c128](https://github.com/lacework/terraform-azure-agentless-scanning/commit/de1c1280744a2a83fb86ea74f4b44f7cc232e71b))
* fix(preflight): only print regions with failed quota checks (Timothy Nguyen)([cafa61d](https://github.com/lacework/terraform-azure-agentless-scanning/commit/cafa61d4ff5ab76890c5f3c72916ef71fa9be12c))
* fix(preflight): remove invalid keyword arg (Timothy Nguyen)([ca6a337](https://github.com/lacework/terraform-azure-agentless-scanning/commit/ca6a33729f84f4ac551608329a1f1647e1925882))
* fix(preflight): get principal id from az account show output for service principals (Timothy Nguyen)([65934f3](https://github.com/lacework/terraform-azure-agentless-scanning/commit/65934f30d4505a3a97c7fa964c392c4068114abb))
* fix: check permissions using regex, consider not actions (Timothy Nguyen)([53fb1f3](https://github.com/lacework/terraform-azure-agentless-scanning/commit/53fb1f38cf13aeea7eabb14ea9178e07881ae418))
## Documentation Updates
* docs: add instructions for deleting orphaned scanning VMs (Timothy Nguyen)([8b6857d](https://github.com/lacework/terraform-azure-agentless-scanning/commit/8b6857d178c1dca98fb6c1edbed981903fe53a88))
* docs(preflight): remove VM count suggestion for NAT gateway (Timothy Nguyen)([6e34909](https://github.com/lacework/terraform-azure-agentless-scanning/commit/6e34909efae835918350739726576429bf31c176))
* docs(preflight): update help text (Timothy Nguyen)([a2a419e](https://github.com/lacework/terraform-azure-agentless-scanning/commit/a2a419e7d33d7e9e790e91b1b3d5f0ebda783608))
* docs(preflight): update auth instructions (Timothy Nguyen)([bd6c8f8](https://github.com/lacework/terraform-azure-agentless-scanning/commit/bd6c8f880f098816e5e34561a7d64657e66cc740))
* docs(preflight): fix SP permissions (Timothy Nguyen)([c1714fa](https://github.com/lacework/terraform-azure-agentless-scanning/commit/c1714faebf847deaad547b5dfdf58c1e947cc75e))
* docs(preflight): update run command (Timothy Nguyen)([9f320db](https://github.com/lacework/terraform-azure-agentless-scanning/commit/9f320dbe312b68986108844c4b6755fe30821e0d))
* docs(preflight): document service principal creation with required permissions (Timothy Nguyen)([4ccf3ff](https://github.com/lacework/terraform-azure-agentless-scanning/commit/4ccf3ff657f9a6de3d10c21706a4d515ea7081f7))
* docs: link to preflight check from main README (Timothy Nguyen)([c248e9a](https://github.com/lacework/terraform-azure-agentless-scanning/commit/c248e9a510f78f0ad527174641181db773607177))
## Other Changes
* style(preflight): ruff format (Timothy Nguyen)([2cab59f](https://github.com/lacework/terraform-azure-agentless-scanning/commit/2cab59f331d2eb886c2cab92bb1ba20b29ac86f3))
* ci: version bump to v1.5.1-dev (Lacework)([db7fc65](https://github.com/lacework/terraform-azure-agentless-scanning/commit/db7fc6532d17d4172fdfd787615747f652787894))
