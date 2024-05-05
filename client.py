import socket
import select
import sys

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
PURPLE = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"

class ChatClient():
    def __init__(self, host="localhost", port=5000):
        self.HOST = host
        self.PORT = port
        self.RECV_BUFFER = 4096
        self.username = ""
        self.group = "GreatHall"
        self.separator = "&&&"  # same as the server
        self.helpMsg = f"""\
            {PURPLE}LIST  => to get a list of people online
            @name => to send a message to a specific person
            CLEAR => clear the screen
            HELP  => display this help message
            EXIT  => exit.{RESET}
            """
        
    def prompt(self):
        # prompt for the current active user to type a message
        sys.stdout.flush()
        sys.stdout.write("\r\033[K")
        sys.stdout.write(BOLD + GREEN + self.username + "> " + RESET)
        sys.stdout.flush()

    def init(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)

        try:
            s.connect((self.HOST, self.PORT))
        except:
            print('Unable to connect')
            sys.exit()

        # set the chat room
        self.printList("CHAT ROOMS", s.recv(self.RECV_BUFFER).decode("utf-8"))
        groupName = input(f"{PURPLE}Join a Chat Room or Create New: {YELLOW}").replace(" ", "")
        if groupName != "":
            self.group = groupName
        s.send(self.group.encode("utf-8"))

        # get the user's name and send it to the server
        while self.username == "":
            self.username = input(f"{PURPLE}Enter your Name: {YELLOW}").replace(" ", "")
        print(RESET)
        s.send(self.username.encode("utf-8"))

        firstConnResponse = s.recv(self.RECV_BUFFER).decode("utf-8")
        if "SERVER_FAIL" + self.separator in firstConnResponse:
            print(f"{BOLD}{RED}ERROR>{RESET} Cannot have the same names")
            sys.exit()
        else:
            print(f"{BOLD}{YELLOW}INFO>{RESET} Connected to host. Start sending messages.")
            print(self.helpMsg)
            print(f"{PURPLE}Joined {YELLOW}{self.group}{PURPLE} group as {YELLOW}{self.username}{RESET}")

        while True:
            self.prompt()
            socket_list = [sys.stdin, s]

            # get the list of sockets which are readable
            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

            for sock in read_sockets:
                # handle incoming messages from the remote server
                if sock == s:
                    data = sock.recv(self.RECV_BUFFER).decode("utf-8")
                    if not data:
                        sys.stdout.write(f"{BOLD}{RED}")
                        sys.stdout.write('Disconnected from the chat server')
                        sys.stdout.write(RESET)
                        sys.exit()
                    else:
                        # receive user messages
                        # clears self stdin (bug-like thingy)
                        try:
                            dt = data.split(self.separator, 1)
                            name = dt[0]
                            msg = dt[1]
                            sys.stdout.write("\r\033[K")
                            sys.stdout.flush()
                            if name == "SERVER_INFO":
                                # information
                                sys.stdout.write(f"{BOLD}{YELLOW}")
                                sys.stdout.write("INFO" + "> ")
                            else:
                                # normal message
                                sys.stdout.write(f"{BOLD}{CYAN}")
                                sys.stdout.write(name + "> ")

                            sys.stdout.write(RESET)
                            sys.stdout.write(msg + "\n")
                        except:
                            # otherwise show a list of users online
                            # not the best way to handle responses
                            self.printList("PEOPLE ONLINE", data)
                # send a message
                else:
                    msg = sys.stdin.readline().strip()
                    if msg == "EXIT":
                        print("Bye,", self.username)
                        sys.exit()
                    elif msg == "NAVID":
                        print('Navid con bolboli, Fuck you!  :)')
                    elif msg == "CLEAR":
                        print("\x1b[2J\x1b[H")
                    elif msg == "HELP":
                        print(self.helpMsg)
                    elif len(msg) > 0:
                        s.send((self.group + self.separator + msg).encode("utf-8"))
    

    def printList(self, msg, response):
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()
        print(YELLOW + "<---- " + msg + " ---->" + RESET)
        for p in response.split("::"):
            print(GREEN + "*" + RESET, p)
        print()

def main():
    try:
        host = sys.argv[1].split(":")[0]
    except:
        host = input("Host: ")
    try:
        port = int(sys.argv[1].split(":")[1])
    except:
        port = int(input("Port: "))

    client = ChatClient(host=host, port=port)
    client.init()

if __name__ == '__main__':
    main()
