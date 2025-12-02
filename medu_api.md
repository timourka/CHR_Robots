# Документация по управлению манипулятором **MEdu**

Файл: `sdk/manipulators/medu.py`  
Класс: `MEdu`

Документация описывает публичные методы класса `MEdu`, используемые для управления учебным манипулятором: движение по суставам, управление питанием наконечника, гриппером, вакуумом, стриминг движений, подписки на состояние и чтение I²C.

---

## Содержание

1. [Создание объекта и служебные методы](#1-создание-объекта-и-служебные-методы)
   - [`__init__`](#medu__init__)
   - [`_cleanup_finished_commands`](#medu_cleanup_finished_commands)
   - [`process_message`](#meduprocess_messagetopic-str-payload-str--none)
2. [Движение по суставам (углы)](#2-движение-по-суставам-углы)
   - [`move_to_angles`](#medumove_to_angles)
   - [`move_to_angles_async`](#medumove_to_angles_async)
   - [`move_to_angles_async_await`](#medumove_to_angles_async_await)
   - [`move_to_angles_no_wait`](#medumove_to_angles_no_wait)
3. [Питание наконечника](#3-питание-наконечника)
   - [`nozzle_power`](#medunozzle_power)
   - [`nozzle_power_async`](#medunozzle_power_async)
   - [`nozzle_power_no_wait`](#medunozzle_power_no_wait)
4. [Управление гриппером](#4-управление-гриппером)
   - [`manage_gripper`](#medumanage_gripper)
   - [`manage_gripper_async`](#medumanage_gripper_async)
   - [`manage_gripper_no_wait`](#medumanage_gripper_no_wait)
5. [Управление вакуумом](#5-управление-вакуумом)
   - [`manage_vacuum`](#medumanage_vacuum)
   - [`manage_vacuum_async`](#medumanage_vacuum_async)
   - [`manage_vacuum_no_wait`](#medumanage_vacuum_no_wait)
6. [Стриминг углов](#6-стриминг-углов)
   - [`stream_joint_angles`](#medustream_joint_angles)
   - [`stream_joint_angles_async`](#medustream_joint_angles_async)
7. [Подписка на состояние суставов](#7-подписка-на-состояние-суставов)
   - [`subscribe_to_joint_state`](#medusubscribe_to_joint_state)
   - [`unsubscribe_from_joint_state`](#meduunsubscribe_from_joint_state)
8. [Чтение I²C](#8-чтение-i²c)
   - [`get_i2c_value`](#meduget_i2c_value)

---

## 1. Создание объекта и служебные методы

### `MEdu.__init__`

```python
def __init__(self, host: str, client_id: str, login: str, password: str) -> None:
    ...
```

**Назначение:**  
Создание объекта манипулятора MEdu и настройка соединения с брокером/роботом.

**Параметры:**

- `host`: адрес брокера или робота (IP/домен).
- `client_id`: идентификатор клиента (для MQTT/соединения).
- `login`: логин для авторизации.
- `password`: пароль для авторизации.

> Обычно после создания объекта используется метод базового класса (например, `connect()`), чтобы фактически установить соединение.

---

### `MEdu._cleanup_finished_commands()`

```python
def _cleanup_finished_commands(self) -> None:
    ...
```

**Назначение:**  
Внутренний метод, очищающий словарь активных команд `self.active_commands` от завершённых.

**Как работает:**

- Обходит пары `(command_id, command)` в `self.active_commands`.
- Удаляет те, у кого промис (`command.promise`) уже не активен (`is_active == False`).

**Применение:**  
Вызывается внутри `process_message`. В прикладном коде напрямую обычно не используется.

---

### `MEdu.process_message(topic: str, payload: str) -> None`

```python
def process_message(self, topic: str, payload: str) -> None:
    ...
```

**Назначение:**  
Обработка входящих сообщений (обычно вызывается слоем коммуникации, например MQTT-клиентом).

**Поведение (основное):**

1. Очищает завершённые команды через `_cleanup_finished_commands()`.
2. Если `topic == "/command_result"`:
   - Парсит `payload` как JSON.
   - Достаёт `command_id` (`data.get("id")`).
   - Находит команду в `self.active_commands` и передаёт ей сообщение (`command.process_message(topic, payload)`).
3. Если `topic == JOINT_INFO_TOPIC` и задан `self.joint_state_callback`:
   - Парсит `payload` как JSON.
   - Вызывает `self.joint_state_callback(data)`.
4. В конце вызывает `super().process_message(topic, payload)` (обработка на уровне базового класса).

---

## 2. Движение по суставам (углы)

### `MEdu.move_to_angles`

```python
def move_to_angles(
    self,
    povorot_osnovaniya: float,
    privod_plecha: float,
    privod_strely: float,
    v_osnovaniya: float = 0.0,
    v_plecha: float = 0.0,
    v_strely: float = 0.0,
    velocity_factor: float = 0.1,
    acceleration_factor: float = 0.1,
    timeout_seconds: float = 60.0,
    throw_error: bool = True,
) -> None:
    ...
```

**Назначение:**  
Блокирующее (с ожиданием) перемещение манипулятора по суставам до заданных углов.

**Параметры:**

- `povorot_osnovaniya`: целевой угол основания, рад.
- `privod_plecha`: целевой угол плеча, рад.
- `privod_strely`: целевой угол стрелы, рад.
- `v_osnovaniya`: скорость основания, рад/с.
- `v_plecha`: скорость плеча, рад/с.
- `v_strely`: скорость стрелы, рад/с.
- `velocity_factor`: коэффициент скорости (0.0–1.0), доля от максимальной.
- `acceleration_factor`: коэффициент ускорения (0.0–1.0).
- `timeout_seconds`: таймаут ожидания выполнения команды.
- `throw_error`: если `True`, при ошибке/таймауте выбрасывается исключение.

**Возвращаемое значение:**  
`None`. При успешном завершении просто возвращается.

**Пример использования:**

```python
medu.move_to_angles(
    povorot_osnovaniya=0.0,
    privod_plecha=0.5,
    privod_strely=-0.5,
    velocity_factor=0.3,
    acceleration_factor=0.3,
)
```

---

### `MEdu.move_to_angles_async`

```python
async def move_to_angles_async(
    self,
    povorot_osnovaniya: float,
    privod_plecha: float,
    privod_strely: float,
    v_osnovaniya: float = 0.0,
    v_plecha: float = 0.0,
    v_strely: float = 0.0,
    velocity_factor: float = 0.1,
    acceleration_factor: float = 0.1,
    timeout_seconds: float = 60.0,
    throw_error: bool = True,
) -> None:
    ...
```

**Назначение:**  
Асинхронная версия `move_to_angles`. Позволяет интегрировать управление в `asyncio`-приложения.

**Особенности:**

- Команда отправляется и ожидается через `await command.promise.async_result()`.
- Интерфейс параметров полностью совпадает с синхронным методом.

**Пример:**

```python
await medu.move_to_angles_async(
    povorot_osnovaniya=0.0,
    privod_plecha=0.5,
    privod_strely=-0.5,
)
```

---

### `MEdu.move_to_angles_async_await`

```python
async def move_to_angles_async_await(
    self,
    povorot_osnovaniya: float,
    privod_plecha: float,
    privod_strely: float,
    v_osnovaniya: float = 0.0,
    v_plecha: float = 0.0,
    v_strely: float = 0.0,
    velocity_factor: float = 0.1,
    acceleration_factor: float = 0.1,
    timeout_seconds: float = 60.0,
    throw_error: bool = True,
) -> None:
    ...
```

**Назначение:**  
Тонкая обёртка над `move_to_angles_async`, которая просто вызывает `await self.move_to_angles_async(...)`.

**Использование:**  
Аналогично `move_to_angles_async`. Добавлена для унификации API.

---

### `MEdu.move_to_angles_no_wait`

```python
def move_to_angles_no_wait(
    self,
    povorot_osnovaniya: float,
    privod_plecha: float,
    privod_strely: float,
    v_osnovaniya: float = 0.0,
    v_plecha: float = 0.0,
    v_strely: float = 0.0,
    velocity_factor: float = 0.1,
    acceleration_factor: float = 0.1,
) -> None:
    ...
```

**Назначение:**  
Отправка команды движения по суставам **без ожидания** её выполнения.

**Особенности:**

- Состояние выполнения не контролируется этим методом.
- Полезно при потоковом управлении, когда состояние отслеживается по обратной связи.

---

## 3. Питание наконечника

### `MEdu.nozzle_power`

```python
def nozzle_power(
    self,
    power: bool,
    timeout_seconds: float = 60.0,
    throw_error: bool = True,
) -> None:
    ...
```

**Назначение:**  
Включение/выключение питания на наконечнике (стреле) манипулятора.  
Питание необходимо для работы гриппера и вакуумного захвата.

**Параметры:**

- `power`: `True` — включить питание, `False` — выключить.
- `timeout_seconds`: таймаут ожидания подтверждения.
- `throw_error`: выбрасывать ли исключение при ошибке.

**Пример:**

```python
medu.nozzle_power(True)   # включить питание
medu.nozzle_power(False)  # выключить питание
```

---

### `MEdu.nozzle_power_async`

```python
async def nozzle_power_async(
    self,
    power: bool,
    timeout_seconds: float = 60.0,
    throw_error: bool = True,
) -> None:
    ...
```

Асинхронная версия `nozzle_power`. Параметры и логика аналогичны, используется `await command.promise.async_result()`.

---

### `MEdu.nozzle_power_no_wait`

```python
def nozzle_power_no_wait(self, power: bool) -> None:
    ...
```

**Назначение:**  
Включение/выключение питания без ожидания результата.

- Использует неблокирующую команду (`NoWaitCommand`).
- Не возвращает информацию об успехе/ошибке.

---

## 4. Управление гриппером

### `MEdu.manage_gripper`

```python
def manage_gripper(
    self,
    rotation: int | None = None,
    gripper: int | None = None,
    timeout_seconds: float = 60.0,
    throw_error: bool = True,
) -> None:
    ...
```

**Назначение:**  
Управление поворотом насадки и сжатием гриппера (блокирующее).

**Параметры:**

- `rotation`: угол поворота насадки (градусы), или `None`, если не изменяем.
- `gripper`: угол/степень сжатия гриппера (градусы), или `None`.
- `timeout_seconds`: таймаут ожидания результата.
- `throw_error`: выбрасывать ли исключение при ошибке.

**Важно:**

- Нельзя вызывать с `rotation is None` и `gripper is None` одновременно — будет `ValueError`.
- Для работы должен быть включён `nozzle_power(True)`.

---

### `MEdu.manage_gripper_async`

```python
async def manage_gripper_async(
    self,
    rotation: int | None = None,
    gripper: int | None = None,
    timeout_seconds: float = 60.0,
    throw_error: bool = True,
) -> None:
    ...
```

Асинхронная версия `manage_gripper`:

- Проверяет, что не оба аргумента `None`.
- Отправляет команду и ожидает `await command.promise.async_result()`.

---

### `MEdu.manage_gripper_no_wait`

```python
def manage_gripper_no_wait(
    self,
    rotation: int | None = None,
    gripper: int | None = None,
) -> None:
    ...
```

**Назначение:**  
Отправка команды управления гриппером без ожидания результата.

**Особенности:**

- При `rotation is None` и `gripper is None` → `ValueError`.
- Используется `NoWaitCommand` с типом `"gripper_control"`.

---

## 5. Управление вакуумом

### `MEdu.manage_vacuum`

```python
def manage_vacuum(
    self,
    rotation: int | None = None,
    power_supply: bool | None = None,
    timeout_seconds: float = 60.0,
    throw_error: bool = True,
) -> None:
    ...
```

**Назначение:**  
Управление вакуумным захватом и поворотом его насадки (блокирующее).

**Параметры:**

- `rotation`: угол поворота насадки (градусы) или `None`.
- `power_supply`: `True` — включить вакуум; `False` — выключить; `None` — не менять.
- `timeout_seconds`: таймаут ожидания результата.
- `throw_error`: выбрасывать ли исключение при ошибке.

**Ограничения:**

- Если `rotation is None` и `power_supply is None` — выбрасывается `ValueError`.
- Требуется включённое питание (`nozzle_power(True)`).

---

### `MEdu.manage_vacuum_async`

```python
async def manage_vacuum_async(
    self,
    rotation: int | None = None,
    power_supply: bool | None = None,
    timeout_seconds: float = 60.0,
    throw_error: bool = True,
) -> None:
    ...
```

Асинхронная версия `manage_vacuum`:

- Аналогична по параметрам и проверкам.
- Завершение ожидается через `await command.promise.async_result()`.

---

### `MEdu.manage_vacuum_no_wait`

```python
def manage_vacuum_no_wait(
    self,
    rotation: int | None = None,
    power_supply: bool | None = None,
) -> None:
    ...
```

**Назначение:**  
Управление вакуумом без ожидания результата.

**Особенности:**

- Нельзя вызывать с обоими параметрами `None` — `ValueError`.
- Отправляет `NoWaitCommand` с типом `"vacuum_control"`.

---

## 6. Стриминг углов

### `MEdu.stream_joint_angles`

```python
def stream_joint_angles(
    self,
    povorot_osnovaniya: float,
    privod_plecha: float,
    privod_strely: float,
    v_osnovaniya: float = 0.0,
    v_plecha: float = 0.0,
    v_strely: float = 0.0,
) -> None:
    ...
```

**Назначение:**  
Разовая «стриминговая» отправка углов и скоростей суставов.

**Параметры:**

- `povorot_osnovaniya`: угол основания, рад.
- `privod_plecha`: угол плеча, рад.
- `privod_strely`: угол стрелы, рад.
- `v_osnovaniya`: скорость основания, рад/с.
- `v_plecha`: скорость плеча, рад/с.
- `v_strely`: скорость стрелы, рад/с.

**Поведение:**  
Формируются словари `positions` и `velocities`, далее вызывается метод базового класса:

```python
self.stream_joint_positions(positions, velocities)
```

---

### `MEdu.stream_joint_angles_async`

```python
async def stream_joint_angles_async(
    self,
    povorot_osnovaniya: float,
    privod_plecha: float,
    privod_strely: float,
    v_osnovaniya: float = 0.0,
    v_plecha: float = 0.0,
    v_strely: float = 0.0,
) -> None:
    ...
```

Асинхронная версия:

- Параметры те же.
- Внутри вызывает:

```python
await self.stream_joint_positions_async(positions, velocities)
```

---

## 7. Подписка на состояние суставов

### `MEdu.subscribe_to_joint_state`

```python
def subscribe_to_joint_state(self, callback: Callable[[dict], None]) -> None:
    ...
```

**Назначение:**  
Подписка на обновления состояния суставов манипулятора.

**Параметры:**

- `callback`: функция вида `callback(data: dict)`, где `data` — словарь, полученный из JSON-сообщения по теме `JOINT_INFO_TOPIC` (например, углы, скорости, состояния приводов).

**Поведение:**

- Сохраняет колбэк в `self.joint_state_callback`.
- Подписывается на `JOINT_INFO_TOPIC` через `self.message_bus`.

**Когда вызывается callback:**  
Каждый раз, когда `process_message` получает сообщение по `JOINT_INFO_TOPIC`.

---

### `MEdu.unsubscribe_from_joint_state`

```python
def unsubscribe_from_joint_state(self) -> None:
    ...
```

**Назначение:**  
Отписка от получения обновлений состояния суставов.

**Поведение:**

- Очищает `self.joint_state_callback`.
- Делает `self.message_bus.unsubscribe(JOINT_INFO_TOPIC)`.

---

## 8. Чтение I²C

### `MEdu.get_i2c_value`

```python
def get_i2c_value(
    self,
    name: str,
    timeout_seconds: float = 60.0,
    throw_error: bool = True,
) -> Optional[float]:
    ...
```

**Назначение:**  
Синхронное чтение значения по I²C-каналу по имени.

**Параметры:**

- `name`: строковое имя канала/датчика.
- `timeout_seconds`: таймаут ожидания ответа.
- `throw_error`: выбрасывать ли исключение при ошибке.

**Возвращаемое значение:**

- Значение `float` из поля `data.value` ответа команды, либо `None`, если значение отсутствует.

**Пример:**

```python
temperature = medu.get_i2c_value("temperature_sensor")
if temperature is not None:
    print("Температура:", temperature)
```

---
