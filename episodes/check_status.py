
import controller
import time


if __name__ == "__main__":
    while True:
        # Run Every 15 minutes
        try:

            controller.sendMsg(["status",None])

        except EOFError:

            print("Socket Closed.  Trying later")
        time.sleep(10*60)


