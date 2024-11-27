@echo off

set ui_dir=ui
set out_dir=ui_compiled

for %%f in (%ui_dir%\*.ui) do (
	call C:\Users\vikto\anaconda3\Scripts\pyuic5 -o "%out_dir%\ui_%%~nf.py" "%%f"
	if errorlevel 1 (
		pause
		exit 1
	)
)
