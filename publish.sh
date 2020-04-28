set -eux


[[ -z $(git status --porcelain) ]] || (echo "Uncommited changes"; exit 1)
git branch | grep master || (echo "Need to be on master"; exit 1)
rm -r dist/ build/ *.egg-info/
pipenv run python setup.py sdist bdist_wheel
pipenv run twine upload dist/*