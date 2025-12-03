# main_medu_example.py

from medu_wrappers import (
    medu_connect,
    medu_move_to_angles,
)

HOST = "192.168.0.183"
CLIENT_ID ="test-client"   # можешь поменять
LOGIN = "user"                    # твои логин/пароль из M Control
PASSWORD = "pass"

def main() -> None:
    # 1. Подключаемся к манипулятору через обёртку
    manipulator = medu_connect(
        host=HOST,
        client_id=CLIENT_ID,
        login=LOGIN,
        password=PASSWORD,
    )

    if manipulator is None:
        print("❌ Не удалось подключиться к MEdu (medu_connect вернул None)")
        return

    # 2. Простой move_to_angles через твою обёртку
    result = medu_move_to_angles(
        manipulator=manipulator,
        povorot_osnovaniya=0.0,
        privod_plecha=-0.35,
        privod_strely=-0.75,
        v_osnovaniya=0.0,
        v_plecha=0.0,
        v_strely=0.0,
        velocity_factor=0.2,
        acceleration_factor=0.2,
        timeout_seconds=60.0,
        throw_error=True,
    )

    if result is None:
        print("⚠️ medu_move_to_angles вернул None (ошибка в обёртке или SDK)")
    else:
        print("✅ Движение по углам выполнено")
        
    manipulator.disconnect()


if __name__ == "__main__":
    main()
