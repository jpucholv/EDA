import MetaTrader5 as mt5
import pandas as pd
import time
import os

# Establecer conexión con MetaTrader 5
mt5.initialize(login=4000013671, server="Darwinex-Live", password="K6Kpnug0RE6U")

# Crear DataFrame
media_movil_periodos = 8
data = pd.DataFrame(columns=['bid', 'ask', f'MA_{media_movil_periodos}'])

ric = 'NDX'  # NDX, GDAXI
position = None

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
    nuevo_registro = pd.DataFrame({'bid': [lasttick.bid],
                                   'ask': [lasttick.ask],
                                   f'MA_{media_movil_periodos}': data['bid'].rolling(window=media_movil_periodos).mean().iloc[-1] if len(data) > 0 else None})
    
    # Concatenar el nuevo registro al DataFrame existente
    data = pd.concat([data, nuevo_registro])

    # Comparar el valor de la media móvil con el valor anterior
    if len(data) > 1 and data[f'MA_{media_movil_periodos}'].iloc[-1] is not None and data[f'MA_{media_movil_periodos}'].iloc[-2] is not None:
        if data[f'MA_{media_movil_periodos}'].iloc[-1] > data[f'MA_{media_movil_periodos}'].iloc[-2]:
            print("La media móvil ha subido")
            if position != 'BUY':
                if position == 'SELL':
                    # Cerrar todas las posiciones cortas
                    positions = mt5.positions_get(symbol=ric)
                    if positions:
                        for position in positions:
                            if position.type == mt5.ORDER_TYPE_SELL:
                                close_request = {
                                    "action": mt5.TRADE_ACTION_DEAL,
                                    "symbol": ric,
                                    "volume": position.volume,
                                    "type": mt5.ORDER_TYPE_BUY,
                                    "position": position.ticket,
                                    "deviation": 20,
                                    "comment": "python script close",
                                    "type_time": mt5.ORDER_TIME_GTC,
                                    "type_filling": mt5.ORDER_FILLING_FOK
                                }
                                close_result = mt5.order_send(close_request)
                                if close_result.retcode != mt5.TRADE_RETCODE_DONE:
                                    print("Error al cerrar la posición corta")
                                else:
                                    print("Posición corta cerrada")
                                    position = None
                                    break  # Salir del bucle después de cerrar la posición corta

                # Abrir una nueva posición larga
                lot = 1.0
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": ric,
                    "volume": lot,
                    "type": mt5.ORDER_TYPE_BUY,
                    "price": mt5.symbol_info_tick(ric).ask,
                    "deviation": 20,
                    "comment": "python script open",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_FOK
                }
                result = mt5.order_send(request)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print("Error al abrir la posición larga")
                else:
                    print("Posición larga abierta")
                    position = 'BUY'
        
        elif data[f'MA_{media_movil_periodos}'].iloc[-1] < data[f'MA_{media_movil_periodos}'].iloc[-2]:
            print("La media móvil ha bajado")
            if position != 'SELL':
                if position == 'BUY':
                    # Cerrar todas las posiciones largas
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
                                    print("Error al cerrar la posición larga")
                                else:
                                    print("Posición larga cerrada")
                                    position = None
                                    break  # Salir del bucle después de cerrar la posición larga

                # Abrir una nueva posición corta
                lot = 1.0
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": ric,
                    "volume": lot,
                    "type": mt5.ORDER_TYPE_SELL,
                    "price": mt5.symbol_info_tick(ric).bid,
                    "deviation": 20,
                    "comment": "python script open",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_FOK
                }
                result = mt5.order_send(request)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print("Error al abrir la posición corta")
                else:
                    print("Posición corta abierta")
                    position = 'SELL'
        
        else:
            print("La media móvil se mantiene igual")

    # Obtener el saldo disponible en la cuenta
    account_info = mt5.account_info()
    balance = account_info.balance
    equity = account_info.equity
    margin = account_info.margin

    # Imprimir resultados
    print("Saldo disponible:", balance)
    print("Equidad:", equity)
    print("Margen utilizado:", margin)

    print(data.iloc[-1])
    print(position)

    # Esperar 1 minuto antes de tomar el siguiente registro
    time.sleep(3600)
