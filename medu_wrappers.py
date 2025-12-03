"""
medu_wrappers.py — простые обёртки для MEdu SDK (только синхронные функции).

Особенности:
- НЕТ классов и общих ensure-хелперов.
- НЕТ глобальных переменных (кроме импортов).
- Каждая функция сама проверяет свои параметры (тип + диапазон).
- Вызовы SDK всегда внутри try/except.
- В except пишем лог в консоль и возвращаем None.

Числовые диапазоны здесь заданы "разумными по умолчанию".
При необходимости подправь их под свои реальные ограничения робота.
"""

from sdk.manipulators.medu import MEdu
from sdk.commands.move_coordinates_command import (
    MoveCoordinatesParamsPosition,
    MoveCoordinatesParamsOrientation,
)
from sdk.commands.arc_motion import Pose, Position, Orientation
from sdk.utils.enums import ServoControlType  # PlannerType в новой версии SDK нет

# ---------------------------------------------------------------------------
# 1. Подключение и получение управления
# ---------------------------------------------------------------------------

def medu_connect(host: str, client_id: str, login: str, password: str):
    """
    Создать объект MEdu, подключиться и захватить управление.
    Возвращает объект manipulator или None при ошибке.
    """
    try:
        # Простейшая проверка строк
        if not isinstance(host, str) or not host.strip():
            raise ValueError("host должен быть непустой строкой")
        if not isinstance(client_id, str) or not client_id.strip():
            raise ValueError("client_id должен быть непустой строкой")
        if not isinstance(login, str) or not login.strip():
            raise ValueError("login должен быть непустой строкой")
        if not isinstance(password, str) or not password.strip():
            raise ValueError("password должен быть непустой строкой")

        manipulator = MEdu(host, client_id, login, password)

        # Подключение + захват управления — тоже в try
        manipulator.connect()
        manipulator.get_control()

        return manipulator

    except Exception as e:
        print(f"[medu_connect] Ошибка подключения: {e}")
        return None


# ---------------------------------------------------------------------------
# 2. Движение по суставам (joint space)
# ---------------------------------------------------------------------------

def medu_move_to_angles(
    manipulator,
    povorot_osnovaniya,
    privod_plecha,
    privod_strely,
    v_osnovaniya=0.0,
    v_plecha=0.0,
    v_strely=0.0,
    velocity_factor=0.1,
    acceleration_factor=0.1,
    timeout_seconds=60.0,
    throw_error=True,
):
    """
    Обёртка для manipulator.move_to_angles(...) с проверкой параметров.
    """

    try:
        if manipulator is None:
            raise ValueError("manipulator == None")

        # Пример ограничений для углов (рад)
        joint_min = -3.14
        joint_max = 3.14

        if not isinstance(povorot_osnovaniya, (int, float)):
            raise TypeError("povorot_osnovaniya должен быть числом")
        if not joint_min <= float(povorot_osnovaniya) <= joint_max:
            raise ValueError("povorot_osnovaniya вне диапазона [-3.14, 3.14]")

        if not isinstance(privod_plecha, (int, float)):
            raise TypeError("privod_plecha должен быть числом")
        if not joint_min <= float(privod_plecha) <= joint_max:
            raise ValueError("privod_plecha вне диапазона [-3.14, 3.14]")

        if not isinstance(privod_strely, (int, float)):
            raise TypeError("privod_strely должен быть числом")
        if not joint_min <= float(privod_strely) <= joint_max:
            raise ValueError("privod_strely вне диапазона [-3.14, 3.14]")

        # Скорости суставов — просто проверка на число
        for name, value in [
            ("v_osnovaniya", v_osnovaniya),
            ("v_plecha", v_plecha),
            ("v_strely", v_strely),
        ]:
            if not isinstance(value, (int, float)):
                raise TypeError(f"{name} должен быть числом")

        # Коэффициенты скорости/ускорения [0..1]
        if not isinstance(velocity_factor, (int, float)):
            raise TypeError("velocity_factor должен быть числом")
        if not 0.0 <= float(velocity_factor) <= 1.0:
            raise ValueError("velocity_factor должен быть в диапазоне [0.0, 1.0]")

        if not isinstance(acceleration_factor, (int, float)):
            raise TypeError("acceleration_factor должен быть числом")
        if not 0.0 <= float(acceleration_factor) <= 1.0:
            raise ValueError("acceleration_factor должен быть в диапазоне [0.0, 1.0]")

        # timeout_seconds
        if not isinstance(timeout_seconds, (int, float)):
            raise TypeError("timeout_seconds должен быть числом")
        if float(timeout_seconds) < 0.0:
            raise ValueError("timeout_seconds не может быть отрицательным")

        if not isinstance(throw_error, bool):
            raise TypeError("throw_error должен быть bool")

        # Вызов SDK
        return manipulator.move_to_angles(
            float(povorot_osnovaniya),
            float(privod_plecha),
            float(privod_strely),
            float(v_osnovaniya),
            float(v_plecha),
            float(v_strely),
            float(velocity_factor),
            float(acceleration_factor),
            timeout_seconds=float(timeout_seconds),
            throw_error=throw_error,
        )

    except Exception as e:
        print(f"[medu_move_to_angles] Ошибка: {e}")
        return None


# ---------------------------------------------------------------------------
# 3. Движение по декартовым координатам
# ---------------------------------------------------------------------------

def medu_move_to_coordinates(
    manipulator,
    x,
    y,
    z,
    ox,
    oy,
    oz,
    ow,
    velocity_scaling_factor=0.1,
    acceleration_scaling_factor=0.1,
    planner_type=None,
    timeout_seconds=30.0,
    throw_error=True,
):
    """
    Обёртка для manipulator.move_to_coordinates(...) с проверкой параметров.
    """

    try:
        if manipulator is None:
            raise ValueError("manipulator == None")

        # Диапазоны координат (примерно для маленького робота, м)
        coord_min = -1.0
        coord_max = 1.0

        for name, value in [("x", x), ("y", y), ("z", z)]:
            if not isinstance(value, (int, float)):
                raise TypeError(f"{name} должен быть числом")
            if not coord_min <= float(value) <= coord_max:
                raise ValueError(f"{name} вне диапазона [{coord_min}, {coord_max}]")

        # Кватернион (ox, oy, oz, ow) — просто числа; диапазон [-1..1]
        for name, value in [("ox", ox), ("oy", oy), ("oz", oz), ("ow", ow)]:
            if not isinstance(value, (int, float)):
                raise TypeError(f"{name} должен быть числом")
            if not -1.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} вне диапазона [-1.0, 1.0]")

        # velocity/acceleration [0..1]
        if not isinstance(velocity_scaling_factor, (int, float)):
            raise TypeError("velocity_scaling_factor должен быть числом")
        if not 0.0 <= float(velocity_scaling_factor) <= 1.0:
            raise ValueError(
                "velocity_scaling_factor должен быть в диапазоне [0.0, 1.0]"
            )

        if not isinstance(acceleration_scaling_factor, (int, float)):
            raise TypeError("acceleration_scaling_factor должен быть числом")
        if not 0.0 <= float(acceleration_scaling_factor) <= 1.0:
            raise ValueError(
                "acceleration_scaling_factor должен быть в диапазоне [0.0, 1.0]"
            )

        if not isinstance(planner_type, PlannerType):
            raise TypeError("planner_type должен быть экземпляром PlannerType")

        if not isinstance(timeout_seconds, (int, float)):
            raise TypeError("timeout_seconds должен быть числом")
        if float(timeout_seconds) < 0.0:
            raise ValueError("timeout_seconds не может быть отрицательным")

        if not isinstance(throw_error, bool):
            raise TypeError("throw_error должен быть bool")

        position = MoveCoordinatesParamsPosition(float(x), float(y), float(z))
        orientation = MoveCoordinatesParamsOrientation(
            float(ox),
            float(oy),
            float(oz),
            float(ow),
        )

        return manipulator.move_to_coordinates(
            position,
            orientation,
            float(velocity_scaling_factor),
            float(acceleration_scaling_factor),
            planner_type,
            timeout_seconds=float(timeout_seconds),
            throw_error=throw_error,
        )

    except Exception as e:
        print(f"[medu_move_to_coordinates] Ошибка: {e}")
        return None


# ---------------------------------------------------------------------------
# 4. Движение по дуге
# ---------------------------------------------------------------------------

def medu_arc_motion(
    manipulator,
    target_x,
    target_y,
    target_z,
    center_x,
    center_y,
    center_z,
    step=0.05,
    count_point_arc=50,
    max_velocity_scaling_factor=0.5,
    max_acceleration_scaling_factor=0.5,
    timeout_seconds=60.0,
    throw_error=True,
):
    """
    Обёртка для manipulator.arc_motion(...) с проверкой параметров.
    """

    try:
        if manipulator is None:
            raise ValueError("manipulator == None")

        coord_min = -1.0
        coord_max = 1.0

        for name, value in [
            ("target_x", target_x),
            ("target_y", target_y),
            ("target_z", target_z),
            ("center_x", center_x),
            ("center_y", center_y),
            ("center_z", center_z),
        ]:
            if not isinstance(value, (int, float)):
                raise TypeError(f"{name} должен быть числом")
            if not coord_min <= float(value) <= coord_max:
                raise ValueError(f"{name} вне диапазона [{coord_min}, {coord_max}]")

        if not isinstance(step, (int, float)):
            raise TypeError("step должен быть числом")
        if float(step) <= 0.0:
            raise ValueError("step должен быть > 0")

        if not isinstance(count_point_arc, int):
            raise TypeError("count_point_arc должен быть целым числом")
        if count_point_arc <= 0:
            raise ValueError("count_point_arc должен быть > 0")

        for name, value in [
            ("max_velocity_scaling_factor", max_velocity_scaling_factor),
            ("max_acceleration_scaling_factor", max_acceleration_scaling_factor),
        ]:
            if not isinstance(value, (int, float)):
                raise TypeError(f"{name} должен быть числом")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} должен быть в диапазоне [0.0, 1.0]")

        if not isinstance(timeout_seconds, (int, float)):
            raise TypeError("timeout_seconds должен быть числом")
        if float(timeout_seconds) < 0.0:
            raise ValueError("timeout_seconds не может быть отрицательным")

        if not isinstance(throw_error, bool):
            raise TypeError("throw_error должен быть bool")

        target = Pose(
            position=Position(float(target_x), float(target_y), float(target_z)),
            orientation=Orientation(),
        )
        center_arc = Pose(
            position=Position(float(center_x), float(center_y), float(center_z)),
            orientation=Orientation(),
        )

        return manipulator.arc_motion(
            target,
            center_arc,
            float(step),
            int(count_point_arc),
            float(max_velocity_scaling_factor),
            float(max_acceleration_scaling_factor),
            timeout_seconds=float(timeout_seconds),
            throw_error=throw_error,
        )

    except Exception as e:
        print(f"[medu_arc_motion] Ошибка: {e}")
        return None


# ---------------------------------------------------------------------------
# 5. Насадка и гриппер
# ---------------------------------------------------------------------------

def medu_nozzle_power(manipulator, state: bool):
    """
    Включить/выключить питание насадки.
    """
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")
        if not isinstance(state, bool):
            raise TypeError("state должен быть bool")

        return manipulator.nozzle_power(state)

    except Exception as e:
        print(f"[medu_nozzle_power] Ошибка: {e}")
        return None


def medu_manage_gripper(manipulator, rotation=None, gripper=None):
    """
    Управление гриппером (rotation и gripper — числа или None).
    """
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")

        if rotation is not None and not isinstance(rotation, (int, float)):
            raise TypeError("rotation должен быть числом или None")

        if gripper is not None and not isinstance(gripper, (int, float)):
            raise TypeError("gripper должен быть числом или None")

        return manipulator.manage_gripper(rotation, gripper)

    except Exception as e:
        print(f"[medu_manage_gripper] Ошибка: {e}")
        return None


# ---------------------------------------------------------------------------
# 6. Серво-режимы и стриминг
# ---------------------------------------------------------------------------

def medu_set_servo_control_type(manipulator, servo_type):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")

        if not isinstance(servo_type, ServoControlType):
            raise TypeError("servo_type должен быть экземпляром ServoControlType")

        return manipulator.set_servo_control_type(servo_type)

    except Exception as e:
        print(f"[medu_set_servo_control_type] Ошибка: {e}")
        return None


def medu_set_servo_twist_mode(manipulator):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")
        return manipulator.set_servo_twist_mode()
    except Exception as e:
        print(f"[medu_set_servo_twist_mode] Ошибка: {e}")
        return None


def medu_set_servo_pose_mode(manipulator):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")
        return manipulator.set_servo_pose_mode()
    except Exception as e:
        print(f"[medu_set_servo_pose_mode] Ошибка: {e}")
        return None


def medu_set_servo_joint_jog_mode(manipulator):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")
        return manipulator.set_servo_joint_jog_mode()
    except Exception as e:
        print(f"[medu_set_servo_joint_jog_mode] Ошибка: {e}")
        return None


def medu_stream_cartesian_velocities(manipulator, linear_vel, angular_vel):
    """
    linear_vel = {'x':..., 'y':..., 'z':...}
    angular_vel = {'rx':..., 'ry':..., 'rz':...}
    """
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")

        for key in ("x", "y", "z"):
            if key not in linear_vel:
                raise ValueError(f"В linear_vel нет ключа '{key}'")
            if not isinstance(linear_vel[key], (int, float)):
                raise TypeError(f"linear_vel['{key}'] должен быть числом")

        for key in ("rx", "ry", "rz"):
            if key not in angular_vel:
                raise ValueError(f"В angular_vel нет ключа '{key}'")
            if not isinstance(angular_vel[key], (int, float)):
                raise TypeError(f"angular_vel['{key}'] должен быть числом")

        return manipulator.stream_cartesian_velocities(linear_vel, angular_vel)

    except Exception as e:
        print(f"[medu_stream_cartesian_velocities] Ошибка: {e}")
        return None


def medu_stream_coordinates(manipulator, x, y, z, ox, oy, oz, ow):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")

        for name, value in [("x", x), ("y", y), ("z", z), ("ox", ox), ("oy", oy), ("oz", oz), ("ow", ow)]:
            if not isinstance(value, (int, float)):
                raise TypeError(f"{name} должен быть числом")

        position = MoveCoordinatesParamsPosition(float(x), float(y), float(z))
        orientation = MoveCoordinatesParamsOrientation(
            float(ox),
            float(oy),
            float(oz),
            float(ow),
        )

        return manipulator.stream_coordinates(position, orientation)

    except Exception as e:
        print(f"[medu_stream_coordinates] Ошибка: {e}")
        return None


def medu_stream_joint_angles(
    manipulator,
    povorot_osnovaniya,
    privod_plecha,
    privod_strely,
    v_osnovaniya,
    v_plecha,
    v_strely,
):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")

        joint_min = -3.14
        joint_max = 3.14

        for name, value in [
            ("povorot_osnovaniya", povorot_osnovaniya),
            ("privod_plecha", privod_plecha),
            ("privod_strely", privod_strely),
        ]:
            if not isinstance(value, (int, float)):
                raise TypeError(f"{name} должен быть числом")
            if not joint_min <= float(value) <= joint_max:
                raise ValueError(f"{name} вне диапазона [{joint_min}, {joint_max}]")

        for name, value in [
            ("v_osnovaniya", v_osnovaniya),
            ("v_plecha", v_plecha),
            ("v_strely", v_strely),
        ]:
            if not isinstance(value, (int, float)):
                raise TypeError(f"{name} должен быть числом")

        return manipulator.stream_joint_angles(
            float(povorot_osnovaniya),
            float(privod_plecha),
            float(privod_strely),
            float(v_osnovaniya),
            float(v_plecha),
            float(v_strely),
        )

    except Exception as e:
        print(f"[medu_stream_joint_angles] Ошибка: {e}")
        return None


# ---------------------------------------------------------------------------
# 7. Программы
# ---------------------------------------------------------------------------

def medu_run_program(manipulator, name: str):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name должен быть непустой строкой")

        return manipulator.run_program(name)

    except Exception as e:
        print(f"[medu_run_program] Ошибка: {e}")
        return None


def medu_run_program_json(manipulator, name: str, program_json: dict):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name должен быть непустой строкой")

        if not isinstance(program_json, dict):
            raise TypeError("program_json должен быть dict")
        if "Root" not in program_json:
            raise ValueError("program_json должен содержать ключ 'Root'")

        return manipulator.run_program_json(name, program_json)

    except Exception as e:
        print(f"[medu_run_program_json] Ошибка: {e}")
        return None


def medu_run_python_program(manipulator, code: str):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")
        if not isinstance(code, str) or not code.strip():
            raise ValueError("code должен быть непустой строкой")

        return manipulator.run_python_program(code)

    except Exception as e:
        print(f"[medu_run_python_program] Ошибка: {e}")
        return None


# ---------------------------------------------------------------------------
# 8. Остановка движения и чтение состояний
# ---------------------------------------------------------------------------

def medu_stop_movement(manipulator, timeout_seconds=5.0):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")
        if not isinstance(timeout_seconds, (int, float)):
            raise TypeError("timeout_seconds должен быть числом")
        if float(timeout_seconds) < 0.0:
            raise ValueError("timeout_seconds не может быть отрицательным")

        return manipulator.stop_movement(timeout_seconds=float(timeout_seconds))

    except Exception as e:
        print(f"[medu_stop_movement] Ошибка: {e}")
        return None


def medu_get_joint_state(manipulator):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")
        return manipulator.get_joint_state()
    except Exception as e:
        print(f"[medu_get_joint_state] Ошибка: {e}")
        return None


def medu_get_home_position(manipulator):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")
        return manipulator.get_home_position()
    except Exception as e:
        print(f"[medu_get_home_position] Ошибка: {e}")
        return None


def medu_get_cartesian_coordinates(manipulator):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")
        return manipulator.get_cartesian_coordinates()
    except Exception as e:
        print(f"[medu_get_cartesian_coordinates] Ошибка: {e}")
        return None


# ---------------------------------------------------------------------------
# 9. GPIO
# ---------------------------------------------------------------------------

def medu_write_gpio(
    manipulator,
    name: str,
    value: int,
    timeout_seconds=0.5,
    throw_error=False,
):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("name должен быть непустой строкой")

        if not isinstance(value, int):
            raise TypeError("value должен быть int")
        if value not in (0, 1):
            raise ValueError("value должен быть 0 или 1")

        if not isinstance(timeout_seconds, (int, float)):
            raise TypeError("timeout_seconds должен быть числом")
        if float(timeout_seconds) < 0.0:
            raise ValueError("timeout_seconds не может быть отрицательным")

        if not isinstance(throw_error, bool):
            raise TypeError("throw_error должен быть bool")

        return manipulator.write_gpio(
            name,
            value,
            timeout_seconds=float(timeout_seconds),
            throw_error=throw_error,
        )

    except Exception as e:
        print(f"[medu_write_gpio] Ошибка: {e}")
        return None


def medu_get_gpio_value(
    manipulator,
    name: str,
    timeout_seconds=0.5,
    throw_error=False,
):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("name должен быть непустой строкой")

        if not isinstance(timeout_seconds, (int, float)):
            raise TypeError("timeout_seconds должен быть числом")
        if float(timeout_seconds) < 0.0:
            raise ValueError("timeout_seconds не может быть отрицательным")

        if not isinstance(throw_error, bool):
            raise TypeError("throw_error должен быть bool")

        return manipulator.get_gpio_value(
            name,
            timeout_seconds=float(timeout_seconds),
            throw_error=throw_error,
        )

    except Exception as e:
        print(f"[medu_get_gpio_value] Ошибка: {e}")
        return None


# ---------------------------------------------------------------------------
# 10. Конвейер MGbot
# ---------------------------------------------------------------------------

def medu_conveyor_set_speed_motors(manipulator, speed: int):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")

        if not isinstance(speed, int):
            raise TypeError("speed должен быть int")

        # Диапазон скорости 0..100 (пример)
        if not 0 <= speed <= 100:
            raise ValueError("speed должен быть в диапазоне [0, 100]")

        return manipulator.mgbot_conveyer.set_speed_motors(speed)

    except Exception as e:
        print(f"[medu_conveyor_set_speed_motors] Ошибка: {e}")
        return None


def medu_conveyor_set_servo_angle(manipulator, angle):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")
        if not isinstance(angle, (int, float)):
            raise TypeError("angle должен быть числом")

        return manipulator.mgbot_conveyer.set_servo_angle(float(angle))

    except Exception as e:
        print(f"[medu_conveyor_set_servo_angle] Ошибка: {e}")
        return None


def medu_conveyor_set_led_color(manipulator, r: int, g: int, b: int):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")

        for name, value in [("r", r), ("g", g), ("b", b)]:
            if not isinstance(value, int):
                raise TypeError(f"{name} должен быть int")
            if not 0 <= value <= 255:
                raise ValueError(f"{name} должен быть в диапазоне [0, 255]")

        return manipulator.mgbot_conveyer.set_led_color(r, g, b)

    except Exception as e:
        print(f"[medu_conveyor_set_led_color] Ошибка: {e}")
        return None


def medu_conveyor_display_text(manipulator, text: str):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text должен быть непустой строкой")

        return manipulator.mgbot_conveyer.display_text(text)

    except Exception as e:
        print(f"[medu_conveyor_display_text] Ошибка: {e}")
        return None


def medu_conveyor_set_buzz_tone(manipulator, level: int):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")
        if not isinstance(level, int):
            raise TypeError("level должен быть int")

        # Пример диапазона 1..15
        if not 1 <= level <= 15:
            raise ValueError("level должен быть в диапазоне [1, 15]")

        return manipulator.mgbot_conveyer.set_buzz_tone(level)

    except Exception as e:
        print(f"[medu_conveyor_set_buzz_tone] Ошибка: {e}")
        return None


def medu_conveyor_get_sensors_data(manipulator, as_json=True):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")
        if not isinstance(as_json, bool):
            raise TypeError("as_json должен быть bool")

        return manipulator.mgbot_conveyer.get_sensors_data(as_json)

    except Exception as e:
        print(f"[medu_conveyor_get_sensors_data] Ошибка: {e}")
        return None


# ---------------------------------------------------------------------------
# 11. Аудио
# ---------------------------------------------------------------------------

def medu_play_audio(
    manipulator,
    file_name: str,
    timeout_seconds=60.0,
    throw_error=True,
):
    try:
        if manipulator is None:
            raise ValueError("manipulator == None")

        if not isinstance(file_name, str) or not file_name.strip():
            raise ValueError("file_name должен быть непустой строкой")

        if not isinstance(timeout_seconds, (int, float)):
            raise TypeError("timeout_seconds должен быть числом")
        if float(timeout_seconds) < 0.0:
            raise ValueError("timeout_seconds не может быть отрицательным")

        if not isinstance(throw_error, bool):
            raise TypeError("throw_error должен быть bool")

        return manipulator.play_audio(
            file_name,
            timeout_seconds=float(timeout_seconds),
            throw_error=throw_error,
        )

    except Exception as e:
        print(f"[medu_play_audio] Ошибка: {e}")
        return None
