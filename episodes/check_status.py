
import controller
import time


if __name__ == "__main__":
    while True:
        # Run Every 15 minutes
        time.sleep(15*60)
        try:

            controller.sendMsg(["status",None])

        except EOFError:

            print("Socket Closed.  Trying later")


