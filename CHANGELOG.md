# v1.5.0

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
---
# v1.4.2

## Bug Fixes
* fix(AWLS2-456) Set tags in scanning resource group and log analytics workspace (Japneet Singh)([a2eb526](https://github.com/lacework/terraform-azure-agentless-scanning/commit/a2eb526d760db50a978e52808c2813d9ea7c6584))
## Other Changes
* ci: version bump to v1.4.2-dev (Lacework)([b2c616f](https://github.com/lacework/terraform-azure-agentless-scanning/commit/b2c616f09544f3271b1131f54527ad0c64d9e7f5))
---
# v1.4.1

## Other Changes
* ci: version bump to v1.4.1-dev (Lacework)([a4fa1f5](https://github.com/lacework/terraform-azure-agentless-scanning/commit/a4fa1f5887e16e6e2b7f6eb7e75af8235fce49d9))
---
# v1.4.0

## Features
* feat(AWLS2-444): add nat gateway to terraform (Joe Wilder)([66db51d](https://github.com/lacework/terraform-azure-agentless-scanning/commit/66db51d37e002e220ee5521189612575664cfc5d))
* feat(AWLS2-444): update CI to use Terraform 1.9 as minimum version (Joe Wilder)([fa56ce1](https://github.com/lacework/terraform-azure-agentless-scanning/commit/fa56ce13ddace99b885276b38f733c9b074f1858))
## Other Changes
* ci: version bump to v1.3.1-dev (Lacework)([608df94](https://github.com/lacework/terraform-azure-agentless-scanning/commit/608df9488015cd3ce8338d61fdf83a5cbb70ff57))
---
# v1.3.0

## Features
* feat(AWLS2-353): remove unnecessary comment (Joe Wilder)([e430566](https://github.com/lacework/terraform-azure-agentless-scanning/commit/e4305666db47721f702210e3be9feda4a81f9c35))
* feat(AWLS2-353): try to scope down permissions (Joe Wilder)([eeb9f29](https://github.com/lacework/terraform-azure-agentless-scanning/commit/eeb9f29d38fb783be88381cabee6dad99515969d))
* feat(AWLS2-353): update role for cost estimation permissions (Joe Wilder)([00775e0](https://github.com/lacework/terraform-azure-agentless-scanning/commit/00775e05487ab050c7b627509482a3490d81b6ed))
## Other Changes
* ci: version bump to v1.2.2-dev (Lacework)([087dc6a](https://github.com/lacework/terraform-azure-agentless-scanning/commit/087dc6ab76e405cb98bb0eb9c4497387ca5f8658))
---
# v1.2.1

## Other Changes
* chore: Update lacework provider dependency to ~>2.0 (Pengyuan Zhao)([2636b25](https://github.com/lacework/terraform-azure-agentless-scanning/commit/2636b2531b8695d4a98b66abbb30936fee0067e7))
* ci: version bump to v1.2.1-dev (Lacework)([2c85ea2](https://github.com/lacework/terraform-azure-agentless-scanning/commit/2c85ea29a9b528824aaa2332057a2e1b306a845a))
---
# v1.2.0

## Features
* feat: Updated Azure provider versions (#37) (Japneet Singh)([1e1d649](https://github.com/lacework/terraform-azure-agentless-scanning/pull/37/commits/1e1d6493be2546799a7222bb8916632b7f1ebae7))
* feat: support regions not supported by Azure (#16) (Ao Zhang)([4e05d59](https://github.com/lacework/terraform-azure-agentless-scanning/commit/4e05d59c6c9184f4dca930a56eec6466abf35727))
## Other Changes
* chore(GROW-2952): add codeowners (#33) (Matt Cadorette)([74d74d8](https://github.com/lacework/terraform-azure-agentless-scanning/commit/74d74d8336cd93a0ab1dfd59fbc3a6121d970ee6))
* ci: version bump to v1.1.3-dev (Lacework)([7e8380f](https://github.com/lacework/terraform-azure-agentless-scanning/commit/7e8380fdd29678e2eda2cae0b79cc8a6823cea59))
---
# v1.1.2

## Bug Fixes
* fix: fix off by one validator condition (#31) (Ao Zhang)([8a2b7d4](https://github.com/lacework/terraform-azure-agentless-scanning/commit/8a2b7d4842901e16289149b6e10819a04cdeb5c1))
## Other Changes
* ci: version bump to v1.1.2-dev (Lacework)([81ce337](https://github.com/lacework/terraform-azure-agentless-scanning/commit/81ce337c503c4926ad7ac8ba1849f187dfda08fb))
---
# v1.1.1

## Bug Fixes
* fix: dependency on global resource group creation   (#29) (Ao Zhang)([c67c592](https://github.com/lacework/terraform-azure-agentless-scanning/commit/c67c5923a416bb4c80f5f5a1467f2153d0dd14a5))
## Other Changes
* ci: version bump to v1.1.1-dev (Lacework)([23d38c1](https://github.com/lacework/terraform-azure-agentless-scanning/commit/23d38c112b83816bf899582f616d8afda177c560))
---
# v1.1.0

## Features
* feat: run jobs immediately after creation (#27) (Ao Zhang)([44c87ba](https://github.com/lacework/terraform-azure-agentless-scanning/commit/44c87ba08365feeae614a783ad91a44d7b224410))
## Other Changes
* ci: update terraform versions used for tests (Timothy MacDonald)([5779a25](https://github.com/lacework/terraform-azure-agentless-scanning/commit/5779a25b7a4d5d749ec4cf3923ea7aee415b5a73))
* ci: update job name in test compat workflow (Timothy MacDonald)([e96d165](https://github.com/lacework/terraform-azure-agentless-scanning/commit/e96d1652407618a5f8adcbe9cc4e0de3d1c56935))
* ci: migrate from codefresh to github actions (Timothy MacDonald)([4296456](https://github.com/lacework/terraform-azure-agentless-scanning/commit/429645607069e49636666969dc64d8386450a67c))
* ci: version bump to v1.0.1-dev (Lacework)([9b51200](https://github.com/lacework/terraform-azure-agentless-scanning/commit/9b51200fbb002f5cda49a70c3b2c0b2c9b065792))
---
# v1.0.0

## 💥 Breaking Changes
* feat: bump tf requirement to 1.5 (#21) (Ao Zhang)([4c44fe8](https://github.com/lacework/terraform-azure-agentless-scanning/commit/4c44fe85e043c11f8d4fada33ce0f1bf0b0d75ee))

## Features
* feat: pass environment variables to cloud task via provider (Max Fechner)([29c3da9](https://github.com/lacework/terraform-azure-agentless-scanning/commit/29c3da96c5f2831a85b13dac6a2bee60c786b195))
* feat: add checks (#21) (Ao Zhang)([4c44fe8](https://github.com/lacework/terraform-azure-agentless-scanning/commit/4c44fe85e043c11f8d4fada33ce0f1bf0b0d75ee))
## Other Changes
* ci: version bump to v1.0.0 (Lacework)([f703714](https://github.com/lacework/terraform-azure-agentless-scanning/commit/f7037143bb5f176ad2a056abbd3d850c2a1f23bb))
---
# v0.2.1

## Bug Fixes
* fix: perms to support enumeration across accts (Ao Zhang)([653c6e9](https://github.com/lacework/terraform-azure-agentless-scanning/commit/653c6e9b2af03c488b489e7964064af01e898385))
## Other Changes
* ci: version bump to v0.2.1-dev (Lacework)([546087e](https://github.com/lacework/terraform-azure-agentless-scanning/commit/546087eda16ed2244017025a5c2e6d80d5ef3d86))
---
# v0.2.0

## Features
* feat: support infra level encryption (#15) (Ao Zhang)([aebfb28](https://github.com/lacework/terraform-azure-agentless-scanning/commit/aebfb28e7bfcb1b6bf326b06efee4a4d81651abd))
## Other Changes
* chore: set local var module name (#19) (Darren)([54dbf48](https://github.com/lacework/terraform-azure-agentless-scanning/commit/54dbf48a7e2266505c7746520afb9d6d9b9e7983))
* chore: add lacework_metric_module datasource (#17) (Darren)([b2ffc6b](https://github.com/lacework/terraform-azure-agentless-scanning/commit/b2ffc6b8d0a0bc30f1e0532f009606e006084f52))
* ci: version bump to v0.1.4-dev (Lacework)([3c8803b](https://github.com/lacework/terraform-azure-agentless-scanning/commit/3c8803bba4e511c78679a7ab0d57d2d5f0d9abaf))
---
# v0.1.3

## Bug Fixes
* fix: public IP address permissions are needed (#11) (Ao Zhang)([7a8dbee](https://github.com/lacework/terraform-azure-agentless-scanning/commit/7a8dbeef17dce76940983290edce06290ccd4294))
## Other Changes
* ci: version bump to v0.1.3-dev (Lacework)([a2b42db](https://github.com/lacework/terraform-azure-agentless-scanning/commit/a2b42db97b1f028fd05995007edc3ba0a6310246))
---
# v0.1.2

## Other Changes
* chore: shorten container app job name (#9) (Ao Zhang)([15140d8](https://github.com/lacework/terraform-azure-agentless-scanning/commit/15140d8f7133a9167998c154894d95cb72a84fd0))
* ci: version bump to v0.1.2-dev (Lacework)([62f0f62](https://github.com/lacework/terraform-azure-agentless-scanning/commit/62f0f626a7768c3b7dd9074db70e807d487dca9c))
---
# v0.1.1

## Other Changes
* ci: version bump to v0.1.1-dev (Lacework)([778b510](https://github.com/lacework/terraform-azure-agentless-scanning/commit/778b5109891553f2947d49f9f3f43b76a8bb92b6))
---
# v0.1.0

## Features
* feat: initial commit with Azure integration module (Ao Zhang)([cd31fcf](https://github.com/lacework/terraform-azure-agentless-scanning/commit/cd31fcfc3af2391b0a4e1a267ce4bb3192d6d57c))
* feat: shape our TF module scaffolding (#1) (matthew zeier)([a37d4e4](https://github.com/lacework/terraform-azure-agentless-scanning/commit/a37d4e407ae523efe14d0aaeb98bd59d0df2e153))
## Bug Fixes
* fix: add periods because TF 1.5 (Ao Zhang)([f3a5b77](https://github.com/lacework/terraform-azure-agentless-scanning/commit/f3a5b7743d8e8685a4a2ded89160b33295c9f872))
## Documentation Updates
* docs(readme): automate update and testing of README.md by terraform-docs Add github action to test that README.md has been update. Also add update of README.md to /scripts/release.sh prepare (Timothy MacDonald)([a7558ba](https://github.com/lacework/terraform-azure-agentless-scanning/commit/a7558ba7f67233bdd28730ef2ae4b82cd607973e))
* docs(readme): add terraform docs automation Add terraform docs script along with makefile target and gihub action for same (Timothy MacDonald)([9d4fc66](https://github.com/lacework/terraform-azure-agentless-scanning/commit/9d4fc66f1aa130ebc809d1c2e3ebbb9248163a45))
## Other Changes
* chore: more cleanup before publishing (#5) (Ao Zhang)([01e8a82](https://github.com/lacework/terraform-azure-agentless-scanning/commit/01e8a82713b73ea3fe061ff1484ee43428c23b4c))
* chore: add doc update (Ao Zhang)([7f6ca56](https://github.com/lacework/terraform-azure-agentless-scanning/commit/7f6ca565dd608c21a8cdc6a9f17f05a33df97046))
* chore: update the version requirement of TF again (Ao Zhang)([db1ffe9](https://github.com/lacework/terraform-azure-agentless-scanning/commit/db1ffe986171d61fb3a7e92e84f09f049851d91a))
* chore: comment out check (Ao Zhang)([4a629ad](https://github.com/lacework/terraform-azure-agentless-scanning/commit/4a629adcfd4dfd996179595a979505ba24774d4f))
* chore: removing spaces #1000 (Ao Zhang)([e08a78d](https://github.com/lacework/terraform-azure-agentless-scanning/commit/e08a78d18ee34832f5204a12623915ca5c7e39d5))
* chore: update readme (Ao Zhang)([5ef1e3e](https://github.com/lacework/terraform-azure-agentless-scanning/commit/5ef1e3ecb59999b9d4c6f53fe8150b65aafc5f21))
* chore: remove space (Ao Zhang)([6ffcda2](https://github.com/lacework/terraform-azure-agentless-scanning/commit/6ffcda2fde5ffea18fdb58162b200d912b1363b5))
* chore: period (Ao Zhang)([c1f13b4](https://github.com/lacework/terraform-azure-agentless-scanning/commit/c1f13b48c599e9f33128a32703370e11b626ee6b))
* chore: update Lacework provider version (#6) (Darren)([a192ae8](https://github.com/lacework/terraform-azure-agentless-scanning/commit/a192ae8741d2c323701941f2bc278f0475ed1c94))
* chore(scaffolding): Update pull-request-template.md to latest (Ross)([073dc1a](https://github.com/lacework/terraform-azure-agentless-scanning/commit/073dc1ab8df9789b3b0912dea1788994690d36f5))
* chore(scaffolding): Add .github config (Ross)([7f6b9c9](https://github.com/lacework/terraform-azure-agentless-scanning/commit/7f6b9c972462a945be53881c5b54d14ee0f764d7))
* chore(scaffolding): Update scaffolding repo (Ross)([1af1f39](https://github.com/lacework/terraform-azure-agentless-scanning/commit/1af1f39bf8e1c05d9024ae0dc643276d1253cf11))
* chore: bump required version of TF to 0.12.31 (#3) (Scott Ford)([09d0ead](https://github.com/lacework/terraform-azure-agentless-scanning/commit/09d0eadc0b4d7a271efc37ceb393c57b43eb3326))
* ci: sign lacework-releng commits (#4) (Salim Afiune)([1627168](https://github.com/lacework/terraform-azure-agentless-scanning/commit/1627168af9b5494764897183fec56b78e8aee22f))
* ci: fix finding major versions during release (#2) (Salim Afiune)([5034a05](https://github.com/lacework/terraform-azure-agentless-scanning/commit/5034a05f1e484b458c71bca96a0e874f23c9f3a9))
---
