echo on
cd venv\Scripts
call activate
cd ../../
pytest -vsm dv_test
pause