#!/usr/bin/env zsh
echo "version bump"
poetry version patch || exit 1
current_version=$(poetry version -s) || exit 1
package_name=$(poetry version | cut -d ' ' -f 1)
git-amend
echo "build"
poetry lock && poetry install || exit 1
poetry build --clean || exit 1
echo "pip install"
pip install -e . || exit 1
echo "pip list"
pip list --editable | grep $package_name
