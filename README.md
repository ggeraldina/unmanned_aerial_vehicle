# Нахождение дронов на видео

## Документация

В папке проекта после `venv/Scripts/activate.bat` выполнить

`>python -m pydoc -p 331`

Документация будет доступна по адресу: http://localhost:331

---

## Папка **test_video**

https://drive.google.com/drive/folders/1nZNIsMh_c6lci8_yOeuPsb9hxv9oZToR?usp=sharing

---

## Нахождение движущихся объектов на видео

### Запуск

`>python -m processing_video -v test_video/any/car_evening.mp4`

### Параметры

* `-v`, `--video` - Путь к видео - **Обязательный праметр**
* `-shm`, `--showing_mask` - Показать маску изображения. Возможные значения *True  / False*. По умолчанию *False*.
* `-sv`, `--saving_videos` - Сохранять видео. Возможные значения *True  / False*. По умолчанию *False*; Сохранено будет в папке saving.

### Сохранить кадр

Нажать клавишу `s`; Сохранено будет в папке saving.

### Выход

Нажать клавишу `Esc` или закрыть окно.

## Пример работы программы

<div style="text-align:center"><img alt="Дрон" src="readme_images/drone00.png" width="100%" vspace="15" hspace="15"></div>

<div style="text-align:center"><img alt="Дрон" src="readme_images/drone01.png" width="100%" vspace="15" hspace="15"></div>

---

## Трекинг объектов на видео

### Запуск

`>python -m tracking_video --video test_video/any/car_evening.mp4 --tracker csrt`

### Параметры

* `-v`, `--video` - Путь к видео - **Обязательный праметр**
* `-t`, `--tracker` - Название трекера. Возможные значения "csrt", "kcf", "boosting", "mil", "tld", "medianflow", "mosse". По умолчанию *kcf*.

### Выбрать объект для трекинга

Нажать клавишу `a`; Выбрать с помощью мыши объект, нажать `enter`.

### Сохранить кадр

Нажать клавишу `s`; Сохранено будет в папке saving.

### Выход

Нажать клавишу `Esc` или закрыть окно.

## Пример работы программы

После инциализации

<div style="text-align:center"><img alt="Трекинг" src="readme_images/tracker00.png" width="100%" vspace="15" hspace="15"></div>

Трекинг

<div style="text-align:center"><img alt="Трекинг" src="readme_images/tracker01.png" width="100%" vspace="15" hspace="15"></div>

Объект "потерялся"

<div style="text-align:center"><img alt="Трекинг" src="readme_images/tracker02.png" width="100%" vspace="15" hspace="15"></div>
