"""
main_medu_manipulator_tests.py

Минимальные тесты функций работы с манипулятором MEdu (НЕ конвейер).
Использует обёртки из medu_wrappers.py.

Каждый тест — отдельная функция вида test_*** (manipulator),
чтобы можно было сделать так:

>>> from main_medu_manipulator_tests import get_manipulator, test_move_to_angles
>>> m = get_manipulator()
>>> test_move_to_angles(m)

Перед использованием ЗАМЕНИ значения HOST / CLIENT_ID / LOGIN / PASSWORD
на свои реальные.
"""

import time

from sdk.utils.enums import ServoControlType  # если PlannerType нет в SDK — убери его импорт
from medu_wrappers import (
    medu_connect,
    medu_move_to_angles,
    medu_move_to_coordinates,
    medu_arc_motion,
    medu_nozzle_power,
    medu_manage_gripper,
    medu_set_servo_control_type,
    medu_set_servo_twist_mode,
    medu_set_servo_pose_mode,
    medu_set_servo_joint_jog_mode,
    medu_stream_cartesian_velocities,
    medu_stream_coordinates,
    medu_stream_joint_angles,
    medu_run_program,
    medu_run_program_json,
    medu_run_python_program,
    medu_stop_movement,
    medu_get_joint_state,
    medu_get_home_position,
    medu_get_cartesian_coordinates,
    medu_write_gpio,
    medu_get_gpio_value,
    medu_play_audio,
)


# ---------------------------------------------------------------------------
# Конфиг подключения — ЗАМЕНИ НА СВОИ
# ---------------------------------------------------------------------------

HOST = "192.168.88.182"   # IP манипулятора / брокера MQTT
CLIENT_ID = "my_client"   # любой уникальный ID
LOGIN = "13"              # логин пользователя
PASSWORD = "14"           # пароль пользователя


# ---------------------------------------------------------------------------
# Глобальный объект манипулятора, создаётся лениво через medu_connect
# ---------------------------------------------------------------------------

_MANIPULATOR = None


def get_manipulator():
    """Ленивое подключение к манипулятору через medu_connect."""
    global _MANIPULATOR
    if _MANIPULATOR is None:
        print("[SETUP] Подключение к манипулятору...")
        _MANIPULATOR = medu_connect(HOST, CLIENT_ID, LOGIN, PASSWORD)
        if _MANIPULATOR is None:
            print("[SETUP] Не удалось подключиться к манипулятору")
        else:
            print("[SETUP] Подключение успешно")
    return _MANIPULATOR


# ---------------------------------------------------------------------------
# Тесты подключения и базового движения
# ---------------------------------------------------------------------------

def test_connect(manipulator):
    """Проверка подключения (manipulator уже создан снаружи)."""
    print("\n=== test_connect ===")
    print("manipulator =", manipulator)
    return manipulator


def test_move_to_angles(manipulator):
    """
    Минимальный тест medu_move_to_angles.
    Значения углов взяты из примера в документации SDK.
    """
    print("\n=== test_move_to_angles ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    result = medu_move_to_angles(
        manipulator,
        povorot_osnovaniya=0.05,
        privod_plecha=-0.35,
        privod_strely=-0.75,
        v_osnovaniya=0.0,
        v_plecha=0.0,
        v_strely=0.0,
        velocity_factor=0.1,
        acceleration_factor=0.1,
        timeout_seconds=60.0,
        throw_error=True,
    )
    print("move_to_angles result:", result)
    return result


def test_move_to_coordinates(manipulator):
    """
    Минимальный тест medu_move_to_coordinates.
    Координаты и ориентация — как в примере из документации.
    """
    print("\n=== test_move_to_coordinates ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    # позиция и ориентация из официального примера
    x, y, z = 0.32, -0.004, 0.25
    ox, oy, oz, ow = 0.0, 0.0, 0.0, 1.0

    try:
        planner = PlannerType.LIN
    except Exception:
        # если в новой версии SDK PlannerType отсутствует,
        # а твоя обёртка не требует его — можно передать None
        planner = None

    result = medu_move_to_coordinates(
        manipulator,
        x, y, z,
        ox, oy, oz, ow,
        velocity_scaling_factor=0.1,
        acceleration_scaling_factor=0.1,
        planner_type=planner,
        timeout_seconds=30.0,
        throw_error=True,
    )
    print("move_to_coordinates result:", result)
    return result


def test_arc_motion(manipulator):
    """
    Минимальный тест medu_arc_motion.
    Координаты взяты в разумном диапазоне для небольшого манипулятора.
    """
    print("\n=== test_arc_motion ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    result = medu_arc_motion(
        manipulator,
        target_x=0.25,
        target_y=-0.05,
        target_z=0.20,
        center_x=0.25,
        center_y=0.0,
        center_z=0.20,
        step=0.02,
        count_point_arc=30,
        max_velocity_scaling_factor=0.3,
        max_acceleration_scaling_factor=0.3,
        timeout_seconds=60.0,
        throw_error=True,
    )
    print("arc_motion result:", result)
    return result


# ---------------------------------------------------------------------------
# Тесты насадки и гриппера
# ---------------------------------------------------------------------------

def test_nozzle_power_on_off(manipulator):
    """Тест включения/выключения питания насадки."""
    print("\n=== test_nozzle_power_on_off ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    print("nozzle_power(True)")
    r1 = medu_nozzle_power(manipulator, True)
    time.sleep(1.0)

    print("nozzle_power(False)")
    r2 = medu_nozzle_power(manipulator, False)

    print("results:", r1, r2)
    return r1, r2


def test_manage_gripper(manipulator):
    """
    Тест medu_manage_gripper.
    Параметры rotation / gripper как в примерах документации.
    """
    print("\n=== test_manage_gripper ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    # включаем питание насадки
    medu_nozzle_power(manipulator, True)
    time.sleep(0.5)

    print("manage_gripper(rotation=20, gripper=10)")
    r1 = medu_manage_gripper(manipulator, rotation=20, gripper=10)
    time.sleep(1.0)

    print("manage_gripper(rotation=None, gripper=0)  # открыть")
    r2 = medu_manage_gripper(manipulator, rotation=None, gripper=0)

    print("results:", r1, r2)
    return r1, r2


# ---------------------------------------------------------------------------
# Тесты серво-режимов и стриминга
# ---------------------------------------------------------------------------

def test_set_servo_control_type(manipulator):
    """Тест установки режима через общий medu_set_servo_control_type."""
    print("\n=== test_set_servo_control_type ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    print("set_servo_control_type(TWIST)")
    r = medu_set_servo_control_type(manipulator, ServoControlType.TWIST)
    print("result:", r)
    return r


def test_set_servo_modes_shortcuts(manipulator):
    """Тест коротких функций: TWIST / POSE / JOINT_JOG."""
    print("\n=== test_set_servo_modes_shortcuts ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    print("set_servo_twist_mode()")
    r1 = medu_set_servo_twist_mode(manipulator)
    time.sleep(0.2)

    print("set_servo_pose_mode()")
    r2 = medu_set_servo_pose_mode(manipulator)
    time.sleep(0.2)

    print("set_servo_joint_jog_mode()")
    r3 = medu_set_servo_joint_jog_mode(manipulator)

    print("results:", r1, r2, r3)
    return r1, r2, r3


def test_stream_cartesian_velocities_once(manipulator):
    """
    Один шаг стриминга скоростей.
    В реальной задаче обычно вызывается в цикле.
    """
    print("\n=== test_stream_cartesian_velocities_once ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    medu_set_servo_twist_mode(manipulator)

    linear_vel = {"x": 0.02, "y": 0.0, "z": 0.0}
    angular_vel = {"rx": 0.0, "ry": 0.0, "rz": 0.01}

    r = medu_stream_cartesian_velocities(manipulator, linear_vel, angular_vel)
    print("stream_cartesian_velocities result:", r)
    return r


def test_stream_coordinates_once(manipulator):
    """Один шаг стриминга позы (stream_coordinates)."""
    print("\n=== test_stream_coordinates_once ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    medu_set_servo_pose_mode(manipulator)

    # возьмём аккуратную точку в рабочей зоне
    r = medu_stream_coordinates(
        manipulator,
        x=0.27,
        y=0.0,
        z=0.15,
        ox=0.0,
        oy=0.0,
        oz=0.0,
        ow=1.0,
    )
    print("stream_coordinates result:", r)
    return r


def test_stream_joint_angles_once(manipulator):
    """Один шаг стриминга суставов (stream_joint_angles)."""
    print("\n=== test_stream_joint_angles_once ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    medu_set_servo_joint_jog_mode(manipulator)

    r = medu_stream_joint_angles(
        manipulator,
        povorot_osnovaniya=0.5,
        privod_plecha=1.0,
        privod_strely=0.8,
        v_osnovaniya=0.2,
        v_plecha=0.1,
        v_strely=0.15,
    )
    print("stream_joint_angles result:", r)
    return r


# ---------------------------------------------------------------------------
# Тесты программ на роботе
# ---------------------------------------------------------------------------

def test_run_program(manipulator):
    """Запуск готовой программы (по имени)."""
    print("\n=== test_run_program ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    # имя программы из документации
    r = medu_run_program(manipulator, "edum/default")
    print("run_program result:", r)
    return r


def test_run_program_json(manipulator):
    """Запуск JSON-программы (пример из документации)."""
    print("\n=== test_run_program_json ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

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

    r = medu_run_program_json(manipulator, "program_1", program_json)
    print("run_program_json result:", r)
    return r


def test_run_python_program(manipulator):
    """Запуск простого Python-кода на роботе."""
    print("\n=== test_run_python_program ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    r = medu_run_python_program(manipulator, "print('Hello from MEdu!')")
    print("run_python_program result:", r)
    return r


# ---------------------------------------------------------------------------
# Тесты остановки и чтения состояния
# ---------------------------------------------------------------------------

def test_stop_movement(manipulator):
    """Тест остановки движения."""
    print("\n=== test_stop_movement ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    r = medu_stop_movement(manipulator, timeout_seconds=5.0)
    print("stop_movement result:", r)
    return r


def test_get_joint_state(manipulator):
    """Тест получения углов суставов."""
    print("\n=== test_get_joint_state ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    state = medu_get_joint_state(manipulator)
    print("joint_state:", state)
    return state


def test_get_home_position(manipulator):
    """Тест получения home-позиции."""
    print("\n=== test_get_home_position ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    home = medu_get_home_position(manipulator)
    print("home_position:", home)
    return home


def test_get_cartesian_coordinates(manipulator):
    """Тест получения текущих декартовых координат."""
    print("\n=== test_get_cartesian_coordinates ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    pose = medu_get_cartesian_coordinates(manipulator)
    print("cartesian_coordinates:", pose)
    return pose


# ---------------------------------------------------------------------------
# Тесты GPIO
# ---------------------------------------------------------------------------

def test_write_gpio(manipulator):
    """Минимальный тест записи в GPIO (пример имени пина из документации)."""
    print("\n=== test_write_gpio ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    gpio_name = "/dev/gpiochip4/e1_pin"  # пример из документации
    r = medu_write_gpio(manipulator, gpio_name, value=1, timeout_seconds=0.5, throw_error=False)
    print("write_gpio result:", r)

    # вернём в 0
    r2 = medu_write_gpio(manipulator, gpio_name, value=0, timeout_seconds=0.5, throw_error=False)
    print("write_gpio (back to 0) result:", r2)
    return r, r2


def test_get_gpio_value(manipulator):
    """Минимальный тест чтения GPIO."""
    print("\n=== test_get_gpio_value ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    gpio_name = "/dev/gpiochip4/e1_pin"
    value = medu_get_gpio_value(manipulator, gpio_name, timeout_seconds=0.5, throw_error=False)
    print("gpio value:", value)
    return value


# ---------------------------------------------------------------------------
# Тест аудио
# ---------------------------------------------------------------------------

def test_play_audio(manipulator):
    """Тест воспроизведения аудио-файла."""
    print("\n=== test_play_audio ===")
    if manipulator is None:
        print("Нет манипулятора")
        return

    # файл должен существовать на стороне робота
    r = medu_play_audio(manipulator, "start.wav", timeout_seconds=10.0, throw_error=False)
    print("play_audio result:", r)
    return r


# ---------------------------------------------------------------------------
# Запуск набора тестов
# ---------------------------------------------------------------------------

def run_smoke_suite():
    """
    Небольшой набор тестов, которые можно прогнать одним вызовом.
    Сейчас ВЫЗЫВАЕТСЯ только test_connect(), все остальные тесты
    закомментированы — раскомментируй нужные.
    """
    manipulator = get_manipulator()
    if manipulator is None:
        return

    # БАЗОВОЕ ПОДКЛЮЧЕНИЕ
    test_connect(manipulator)

    # БАЗОВОЕ ДВИЖЕНИЕ
    test_move_to_angles(manipulator)
    # test_move_to_coordinates(manipulator)
    # test_arc_motion(manipulator)

    # НАСАДКА И ГРИППЕР
    # test_nozzle_power_on_off(manipulator)
    # test_manage_gripper(manipulator)

    # СЕРВО-РЕЖИМЫ И СТРИМИНГ
    # test_set_servo_control_type(manipulator)
    # test_set_servo_modes_shortcuts(manipulator)
    # test_stream_cartesian_velocities_once(manipulator)
    # test_stream_coordinates_once(manipulator)
    # test_stream_joint_angles_once(manipulator)

    # ПРОГРАММЫ НА РОБОТЕ
    # test_run_program(manipulator)
    # test_run_program_json(manipulator)
    # test_run_python_program(manipulator)

    # ОСТАНОВКА И СОСТОЯНИЕ
    # test_stop_movement(manipulator)
    # test_get_joint_state(manipulator)
    # test_get_home_position(manipulator)
    # test_get_cartesian_coordinates(manipulator)

    # GPIO
    test_write_gpio(manipulator)
    # test_get_gpio_value(manipulator)

    # АУДИО
    test_play_audio(manipulator)


if __name__ == "__main__":
    run_smoke_suite()
