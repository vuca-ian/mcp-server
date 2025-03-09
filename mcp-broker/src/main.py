import hupper
import server

def start():
    print("gavc")
    server.main()

if __name__ == "__main__":
    hupper.start_reloader("main.start")
    start()