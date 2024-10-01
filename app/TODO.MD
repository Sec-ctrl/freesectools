###  To Do  ###


Create Test .py's in tests/

github secret tokken Dockker: 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


## LINTING
# Linting the program are reformatting for best practises.
1. (venv) C:\Users\Bib\3D Objects\Resume Projects\privacy_tools\app>flake8 . 
2. C:\Users\Bib\3D Objects\Resume Projects\privacy_tools\app>black .


## UNIT TESTING
# create Automation of test py: - (Redis must be running when testing) target:80%+    actual:85
1. (venv) C:\Users\Bib\3D Objects\Resume Projects\privacy_tools\app>set PYTHONPATH=%PYTHONPATH%;C:\Users\Bib\3D Objects\Resume Projects\privacy_tools\app\   
2. (venv) C:\Users\Bib\3D Objects\Resume Projects\privacy_tools\app>pytest --cov=app --cov=routes --cov-report=term-missing
(3.) (venv) C:\Users\Bib\3D Objects\Resume Projects\privacy_tools\app>pytest --cov=app --cov=routes --cov=forms --cov=models --cov=modules --cov=security_headers --cov-report=term-missing


