# lecture-rewriter

Ака транкрибатор лекций. Преобразует видео лекции в PDF.

# Установка

Скачайте исходный код.\
Установите `Python 3.8+`, [`Tesseract`](https://tesseract-ocr.github.io/tessdoc/Installation.html) и [`ffmpeg`](https://ffmpeg.org/). `Tesseract` и `ffmpeg` необходимо добавить в PATH.\
Потом нужно установить модули.\
Рекомендуется использовать [venv](https://docs.python.org/3/library/venv.html):
```bash
python3 -m venv venv
```
Активация `venv`:
- `Windows`:
```bash
venv\Scripts\activate
```
- `Linux/MacOS`:
```bash
source venv/bin/activate
```
\
Команда установки нужных модулей:
```bash
pip install -r requirements.txt
```

# Использование

Откройте папку с исходным кодом\
Если используется `venv`, необходимо его активировать.\
Запуск скрипта:
```bash
python3 lecture-rewriter.py path/to/cfg-file.json
```
Или сразу путь к директории с лекциями:
```bash
python3 lecture-rewriter.py path/to/lectures-dir
```
Подробнее об использовании прочитайте [полную документацию](DOC.md).

# Лицензия

[MIT](https://opensource.org/license/mit/)
