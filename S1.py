import socket
import threading
import json
import time
import logging
import sqlite3
from quiz_db import initialize_db, insert_statistics, fetch_statistics

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

quiz = [
    {"question": "What does 'IP' stand for in networking?", 
     "options": ["A) Internet Protocol", "B) Internal Processing", "C) Information Provider", "D) Integrated Process"], 
     "answer": "A"},
     
    {"question": "Which device is used to connect multiple networks together?", 
     "options": ["A) Switch", "B) Router", "C) Hub", "D) Bridge"], 
     "answer": "B"},
     
    {"question": "Which layer of the OSI model is responsible for data encryption and compression?", 
     "options": ["A) Transport", "B) Session", "C) Presentation", "D) Network"], 
     "answer": "C"},
     
    {"question": "What is the maximum number of devices that can connect to a Class C IP address range?", 
     "options": ["A) 128", "B) 254", "C) 512", "D) 1024"], 
     "answer": "B"},
     
    {"question": "Which protocol is used for sending emails?", 
     "options": ["A) FTP", "B) SMTP", "C) HTTP", "D) POP3"], 
     "answer": "B"},
     
    {"question": "What is the main purpose of a firewall in networking?", 
     "options": ["A) Boosting internet speed", "B) Filtering and securing network traffic", "C) Connecting networks", "D) Managing IP addresses"], 
     "answer": "B"},
     
    {"question": "What is the default port for HTTP?", 
     "options": ["A) 80", "B) 443", "C) 21", "D) 25"], 
     "answer": "A"},
     
    {"question": "What does DNS stand for in networking?", 
     "options": ["A) Domain Network Server", "B) Data Name System", "C) Domain Name System", "D) Directory Name Server"], 
     "answer": "C"},
     
    {"question": "Which topology connects all devices to a central hub?", 
     "options": ["A) Ring", "B) Star", "C) Mesh", "D) Bus"], 
     "answer": "B"},
     
    {"question": "Which of the following is a private IP address?", 
     "options": ["A) 192.168.0.1", "B) 8.8.8.8", "C) 172.217.16.14", "D) 203.0.113.0"], 
     "answer": "A"}
]


clients = []

# Function to handle a single client
def handle_client(conn, addr):
    try:
        logging.info(f"New connection from {addr}")
        conn.send("Enter your name:".encode())
        name = conn.recv(1024).decode().strip()

        conn.send(f"Welcome to the quiz game, {name}!".encode())

        score = 0
        start_time = time.time()  # Record start time

        for idx, q in enumerate(quiz):
            conn.send(json.dumps(q).encode())
            answer = conn.recv(1024).decode().strip()
            if answer.upper() == q["answer"]:
                score += 1

        end_time = time.time()  # Record end time
        duration = round(end_time - start_time, 2)  # Calculate total time taken

        # Store statistics in the database
        insert_statistics(name, str(addr), score, duration)

        # Send individual results to the client
        conn.send(f"{name}, your final score is {score}/{len(quiz)}. You completed the quiz in {duration} seconds. Thank you for playing!".encode())
        logging.info(f"Client {addr} ({name}) finished the quiz with score {score} in {duration} seconds")

    except Exception as e:
        logging.error(f"Error handling client {addr}: {e}")
    finally:
        if conn in clients:
            clients.remove(conn)
        conn.close()

# Function to fetch and display quiz statistics
def send_statistics_to_all():
    stats = fetch_statistics()
    summary = "\n".join([f"Name: {name}, Score: {score}, Time: {duration}s" for name, score, duration in stats])
    logging.info("\nQuiz Statistics:\n" + summary)

    for client in clients:
        try:
            client.send(f"Quiz Summary:\n{summary}".encode())
        except:
            pass  # Handle disconnected clients

# Function to fetch and display leaderboard
def fetch_leaderboard():
    conn = sqlite3.connect('quiz_stats.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name, score, duration
        FROM quiz_statistics
        ORDER BY score DESC, duration ASC
        LIMIT 5
    ''')
    leaderboard = cursor.fetchall()
    conn.close()
    return leaderboard

def display_leaderboard():
    leaderboard = fetch_leaderboard()
    summary = "\n".join([f"{idx+1}. {name} - Score: {score}, Time: {duration}s" 
                         for idx, (name, score, duration) in enumerate(leaderboard)])
    logging.info("\nLeaderboard:\n" + summary)

# Server setup and management
def start_server():
    initialize_db()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5555))
    server.listen(5)
    logging.info("Server started on port 5555")

    try:
        while True:
            conn, addr = server.accept()
            clients.append(conn)
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
    except KeyboardInterrupt:
        logging.info("Server shutting down...")
        send_statistics_to_all()
        for conn in clients:
            conn.close()
        server.close()
    finally:
        logging.info("Server closed.")

# Command monitoring for statistics and leaderboard
def monitor_commands():
    while True:
        command = input("Enter a command ('stats', 'leaderboard', 'exit'): ").strip().lower()
        if command == 'stats':
            stats = fetch_statistics()
            logging.info("\nCurrent Statistics:\n" + "\n".join(
                [f"{name} - Score: {score}, Time: {duration}s" for name, score, duration in stats]))
        elif command == 'leaderboard':
            display_leaderboard()
        elif command == 'exit':
            logging.info("Shutting down server...")
            send_statistics_to_all()
            for conn in clients:
                conn.close()
            break

if __name__ == "__main__":
    threading.Thread(target=monitor_commands, daemon=True).start()
    start_server()
