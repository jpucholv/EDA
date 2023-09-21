import MetaTrader5 as mt5
import pandas as pd
import time
import os

# Establecer conexión con MetaTrader 5
mt5.initialize(login=4000013671, server="Darwinex-Live", password="K6Kpnug0RE6U")

# Crear DataFrame
media_movil_periodos = 8
data = pd.DataFrame(index=['date'], columns=['bid', 'ask', f'MA_{media_movil_periodos}', f'Derivada_{media_movil_periodos}'])
data[f'MA_{media_movil_periodos}'] = data['bid'].rolling(window=media_movil_periodos).mean().iloc[-1] if len(data) > 0 else None
data[f'Derivada_{media_movil_periodos}'] = data['bid'].diff().rolling(window=media_movil_periodos).mean().iloc[-1] if len(data) > 0 else None

ric = 'GDAXI'  # NDX, GDAXI
position = None
last_order = None

# Establecer el límite máximo de registros en el DataFrame
max_records = 120

while True:
    os.system('cls')

    # Intentar habilitar la visualización de {ric} en MarketWatch
    selected = mt5.symbol_select(ric, True)
    if not selected:
        print(f"Failed to select {ric}")
        mt5.shutdown()
        quit()

    # Obtener el último tick de {ric}
    lasttick = mt5.symbol_info_tick(ric)

    # Verificar si el mercado está cerrado
    if lasttick.time_msc == 0:
        print("Mercado cerrado")
        time.sleep(60)
        continue

    # Crear un nuevo DataFrame con el registro actual
    nuevo_registro = pd.DataFrame({'date': [lasttick.time_msc],
                                   'bid': [lasttick.bid],
                                   'ask': [lasttick.ask],
                                   f'MA_{media_movil_periodos}': data['bid'].rolling(window=media_movil_periodos).mean().iloc[-1] if len(data) > 0 else None,
                                   f'Derivada_{media_movil_periodos}': data['bid'].diff().rolling(window=media_movil_periodos).mean().iloc[-1] if len(data) > 0 else None})
    # Establecer la columna 'date' como el índice
    nuevo_registro = nuevo_registro.set_index('date')

    # Concatenar el nuevo registro al DataFrame existente
    data = pd.concat([data, nuevo_registro])

    # Verificar si se alcanzó el límite máximo de registros
    if len(data) > max_records:
        # Eliminar los registros más antiguos
        data = data.iloc[-max_records:]

    # Obtener el saldo disponible en la cuenta
    account_info = mt5.account_info()
    balance = account_info.balance
    equity = account_info.equity
    margin = account_info.margin

    # Calcular el tamaño de posición como el balance de la cuenta
    max_position_size = 1.0

    # Imprimir resultados
    print("Saldo disponible:", balance)
    print("Equidad:", equity)
    print("Margen utilizado:", margin)
    print("Tamaño máximo de posición:", max_position_size)

    # Cerrar posición si existe una abierta
    if position:
        positions = mt5.positions_get(symbol=ric)
        if positions:
            for position in positions:
                if position.type == mt5.ORDER_TYPE_BUY:
                    close_request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": ric,
                        "volume": position.volume,
                        "type": mt5.ORDER_TYPE_SELL,
                        "position": position.ticket,
                        "deviation": 20,
                        "comment": "python script close",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_FOK
                    }
                    close_result = mt5.order_send(close_request)
                    if close_result.retcode != mt5.TRADE_RETCODE_DONE:
                        print("Error al cerrar la posición")
                        mt5.shutdown()
                        quit()
                    else:
                        print("Posición cerrada")
                        position = None
                        break  # Salir del bucle después de cerrar la posición

    # Abrir posición si se cumplen las condiciones de entrada
    if data[f'Derivada_{media_movil_periodos}'].iloc[-1] >= 0 and not position:
        open_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": ric,
            "volume": max_position_size,
            "type": mt5.ORDER_TYPE_BUY,
            "price": lasttick.ask,
            "magic": 234000,
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK
        }

        open_result = mt5.order_send(open_request)
        if open_result.retcode != mt5.TRADE_RETCODE_DONE:
            print("Error al abrir la posición")
        else:
            print("Posición abierta")
            last_order = open_result.order
            position = True

    # Esperar 1 segundo antes de la siguiente iteración
    time.sleep(1)
