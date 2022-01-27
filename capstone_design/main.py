import http.server
import time
import json
import serial
import psycopg2
import re
import time

"""
ser = serial.Serial(port='COM3', baudrate=9600)
while True:
    if ser.readable():
        input_str = input()  # 최대 32 문자
        size = len(input_str)
        if 0 <= size <= 32:
            # data 전송
            input_str = "gogogo".encode('utf-8')
            ser.write(input_str)
        else:
            print("32 글자 초과, 재입력 바랍니다.")
        time.sleep(5)
"""

class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    ser = serial.Serial(port='COM3', baudrate=9600)
    connect = psycopg2.connect("dbname=capstone user=postgres password=akqj1029")
    cur = connect.cursor()
    id = 0

    def __init__(self, request, client_address, server):
        self.DELAY = 1
        self.MAX = 175
        self.MIN = 5
        self.ANG = 90
        self.slang_words = ["fucking", "unfuckingbelievable", "no fucking way", "fuck", "motherfucker", "shit", "bullshit", "ass", "asshole", "nigga", "jungle fever", "yellow monkey", "dick", "cock", "pussy", "cunt", "tit", "boob", "damn", "bitch", "whore", "freak", "faggot", "bastart"]
        #self.ser = serial.Serial(port='COM3', baudrate=9600)
        #self.servo = self.board.get_pin('d:11:s')
        http.server.BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    # Post가 왔을 때
    def do_POST(self):
        # rfile에 post된 값을 'Content-Length'만큼 읽어옴
        content_len = int(self.headers['Content-Length'])
        post_body = self.rfile.read(content_len)

        print(post_body)
        print(type(post_body))

        # bytes -> str decode
        mm = post_body.decode('utf-8')

        # 받은 값에서 실제 value parsing
        temp = mm.split("%")
        print(temp)
        star = int(temp[2].split("=")[-1][0])
        review = temp[-1].split("=")[-1]
        review = re.sub(r"\+", " ", review)
        print(star)
        print(review)
        is_slang = False
        for words in self.slang_words:
            if words in review.lower():
                is_slang =True
                break
        if not is_slang:
            self.cur.execute("select max(id) from review;")
            result = self.cur.fetchall()
            self.id = int(result[0][0]) + 1
            statement = "insert into review values ('" + str(self.id) + "', " + str(star) + ", '" + review + "');"
            self.cur.execute(statement)
            self.connect.commit()
            size = len(review)
            self.cur.execute("select avg(star) from review;")
            result = self.cur.fetchall()
            avg = round(float(result[0][0]),1)

            if self.ser.readable():
                input_star = ("rate " + str(star)+ ", avg: " + str(avg))
                #self.ser.write(input_star)
                #time.sleep(1)
                if size <= 32:
                    input_str = (input_star+review).encode('utf-8')
                    self.ser.write(input_str)
            else:
                print("WTF")
            self.response(200, "Hello")
        else:
            input_str = ("slang filtered").encode('utf-8')
            self.ser.write(input_str)
            self.response(0, "Slang Not displayed")

        # http post에 대한 response 보냄
        #return http.server.BaseHTTPRequestHandler.do_POST(self)

    # Get을 할 때
    def do_GET(self):

        self.route()

    def route(self):

        if self.path == '/hello':
            self.hello()
        else:
            self.response_404_not_found()

    def hello(self):
        self.response(200, "Hello")

    def response_404_not_found(self):
        self.response(404, "Command not found")

    def response(self, status_code, body):
        self.send_response(status_code)

        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()

        self.wfile.write(body.encode('utf-8'))

class http_server:
    def __init__(self, t1):
        HTTPRequestHandler.t1 = t1
        server = http.server.HTTPServer(('192.168.1.184', 8886), HTTPRequestHandler)
        print(f'waiting')
        server.serve_forever()

ADDRESS = '192.168.1.184', 8886# (IP 주소, Port 번호)

#ser = serial.Serial(port='COM3', baudrate=9600)
#Go_serve = http_server(ser)
listener = http.server.HTTPServer(ADDRESS, HTTPRequestHandler)
print(f'waiting')
listener.serve_forever()