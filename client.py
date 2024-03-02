import threading
import time
import websocket
import json
import curses

# Initialize new variables
integers = [0]  # List of integers, the length can vary
int_tuples = (0, 0)  # Tuple of integers
float_tuples = (0.0, 0.0)  # Tuple of decimal floats
lock = threading.Lock()
is_running = True

def display_values(stdscr):
    stdscr.clear()
    stdscr.addstr("Control the values using keyboard keys. Press 'ESC' to exit.\n")
    stdscr.addstr(f'Integers: {integers}\n')
    stdscr.addstr(f'Int Tuples: {int_tuples}\n')
    stdscr.addstr(f'Float Tuples: {float_tuples}\n')
    stdscr.refresh()

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def update_values(stdscr):
    global integers, int_tuples, float_tuples, is_running
    stdscr.nodelay(True)

    key_actions = {
        '1': lambda: update_integers(1),
        '2': lambda: update_integers(-1),
        't': lambda: update_int_tuples(),
        'f': lambda: update_float_tuples(),
    }

    while is_running:
        try:
            key = stdscr.getkey()
            if key == '\x1b':  # ESC key for exit
                is_running = False
            elif key in key_actions:
                key_actions[key]()
                display_values(stdscr)
        except Exception as e:
            pass

def update_integers(delta):
    # Example action for modifying the integer list
    if len(integers) < 5:  # Example condition, modify as needed
        integers.append(integers[-1] + delta)
    else:
        integers.clear()  # Reset when reaching a certain condition

def update_int_tuples():
    global int_tuples
    # Example action for modifying the integer tuple
    int_tuples = (int_tuples[0] + 1, int_tuples[1] - 1)

def update_float_tuples():
    global float_tuples
    # Example action for modifying the float tuple
    float_tuples = (float_tuples[0] + 0.1, float_tuples[1] - 0.1)

def send_data(ws):
    while is_running:
        try:
            with lock:
                data = {
                    "integers": integers,
                    "int_tuples": int_tuples,
                    "float_tuples": float_tuples,
                }
            ws.send(json.dumps(data))
        except websocket.WebSocketConnectionClosedException:
            print("WebSocket connection closed. Attempting to reconnect...")
            time.sleep(5)
            start_websocket()  # Attempt to reconnect
            break
        except Exception as e:
            print(f"Error in sending data: {e}")
            break
        time.sleep(0.1)  # Sending data at 10 Hz

def start_websocket():
    uri = "ws://192.168.1.22:6969"
    ws = websocket.WebSocketApp(uri, on_open=lambda ws: threading.Thread(target=send_data, args=(ws,)).start())
    ws.run_forever()

threading.Thread(target=start_websocket, daemon=True).start()

curses.wrapper(update_values)
is_running = False
print("Exiting application...")
