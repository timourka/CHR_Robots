# MEdu Python SDK 0.6.8 — документация по управлению манипулятором

Актуально для версии SDK: **0.6.8** (по HTML‑инструкции).

Документ описывает, как с помощью Python управлять манипулятором MEdu через приложение **M Control**: подключение, движение, стриминг, работа с гриппером и конвейером, GPIO и аудио.

---

## 1. Требования и подготовка окружения

### 1.1. Версия Python

Рекомендуется использовать **Python 3.12** в отдельном виртуальном окружении:

```bash
python3.12 -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip setuptools wheel
```

### 1.2. Сеть

- ПК с SDK и манипулятор должны «видеть» друг друга по сети (локально или через интернет).
- Адрес манипулятора/брокера будет использоваться как `host`.

---

## 2. Архитектура SDK (коротко)

- **Клиент**: ваш Python‑скрипт, использующий SDK.
- **Сервер (pm_develop_api)**: компонент на манипуляторе, принимает команды и отдает ответы.
- **M Control**: приложение на ПК/планшете, через которое также можно управлять манипулятором.

Команды и данные ходят по **MQTT**. SDK всё это скрывает — вы работаете через методы класса `MEdu`.

---

## 3. Типы команд в SDK

SDK использует следующие типы вызовов:

- **Синхронные** — блокируют код до завершения (обычно без суффикса).
- **Асинхронные** — имеют суффикс `_async` (используются с `await`).
- **Асинхронные с ожиданием** — обёртки с `*_async_await`, удобны в `asyncio`.
- **no_wait** — команды, которые не ждут результата (`*_no_wait`).
- **Стриминговые** — команды непрерывного управления: скорости, поза, суставы.

Примеры обозначений:

```python
manipulator.get_control()                  # синхронный
await manipulator.get_control_async_await()  # async/await
manipulator.get_control_no_wait()          # fire-and-forget
```

---

## 4. Базовое подключение и захват управления

### 4.1. Инициализация MEdu

```python
from sdk.manipulators.medu import MEdu

host = "192.168.88.182"  # IP манипулятора / брокера MQTT
client_id = "my_client"  # любой уникальный идентификатор
login = "user_login"     # логин
password = "user_pass"   # пароль

manipulator = MEdu(host, client_id, login, password)
manipulator.connect()       # установить соединение
manipulator.get_control()   # захватить управление
```

> Рекомендуется завернуть подключение в `try/except`, чтобы корректно обрабатывать сетевые ошибки.

---

## 5. Движение по суставам (joint space)

### 5.1. `move_to_angles` — синхронное движение

```python
manipulator.move_to_angles(
    povorot_osnovaniya=0.05,   # основание, рад
    privod_plecha=-0.35,       # плечо, рад
    privod_strely=-0.75,       # стрела, рад
    v_osnovaniya=0.0,          # скорость основания, рад/с
    v_plecha=0.0,              # скорость плеча, рад/с
    v_strely=0.0,              # скорость стрелы, рад/с
    velocity_factor=0.1,       # коэффициент скорости [0..1]
    acceleration_factor=0.1,   # коэффициент ускорения [0..1]
    # timeout_seconds=60.0,
    # throw_error=True,
)
```

**Параметры (основное):**

- `povorot_osnovaniya`, `privod_plecha`, `privod_strely`: целевые углы в радианах (обязательные).
- `v_osnovaniya`, `v_plecha`, `v_strely`: скорости суставов (если 0 — берётся значение по умолчанию).
- `velocity_factor`: доля от максимальной скорости.
- `acceleration_factor`: доля от максимального ускорения.
- `timeout_seconds`: таймаут ожидания исполнения.
- `throw_error`: выбрасывать исключение при ошибке/таймауте.

### 5.2. Асинхронные и no_wait‑варианты

В SDK для большинства команд применяются следующие варианты:

```python
# асинхронно (внутри async-функции)
await manipulator.move_to_angles_async(
    povorot_osnovaniya=0.0,
    privod_plecha=0.5,
    privod_strely=-0.5,
)

# обёртка с ожиданием
await manipulator.move_to_angles_async_await(
    povorot_osnovaniya=0.1,
    privod_plecha=0.4,
    privod_strely=-0.4,
)

# без ожидания завершения
manipulator.move_to_angles_no_wait(
    povorot_osnovaniya=0.1,
    privod_plecha=0.4,
    privod_strely=-0.4,
)
```

---

## 6. Движение по декартовым координатам

Для работы с декартовыми координатами используются классы параметров:

- `MoveCoordinatesParamsPosition(x, y, z)`
- `MoveCoordinatesParamsOrientation(x, y, z, w)`
- `PlannerType` (например, `PlannerType.LIN`)

### 6.1. `move_to_coordinates`

```python
from sdk.commands.move_coordinates_command import (
    MoveCoordinatesParamsPosition,
    MoveCoordinatesParamsOrientation,
)
from sdk.utils.enums import PlannerType

position = MoveCoordinatesParamsPosition(0.32, -0.004, 0.25)
orientation = MoveCoordinatesParamsOrientation(0.0, 0.0, 0.0, 1.0)

manipulator.move_to_coordinates(
    position,
    orientation,
    velocity_scaling_factor=0.1,
    acceleration_scaling_factor=0.1,
    planner_type=PlannerType.LIN,
    timeout_seconds=30.0,
    throw_error=True,
)
```

**Параметры:**

- `position`: объект с полями `x, y, z`.
- `orientation`: кватернион ориентации `x, y, z, w`.
- `velocity_scaling_factor`: масштаб максимальной скорости движения.
- `acceleration_scaling_factor`: масштаб максимального ускорения.
- `planner_type`: тип планировщика траектории (например, линейный `LIN`).
- `timeout_seconds`, `throw_error`: аналогично `move_to_angles`.

**Замечание:** при ошибках планирования траектории задавайте координаты с большей точностью (не «круглые» числа, а реальные значения, считаемые с робота).

---

## 7. Движение по дуге — `arc_motion`

```python
from sdk.commands.arc_motion import ArcMotion, Pose, Position, Orientation

target = Pose(
    position=Position(target_x, target_y, target_z),
    orientation=Orientation(),  # или заданный кватернион
)

center_arc = Pose(
    position=Position(center_x, center_y, center_z),
    orientation=Orientation(),
)

manipulator.arc_motion(
    target,
    center_arc,
    step=0.05,
    count_point_arc=50,
    max_velocity_scaling_factor=0.5,
    max_acceleration_scaling_factor=0.5,
    # timeout_seconds=60.0,
    # throw_error=True,
)
```

**Основные параметры:**

- `target`: целевая поза (конец дуги).
- `center_arc`: поза центра дуги.
- `step`: шаг по дуге (чем меньше, тем плавнее, но больше точек).
- `count_point_arc`: количество промежуточных точек.
- `max_velocity_scaling_factor`, `max_acceleration_scaling_factor`: ограничения скорости и ускорения.

---

## 8. Работа с гриппером и насадками

### 8.1. Включение питания наконечника — `nozzle_power`

Перед управлением гриппером/вакуумом **обязательно** включить питание:

```python
manipulator.nozzle_power(True)   # включить питание
# ...
manipulator.nozzle_power(False)  # выключить питание
```

Есть также `nozzle_power_no_wait` и асинхронный вариант `nozzle_power_async`.

### 8.2. Управление гриппером — `manage_gripper`

Через манипулятор:

```python
# питание уже включено
manipulator.nozzle_power(True)

# Повернуть насадку и сжать гриппер
manipulator.manage_gripper(
    rotation=20,   # угол насадки (°)
    gripper=10,    # степень сжатия (°/условные единицы)
)

# Только изменить степень сжатия
manipulator.manage_gripper(
    rotation=None,
    gripper=30,
)
```

Варианты:

- `manage_gripper` — синхронно.
- `manage_gripper_no_wait` — без ожидания ответа.
- `manage_gripper_async` — асинхронно.

### 8.3. Использование классов насадок (опционально)

Если SDK содержит класс `GripperAttachment`:

```python
from sdk.attachments.gripper_attachment import GripperAttachment

manipulator.nozzle_power(True)
gripper = GripperAttachment(manipulator)

gripper.activate(rotation=20, gripper=10)
gripper.deactivate()
```

---

## 9. Стриминг движений (серво‑режимы)

SDK поддерживает 3 режима серво‑управления:

- `TWIST` — управление **скоростями** (линейные + угловые).
- `POSE` — управление **целевой позой**.
- `JOINT_JOG` — управление **углами суставов**.

### 9.1. Переключение режимов

```python
from sdk.utils.enums import ServoControlType

# Универсальный метод
manipulator.set_servo_control_type(ServoControlType.TWIST)
manipulator.set_servo_control_type(ServoControlType.POSE)
manipulator.set_servo_control_type(ServoControlType.JOINT_JOG)

# Короткие синонимы
manipulator.set_servo_twist_mode()
manipulator.set_servo_pose_mode()
manipulator.set_servo_joint_jog_mode()
```

### 9.2. Стриминг скоростей — `stream_cartesian_velocities`

```python
# Включаем режим TWIST
manipulator.set_servo_twist_mode()

linear_vel = {"x": 0.02, "y": 0.0, "z": 0.0}
angular_vel = {"rx": 0.0, "ry": 0.0, "rz": 0.01}

manipulator.stream_cartesian_velocities(linear_vel, angular_vel)
```

Можно отправлять эти команды циклом с небольшим интервалом (например, 50–100 мс).

### 9.3. Стриминг позы — `stream_coordinates`

```python
from sdk.commands.move_coordinates_command import (
    MoveCoordinatesParamsPosition,
    MoveCoordinatesParamsOrientation,
)

manipulator.set_servo_pose_mode()

position = MoveCoordinatesParamsPosition(0.27, 0.0, 0.15)
orientation = MoveCoordinatesParamsOrientation(0.0, 0.0, 0.0, 1.0)

manipulator.stream_coordinates(position, orientation)
```

### 9.4. Стриминг суставов — `stream_joint_angles`

```python
manipulator.set_servo_joint_jog_mode()

manipulator.stream_joint_angles(
    povorot_osnovaniya=0.5,
    privod_plecha=1.0,
    privod_strely=0.8,
    v_osnovaniya=0.2,
    v_plecha=0.1,
    v_strely=0.15,
)
```

---

## 10. Программы на роботе

SDK позволяет запускать:

- готовые программы;
- JSON‑программы;
- Python‑скрипты на роботе.

### 10.1. Готовая программа — `run_program`

```python
manipulator.run_program("edum/default")
```

### 10.2. JSON‑программа — `run_program_json`

```python
program_json = {
    "Root": [
        {
            "Move": {
                "content": [
                    {"Point": {"positions": [0.3, -0.3, -0.4], "time": 0.5}}
                ],
                "type": "Simple",
            }
        }
    ]
}

manipulator.run_program_json("program_1", program_json)
```

### 10.3. Python‑код на роботе — `run_python_program`

```python
manipulator.run_python_program("print('Hello from MEdu!')")
```

---

## 11. Остановка движения

### 11.1. `stop_movement`

```python
manipulator.stop_movement(timeout_seconds=5.0)
```

Останавливает текущее движение манипулятора.

---

## 12. Получение состояния и подписки

### 12.1. Текущее состояние

```python
joints = manipulator.get_joint_state()              # углы суставов
home_pos = manipulator.get_home_position()          # домашняя позиция
pose = manipulator.get_cartesian_coordinates()      # текущие координаты TCP
```

Тип возвращаемых структур зависит от реализации SDK (словарь / dataclass).

### 12.2. Подписка на аппаратные ошибки

```python
def on_hardware_error(data: dict):
    # data: {"type": int, "message": "...", ...}
    print("Hardware error:", data)

manipulator.subscribe_hardware_error(on_hardware_error)

# ... позже
manipulator.unsubscribe_hardware_error()
```

---

## 13. Конвейерная лента (MGbot)

В SDK конвейер доступен как объект `manipulator.mgbot_conveyer`.

### 13.1. Управление

```python
# Установить скорость мотора (0..100)
manipulator.mgbot_conveyer.set_speed_motors(10)

# Повернуть сервопривод (градусы)
manipulator.mgbot_conveyer.set_servo_angle(45)

# Установить цвет светодиода (R,G,B: 0..255)
manipulator.mgbot_conveyer.set_led_color(255, 0, 0)

# Показать текст на дисплее
manipulator.mgbot_conveyer.display_text("Hello")

# Звуковой сигнал (1..15)
manipulator.mgbot_conveyer.set_buzz_tone(10)
```

### 13.2. Чтение датчиков

```python
sensor_data = manipulator.mgbot_conveyer.get_sensors_data(True)

# Ожидаемые поля:
# sensor_data["DistanceSensor"]
# sensor_data["ColorSensor"] -> {"R":..., "G":..., "B":..., "Prox":...}
# sensor_data["Prox"]
```

---

## 14. GPIO

Позволяет управлять внешними устройствами/индикаторами.

### 14.1. Запись и чтение GPIO

```python
# Имя пина зависит от конфигурации, пример:
gpio_name = "/dev/gpiochip4/e1_pin"

# Запись
manipulator.write_gpio(
    gpio_name,
    value=1,               # 1 — включить, 0 — выключить
    timeout_seconds=0.5,
    throw_error=False,
)

# Чтение
value = manipulator.get_gpio_value(
    gpio_name,
    timeout_seconds=0.5,
    throw_error=True,
)
print("GPIO value:", value)
```

> `get_gpio_value` доступен только в синхронном виде.

---

## 15. Воспроизведение аудио

### 15.1. `play_audio`

```python
try:
    manipulator.play_audio("start.wav", timeout_seconds=10.0, throw_error=True)
    print("Аудиофайл воспроизведён")
except Exception as e:
    print("Ошибка воспроизведения аудио:", e)
```

**Параметры:**

- `file_name`: имя файла (должен существовать на стороне робота).
- `timeout_seconds`, `throw_error`: стандартные параметры обработки ошибок.

---

## 16. Минимальный пример целиком

```python
from sdk.manipulators.medu import MEdu
from sdk.commands.move_coordinates_command import (
    MoveCoordinatesParamsPosition,
    MoveCoordinatesParamsOrientation,
)
from sdk.utils.enums import PlannerType

HOST = "192.168.88.182"
CLIENT_ID = "my_client"
LOGIN = "user"
PASSWORD = "pass"


def main():
    manipulator = MEdu(HOST, CLIENT_ID, LOGIN, PASSWORD)

    try:
        manipulator.connect()
        manipulator.get_control()

        # Движение по суставам
        manipulator.move_to_angles(
            povorot_osnovaniya=0.0,
            privod_plecha=-0.3,
            privod_strely=-0.7,
            velocity_factor=0.2,
            acceleration_factor=0.2,
        )

        # Движение по координатам
        position = MoveCoordinatesParamsPosition(0.32, -0.004, 0.25)
        orientation = MoveCoordinatesParamsOrientation(0.0, 0.0, 0.0, 1.0)

        manipulator.move_to_coordinates(
            position,
            orientation,
            velocity_scaling_factor=0.1,
            acceleration_scaling_factor=0.1,
            planner_type=PlannerType.LIN,
        )

        # Захват объекта гриппером
        manipulator.nozzle_power(True)
        manipulator.manage_gripper(rotation=0, gripper=20)

        # Лёгкий звуковой сигнал
        manipulator.play_audio("start.wav", timeout_seconds=5.0, throw_error=False)

    except Exception as e:
        print("Ошибка работы с манипулятором:", e)
    finally:
        # Остановить движения и (опционально) отпустить управление
        try:
            manipulator.stop_movement(timeout_seconds=5.0)
        except Exception:
            pass


if __name__ == "__main__":
    main()
```

---

## 17. Рекомендации по обработке ошибок

- Любые сетевые/аппаратные операции оборачивайте в `try/except`.
- Логируйте текст ошибок (`e`) и, по возможности, сохраняйте их в файл.
- При сложных ошибках прикладывайте логи при обращении в техподдержку ПРОМОБОТ.

