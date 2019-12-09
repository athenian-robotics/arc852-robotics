[![Code Health](https://landscape.io/github/athenian-robotics/arc852-robotics/master/landscape.svg?style=flat)](https://landscape.io/github/athenian-robotics/arc852-robotics/master)
[![Maintainability](https://api.codeclimate.com/v1/badges/f1537538c97f8f4bfcb6/maintainability)](https://codeclimate.com/github/athenian-robotics/arc852-robotics/maintainability)

# ARC852 Robotics Utilities

## Setup

Install *arc852-robotics* with:
```bash
sudo -H pip3 install arc852-robotics --extra-index-url https://pypi.fury.io/pambrose/
```
**Warning:** if you have problems with the cache, use the `--no-cache-dir` option.

Update *arc852-robotics* with:
```bash
sudo -H pip3 install --upgrade arc852-robotics --extra-index-url https://pypi.fury.io/pambrose/
```

Uninstall *arc852-robotics* with:
```bash
sudo -H pip3 uninstall arc852-robotics
```

Every update requires a version update in *setup.py*.

## Gemfury Setup

Update the `version` in `setup.py` before pushing to Gemfury.

Add the Gemfury repo with:
```bash
git remote add fury https://<your-username>@git.fury.io/pambrose/arc852-robotics.git
```

Push new versions to Gemfury with:
```bash
git push fury master
```

