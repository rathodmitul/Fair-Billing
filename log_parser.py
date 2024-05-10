import sys
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Session:
    start_time: datetime
    end_time: datetime
    duration: int


@dataclass
class User:
    name: str
    sessions: list[Session]
    total_session_time: int = 0


class LogParser:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.users = {}
        self.earliest_time = None
        self.latest_time = None
        self.allowed_actions = {"Start", "End"}

    def is_valid_record(self, username: str, action: str) -> bool:
        if not username.isalnum() or action not in self.allowed_actions:
            return False
        return True

    def update_time_range(self, timestamp: datetime) -> None:
        if self.earliest_time is None:
            self.earliest_time = timestamp
        if self.latest_time is None or timestamp > self.latest_time:
            self.latest_time = timestamp

    def update_user_sessions(
        self, username: str, action: str, timestamp: datetime
    ) -> None:
        user = self.users[username]
        if action == "Start":
            user.sessions.append(Session(timestamp, None, None))
        else:
            self.update_active_session(user, timestamp)

    def update_active_session(self, user: User, timestamp: datetime) -> None:
        for session in user.sessions:
            if session.end_time is None:
                session.end_time = timestamp
                session.duration = (session.end_time - session.start_time).seconds
                return
        self.create_new_session(user, timestamp)

    def create_new_session(self, user: User, timestamp: datetime) -> None:
        session = Session(
            self.earliest_time,
            timestamp,
            (timestamp - self.earliest_time).seconds,
        )
        user.sessions.append(session)

    def complete_active_sessions(self) -> None:
        for user in self.users.values():
            for session in user.sessions:
                if session.end_time is None:
                    session.end_time = self.latest_time
                    session.duration = (session.end_time - session.start_time).seconds
                user.total_session_time += session.duration

    def parse_log_file(self) -> None:
        with open(self.file_path, "r", encoding="utf-8") as file:
            for record in file:
                parts = record.strip().split()

                if len(parts) != 3:
                    continue

                time_str, username, action = parts

                try:
                    timestamp = datetime.strptime(time_str, "%H:%M:%S")
                except ValueError:
                    continue

                if not self.is_valid_record(username, action):
                    continue

                self.update_time_range(timestamp)

                if username not in self.users:
                    self.users[username] = User(username, [])

                self.update_user_sessions(username, action, timestamp)

        self.complete_active_sessions()

    def print_user_sessions(self) -> None:
        for user in self.users.values():
            print(f"{user.name} {len(user.sessions)} {user.total_session_time}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python log_parser.py <path_to_log_file>")
        return

    file_path = sys.argv[1]
    parser = LogParser(file_path)
    parser.parse_log_file()
    parser.print_user_sessions()


if __name__ == "__main__":
    main()
