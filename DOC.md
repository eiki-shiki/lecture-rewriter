# ДОКУМЕНТАЦИЯ

# Использование

Откройте папку с исходным кодом\
Если используется `venv`, необходимо его активировать.\
Запуск скрипта:
```bash
python3 lecture-rewriter.py path/to/launch-sript.json
```
Или сразу путь к директории с лекциями:
```bash
python3 lecture-rewriter.py path/to/lectures-dir
```

# Структура `launch-script.json`

*Хотя вместо launch-script.json может быть любое название.*
```python
[
    {
        # Директория с mp4 файлами (скрипт пройдётся по каждому) или сам mp4 файл
        "task": [
            "path/to/dir", "path/to/file.mp4"
        ],
        # Действия:
        # 0 - voice_to_txt
        # 1 - vid_seq_to_txt
        # 2 - summary
        # 3 - to_pdf (только для директории)
        # def: []
        "act": [ # array[?] of int{0, 1, 2, 3}
            0, 1, 2, 3
        ],
        # Доп параметры (необязательно)
        "args": {
            # 0 и 1 будут выполняться одновременно. def: true
            "01async": true # bool
        }
    },
    {
        ...
    }
]
```
Если ввести путь к директории, то `launch-script.json` будет в `"task"` иметь только этот путь, а в `act` будет иметь `[0, 1, 2, 3]`. Так же рекомендуется не использовать `to_pdf` в одном `"task"` вместе с остальными. Лучше сделать это отдельным `"task"`. Исключение: если в `"task"` находится только директории (к которым `to_pdf` будет применено индивидуально).

- `voice_to_txt` - преобразует голос в текст из лекции.
- `vid_seq_to_txt` - делает скриншоты лекции.
- `summary` - совмещает `voice_to_txt` и `vid_seq_to_txt` для `to_pdf` для одной лекции.
- `to_pdf` - создаёт PDF с преобразованным голосом в текст и скриншотами из лекций. На вход идёт директория с готовыми `summary`. PDF будет содержать все лекции.

# Структура директории лекций

Если структура будет именно такой, то в скрипт можно будет ввести сразу путь к директории `/Лекции`:
```
.
├── Лекции
│   ├── Лекция1.mp4
│   ├── Лекция1
│   │   ├── voice_to_txt.cfg.json
│   │   └── vid_seq_to_txt.cfg.json
│   ├── Лекция2.mp4
│   ├── Лекция2
│   │   └── ...
│   ├── Лекция3.mp4
│   ├── Лекция3
│   │   └── ...
│   ├── ...
│   ├── ЛекцияN.mp4
│   ├── ЛекцияN
│   │   └── ...
│   ├── ...
```
- `/Лекции/ЛекцияN.mp4` - видео с лекции.
- `/Лекции/ЛекцияN/` - директория, имеющая точно такое же название, что и видео с лекции.
- `/Лекции/ЛекцияN/voice_to_txt.cfg.json` - поведение для преобразователя голос в текст. См [`Структура voice_to_txt.cfg.json`](#структура-voice_to_txtcfgjson)
- `/Лекции/ЛекцияN/vid_seq_to_txt.cfg.json` - поведение для создателя скриншотов. См [`Структура vid_seq_to_txt.cfg.json`](#структура-vid_seq_to_txtcfgjson)
- `/Лекции/ЛекцияN/summary.cfg.json` - поведение для скрипта для слияния сриншотов и голоса в тексте. См [`Структура summary.cfg.json`](#структура-summarycfgjson)
- `/Лекции/to_pdf.cfg.json` - поведение для создателя PDF. См [`Структура to_pdf.cfg.json`](#структура-to_pdfcfgjson)

Не рекомендуется оставлять какие-либо лишние файлы и директории (кроме PDF файлов).\
`*.cfg.json` файлы необязательны. В случае их отсутствия используются значения по умолчанию. Соответственно, необходимый минимум - только mp4 файлы.\
Так же mp4 файлы можно добавлять в скрипт запуска вручную.\
После активации скрипта, директория лекций будет выглядеть примерно так:
```
├── Лекции
│   ├── Лекция1.mp4
│   ├── Лекция1
│   │   ├── screens
│   │   │   ├── 1_???.jpg
│   │   │   ├── 2_???.jpg
│   │   │   └── ...
│   │   ├── audio-chunks
│   │   │   ├── chunk1.wav
│   │   │   ├── chunk2.wav
│   │   │   └── ...
│   │   ├── voice_to_txt.json
│   │   ├── vid_seq_to_txt.json
│   │   ├── voice_to_txt.json.done
│   │   ├── vid_seq_to_txt.json.done
│   │   ├── voice_to_txt.cfg.json
│   │   ├── vid_seq_to_txt.cfg.json
│   │   ├── summary.json
│   │   └── summary.json.done
│   ├── Лекция2.mp4
│   ├── Лекция2
│   │   └── ...
│   ├── Лекция3.mp4
│   ├── Лекция3
│   │   └── ...
│   ├── ...
│   ├── ЛекцияN.mp4
│   ├── ЛекцияN
│   │   └── ...
│   ├── ...
│   └── Document.pdf
```
- `/Лекции/ЛекцияN/screens` - директория со скриншотами.
- `/Лекции/ЛекцияN/vid_seq_to_txt.json` - данные о скриншотах.
- `/Лекции/ЛекцияN/audio-chunks` - директория с звуковыми файлами лекции (можно потом удалить).
- `/Лекции/ЛекцияN/voice_to_txt.json` - данные о преобразованном голосе в текст.
- `/Лекции/ЛекцияN/summary.json` - объединённые данные со скриншотов и голоса в текст.
- `/Лекции/Document.pdf` - PDF с голосом в текст и скриншотами.

# Структура `vid_seq_to_txt.cfg.json`

Поведение для `vid_seq_to_txt`.\
Используемые значения в каждом ключе - это значения по умолчанию.
```python
[
    {
        # Время в мс.
        # Можно использовать вместо "time" просто "t".
        "time": 0, # uint
        # Комментарий. Нигде не используется.
        "//": "", # any
        # Конфиги для vid_seq_to_txt.
        "configs": [], # array[?] of strings ; reset
        # Если true, то игнорируется сравнение со скриншотом на предыдущей итерации, и скриншот будет создан.
        "force": false, # bool ; reset
        # С момента времени "time" переместится на "jump" мс и продолжит итерацию.
        "jump": 0, # int ; reset
        # Перейдёт на "jump_to" момент времени в мс и продолжит итерацию, если > 0. В противном случае игнорируется.
        "jump_to": -1, # int ; reset
        # Итерация пройдёт, но скриншот сделан не будет. Полезно в сочетании с "jump" или "jump_to", чтобы не делать скриншот сразу после этого, а попытаться сделать на следующей итерации.
        "ignore": false, # bool ; reset
        # Аргументы для tesseract. Не рекомендуется менять.
        "tesseract_args": "-l rus+eng",
        # Кадрирование вида [x1, y1, x2, y2]. Если crop[3] = 0, то подставится ширина кадра. Если crop[4] = 0, то подставится высота кадра.
        "crop": [0, 0, 0, 0], # array[4] or uint
        # Кадрирование как "crop". Используется для области распознавания для сравнения с предыдущей итерации (если они разные, то создаётся новый скриншот).
        # Зависимость кадрирования: crop -> crop_rel -> crop_tess
        "crop_tess": [0, 0, 0, 0], # array[4] or uint
        # Кадрирование как "crop". Используется для кадрирования конечного изображения, которое пойдёт в screens.
        # Зависимость кадрирования: crop -> crop_rel -> crop_srcn
        "crop_scrn": [0, 0, 0, 0], # array[4] or uint
        # Кадрирование как "crop". Используется как второе кадрирование относительно crop.
        # Второе кадрирование может использоваться после основного кадрирования из конфига.
        # Зависимость кадрирования: crop -> crop_rel
        "crop_rel": [0, 0, 0, 0], # array[4] or uint
        # Кадрирование как "crop". Используется как второе кадрирование относительно crop_tess.
        # Второе кадрирование может использоваться после основного кадрирования из конфига.
        # Зависимость кадрирования: crop -> crop_rel -> crop_tess -> crop_tess_rel
        "crop_tess_rel": [0, 0, 0, 0], # array[4] or uint
        # Кадрирование как "crop". Используется как второе кадрирование относительно crop_scrn.
        # Второе кадрирование может использоваться после основного кадрирования из конфига.
        # Зависимость кадрирования: crop -> crop_rel -> crop_scrn -> crop_scrn_rel
        "crop_scrn_rel": [0, 0, 0, 0], # array[4] or uint
        # Максимальная допустимая разница текстов скриншота и скриншота предыдущей итерации, ниже которой текст считается разным.
        # Просто иногда преобразователь немного по-разному считывает один и тот же скриншот.
        "max_text_difference_ratio": 0.85, # float ; 0.0 < x < 1.0
        # Шаг итерации в мс. Не "портит" параметр "time" (или "t").
        "step": 3000, # int (or uint?)
        # Завершает этап (не аварийно), записывая результаты.
        "stop": false, # bool
    },
    {
        ...
    }
]
```

# Структура `voice_to_txt.cfg.json`

Поведение для `voice_to_txt`.\
Используемые значения в каждом ключе - это значения по умолчанию.
```python
[
    {
        # Время в мс.
        # Можно использовать вместо "time" просто "t".
        "time": 0, # uint
        # Комментарий. Нигде не используется.
        "//": "", # any
        # Конфиги для voice_to_txt.
        "configs": [], # array[?] of strings ; reset
        # Минимальная длина тишины в мс для разделения звуковой дорожки.
        # Действует только при "time" = 0. В остальных игнорируется.
        "min_silence_len": 1500, # uint
        # В дБ. При добавлении к средней громкости лекции считается тишиной.
        # Действует только при "time" = 0. В остальных игнорируется.
        "silence_thresh": -16, # int
        # Добавить тишины до и после разделённого сегмента в мс.
        # Действует только при "time" = 0. В остальных игнорируется.
        "keep_silence": 200, # uint
        # Добавить громкости в дБ до разделения звуковой дорожки.
        # Действует только при "time" = 0. В остальных игнорируется.
        "add_volume_before": 0, # int
        # Добавляет громкости в дБ после разделения дорожек. Не зависит от других add "add_volume".
        "add_volume": 0, # int
        # Добавляет громкости в дБ после разделения дорожек к существующему "add_volume". Не зависит от других add "add_volume_rel".
        # Второе добавление громкости может использоваться после основного из конфига.
        "add_volume_rel": 0, # int
        # Язык распознавания. Подробнее RFC 5646 language tag.
        "language": "ru-RU", # string
        # Перейдёт на "jump_to" момент времени в мс и продолжит итерацию, если > 0. В противном случае игнорируется.
        "jump_to": -1, # int
        # Итерация пройдёт, но распознавание голоса сделано не будет. Полезно в сочетании с "jump" или "jump_to", чтобы не делать распознавание сразу после этого, а попытаться сделать на следующей итерации.
        "ignore": false, # bool ; reset
        # Шаг итерации. Вообще не рекомендуется трогать.
        "step": 1, # int
        # Завершает этап (не аварийно), записывая результаты.
        "stop": false, # bool
    },
    {
        ...
    }
]
```

# Структура `summary.cfg.json`

### (пока не используется / coming soon)
Поведение для `summary`\
Используемые значения в каждом ключе - это значения по умолчанию.\
Отличительная особенность: используется единоразово.
```python
{
    # Комментарий. Нигде не используется.
    "//": "", # any
    # Конфиги для summary.
    "configs": [], # array[?] of strings ; reset
    # Заголовок в PDF. Если null, то берётся название mp4 файла (без расширения).
    "title": null, # string or null
    # Описание. В PDF будет написано под заголовком.
    "desc": "" # string
}
```

# Структура `to_pdf.cfg.json`

### (пока не используется / coming soon)
Поведение для `to_pdf`\
Используемые значения в каждом ключе - это значения по умолчанию.\
Отличительная особенность: используется единоразово.
```python
{
    # Комментарий. Нигде не используется.
    "//": "" # any
    # Конфиги для to_pdf.
    "configs": [], # array[?] of strings
}
```

# Система конфигов

Конфиги повторяют структуру соответствующих `*.cfg.json` и используются в них для сокращения размеров json файлов и для повторного использования. Единственное исключение состоит в том, что конфиги не имеют `"time"` (или `"t"`) и используются единоразово (как только были вызваны), поэтому, если возможно, вместо массива словарей они имеют структуру только словаря (как [структура `summary.cfg.json`](#структура-summarycfgjson)). В качестве примера можно рассмотреть конфиги по умолчанию в папке скрипта `src/configs/`. Так же можно создавать и свои конфиги. Так же название конфига `default` зарезервировано для возвращения значений по умолчанию.\
Для использования конфигов в `configs` соответствующих json файлов поведений, нужно написать путь к директории конфига или названия конфига из `src/configs/` (название директории). Можно использовать несколько конфигов в одном массиве. Они будут идти последовательно справа-налево.

# Структура конфигов

Так выглядет структура директории конфига, путь к которой используется в параметре `"configs"`.
```
├── Config_Name
│   ├── voice_to_txt.cfg.json
│   └── vid_seq_to_txt.cfg.json
```
В [`Системе конфигов`](#система-конфигов) была описана разница, между json файлами поведения и json файлами конфигов с одинаковым названием. Примеры можно увидеть в `src/configs/`.

# Повторное использование скрипта на той же лекции

После использования скрипта и выполнения соответственной фазы, создаются файлы `vid_seq_to_txt.json.done`, `voice_to_txt.json.done` и `summary.json.done`, которые препятствуют повторному использованию скрипта на одной и той же лекции. Для повторного использования эти файлы нужно удалить. Также рекомендуется удалить папки `screens` и `audio-chunks` для меньшего использования памяти компьютера.

# Резервное копирование

Если во время исполнения этапа `voice_to_txt` или `vid_seq_to_txt` что-то пойдёт не так и скрипт завершит свою работу до того, как всё будет готово - будут созданы файлы `voice_to_txt.save.json` или `vid_seq_to_txt.save.json` соответственно, чтобы продолжить прогресс при следующем запуске скрипта на соответствующем этапе. Чтобы сброить прогресс, удалите эти файлы. При корректном завершении этапа, эти файлы автоматически удаляются.

# ПРИМЕРЫ

# Пример 1

### Лекции Ли.
Директория должна выглядеть [`всё так же`](#структура-директории-лекций):
```
.
├── Лекции_Ли
│   ├── Лекция1.mp4
│   ├── Лекция1
│   │   ├── voice_to_txt.cfg.json
│   │   └── vid_seq_to_txt.cfg.json
│   ├── Лекция2.mp4
│   ├── Лекция2
│   │   └── ...
│   ├── Лекция3.mp4
│   ├── Лекция3
│   │   └── ...
│   ├── ...
│   ├── ЛекцияN.mp4
│   ├── ЛекцияN
│   │   └── ...
│   ├── ...
```

Так, как конфиг для лекции Ли, которые проводятся в microsoft teams, есть по умолчанию в `src/configs/` (который содержит в себе сразу конфиг `teams-basic`), то предлагаются такие JSON файлы поведения:
`voice_to_txt.cfg.json`
```python
[
    {
        "configs": ["os-li-basic"]
    }
]
```
`vid_seq_to_txt.cfg.json`
```python
[
    {
        "configs": ["os-li-basic"],
        "step": 1000
    },
    {
        "force": true
    },
    {
        "jump_to": 3000,
        "force": true
    },
    {
        "jump_to": 138000,
        "force": true
    },
    {
        "jump_to": 186000,
        "force": true
    },
    {
        "jump_to": 557000,
        "force": true
    },
    {
        "stop": true
    }
]
```
Так, как автоматическое создание скриншотов пока работает криво, рекомендуется делать скриншоты вручную. `"jump_to"` - на каком моменте в мс сделать скриншот. `"force"` в таком случае должен быть в каждом `true`. Завершается всё `"stop": true`. Так же в начале рекомендуется поставить `"step"` на очень небольшой промежуток времени в мс (иногда возникают повторные скриншоты).\
Аналогично будет всё и с лекциями Сы.

# Пример 2

### Лекции Ша.

Его лекции тоже проводятся в microsoft teams, но лично его конфига в `src/configs/` нет.\
Тогда JSON файлы поведения будут выглядеть примерно так:
`voice_to_txt.cfg.json`
```python
[
    {
        "configs": ["teams-basic"]
    }
]
```
`vid_seq_to_txt.cfg.json`
```python
[
    {
        "configs": ["teams-basic"],
        "step": 1000
    },
    {
        "force": true
    },
    {
        "jump_to": 3000,
        "force": true
    },
    {
        "jump_to": 138000,
        "force": true
    },
    {
        "jump_to": 186000,
        "force": true
    },
    {
        "jump_to": 557000,
        "force": true
    },
    {
        "stop": true
    }
]
```
