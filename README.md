# PrivSense and misc tools

Python3 (assuming your default python installation is python)
Good to use pyvenv: python -m venv /path/to/new/virtual/environment

Dependencies:
  - pip3 install colorama spacy python-levenshtein json2table javalang
  - python -m spacy download en_core_web_lg
  - ulimit -Sn 409600

All code in base should have --help available. 
PrivacySimilarity takes a while to start up because of the spacy module library.
Debug options require a random argument right now. (e.g. -d 1)

RunAnalysis runs full analysis with results written to dir youre running from. 
  - CodeExtractor -> PrivacySimilarity -> results
  - there are post analysis scripts in ./tools/ancilliary_tools
  - Results also written to html tables if you ever want to make a web app to run analysis and show results.
  - All apps and app results expected to written to App category sub directories.
  - Makes use of multiprocessing and concurrent processes via yeild statements.
