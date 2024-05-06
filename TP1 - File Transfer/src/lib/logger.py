class Logger:
    def __init__(self, show_msgs):
        self.show_msgs = show_msgs

    def print_msg(self, msg):
        if self.show_msgs:
            print(msg)

    def received_expecting_sr_msg(self, msg_seq_num, sr_seq_num):
        print(f"Received {msg_seq_num} while expecting {sr_seq_num}")

    def timeout_ack_msg(self):
        print("Timeout waiting for ACK package. Retrying...")

    def timeout_data_msg(self):
        print("Timeout waiting for data package. Retrying...")

    def resend_sr_msg(self, seq_num, base, timestamp):
        print(f"Resent {seq_num} with window {base} and timestamp {timestamp}")

    def send_with_sr_msg(self, seq_num, base):
        print(f"Sent {seq_num} with window {base}")

    def send_last_data_with_sr_msg(self, seq_num, base):
        print(f"Sent last data {seq_num} with window {base}")
