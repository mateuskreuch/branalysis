```python -m build```

```twine upload dist/*```

```twine upload --repository testpypi dist/*```

```pip install --index-url https://test.pypi.org/simple/ branalysis```