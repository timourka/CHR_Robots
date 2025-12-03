# main_medu_conveyor_tests.py

import time

from medu_wrappers import (
    medu_connect,
    medu_conveyor_set_speed_motors,
    medu_conveyor_set_servo_angle,
    medu_conveyor_set_led_color,
    medu_conveyor_display_text,
    medu_conveyor_set_buzz_tone,
    medu_conveyor_get_sensors_data,
)

HOST = "192.168.0.183"
CLIENT_ID = "python_full_test"
LOGIN = "13"
PASSWORD = "14"

def testText(manipulator) -> None:
    """Тест: вывести текст на дисплей ленты."""
    print("→ testText: display_text('TEST LENTA')")
    res = medu_conveyor_display_text(manipulator, "TEST LENTA")
    print("  display_text ->", res)


def testLed(manipulator) -> None:
    """Тест: включить зелёный светодиод на ленте."""
    print("→ testLed: set_led_color(0, 255, 0)")
    res = medu_conveyor_set_led_color(manipulator, r=0, g=255, b=0)
    print("  set_led_color ->", res)


def testSpeed(manipulator) -> None:
    """Тест: погонять ленту по скоростям 30 → 60 → 0."""
    print("→ testSpeed: speed = 30")
    res1 = medu_conveyor_set_speed_motors(manipulator, 30)
    print("  set_speed_motors(30) ->", res1)
    time.sleep(3)

    print("→ testSpeed: speed = 60")
    res2 = medu_conveyor_set_speed_motors(manipulator, 60)
    print("  set_speed_motors(60) ->", res2)
    time.sleep(3)

    print("→ testSpeed: speed = 0 (stop)")
    res3 = medu_conveyor_set_speed_motors(manipulator, 0)
    print("  set_speed_motors(0) ->", res3)


def testServo(manipulator) -> None:
    """Тест: повернуть сервопривод ленты на 45°."""
    print("→ testServo: servo_angle = 45°")
    res = medu_conveyor_set_servo_angle(manipulator, 45.0)
    print("  set_servo_angle(45.0) ->", res)


def testBuzz(manipulator) -> None:
    """Тест: включить буззер ленты на уровне 5."""
    print("→ testBuzz: buzz level = 5")
    res = medu_conveyor_set_buzz_tone(manipulator, 5)
    print("  set_buzz_tone(5) ->", res)


def testSensors(manipulator) -> None:
    """Тест: прочитать данные с датчиков ленты."""
    print("→ testSensors: get_sensors_data(as_json=True)")
    res = medu_conveyor_get_sensors_data(manipulator, as_json=True)
    print("  get_sensors_data ->", res)


# ------------ пример общего запуска ------------

def main() -> None:
    manipulator = medu_connect(
        host=HOST,
        client_id=CLIENT_ID,
        login=LOGIN,
        password=PASSWORD,
    )

    if manipulator is None:
        print("❌ Не удалось подключиться к MEdu")
        return

    print("✅ Подключение к MEdu установлено")

    # тут можно вызывать любые тесты по очереди
    testText(manipulator)
    #testLed(manipulator)
    #testSpeed(manipulator)
    #testServo(manipulator)
    #testBuzz(manipulator)
    #testSensors(manipulator)

    print("✅ Все тесты выполнены")
    
    manipulator.disconnect()


if __name__ == "__main__":
    main()
