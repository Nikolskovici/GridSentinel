@echo off
cd Interfata
call node_modules\.bin\electron . --enable-logging --log-level INFO 2>&1
