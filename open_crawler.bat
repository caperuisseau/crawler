@echo off
for /l %%i in (1,1,40) do (
    start python "test.py"
)
