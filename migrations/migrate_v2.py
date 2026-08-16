import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from core.security import hash_password


MIGRATION_ID = "20260808_ums_v2"
PASSWORD_SCRUB_MIGRATION_ID = "20260808_password_scrub"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def columns(connection: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}


def add_column(connection: sqlite3.Connection, table: str, definition: str) -> None:
    name = definition.split()[0]
    if name not in columns(connection, table):
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {definition}")


def ensure_legacy_tables(connection: sqlite3.Connection) -> None:
    connection.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT)")
    connection.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, fullname TEXT)")
    connection.execute("CREATE TABLE IF NOT EXISTS professors (id INTEGER PRIMARY KEY AUTOINCREMENT, fullname TEXT, department TEXT)")
    connection.execute("CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY AUTOINCREMENT, course_code TEXT, course_name TEXT, units INTEGER, teacher TEXT, capacity INTEGER)")
    connection.execute("CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, course_id INTEGER)")


def create_new_tables(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL UNIQUE,
            is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS semesters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            registration_start TEXT NOT NULL,
            registration_end TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('planned', 'active', 'closed')),
            max_units_default INTEGER NOT NULL DEFAULT 20 CHECK (max_units_default > 0),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS classrooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            building TEXT NOT NULL,
            room_number TEXT NOT NULL,
            capacity INTEGER NOT NULL CHECK (capacity > 0),
            is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE (building, room_number)
        );
        CREATE TABLE IF NOT EXISTS course_prerequisites (
            course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
            prerequisite_course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
            minimum_score REAL NOT NULL DEFAULT 10 CHECK (minimum_score BETWEEN 0 AND 20),
            created_at TEXT NOT NULL,
            PRIMARY KEY (course_id, prerequisite_course_id),
            CHECK (course_id <> prerequisite_course_id)
        );
        CREATE TABLE IF NOT EXISTS course_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
            semester_id INTEGER NOT NULL REFERENCES semesters(id) ON DELETE RESTRICT,
            professor_id INTEGER REFERENCES professors(id) ON DELETE SET NULL,
            classroom_id INTEGER REFERENCES classrooms(id) ON DELETE SET NULL,
            section_number TEXT NOT NULL,
            capacity INTEGER NOT NULL CHECK (capacity > 0),
            status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'closed', 'cancelled')),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE (course_id, semester_id, section_number)
        );
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_section_id INTEGER NOT NULL REFERENCES course_sections(id) ON DELETE CASCADE,
            day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            CHECK (start_time < end_time)
        );
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enrollment_id INTEGER NOT NULL UNIQUE REFERENCES enrollments(id) ON DELETE RESTRICT,
            score REAL CHECK (score BETWEEN 0 AND 20),
            letter_grade TEXT,
            status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published')),
            graded_by_professor_id INTEGER REFERENCES professors(id) ON DELETE SET NULL,
            published_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
    )


def add_v2_columns(connection: sqlite3.Connection) -> None:
    for definition in ("full_name TEXT", "password_hash TEXT", "is_active INTEGER NOT NULL DEFAULT 1", "last_login_at TEXT", "created_at TEXT", "updated_at TEXT"):
        add_column(connection, "users", definition)
    for definition in ("user_id INTEGER", "student_number TEXT", "department_id INTEGER", "major TEXT", "entry_year INTEGER", "academic_status TEXT NOT NULL DEFAULT 'active'", "created_at TEXT", "updated_at TEXT"):
        add_column(connection, "students", definition)
    for definition in ("user_id INTEGER", "department_id INTEGER", "personnel_code TEXT", "employment_status TEXT NOT NULL DEFAULT 'active'", "academic_rank TEXT", "created_at TEXT", "updated_at TEXT"):
        add_column(connection, "professors", definition)
    for definition in ("department_id INTEGER", "description TEXT", "is_active INTEGER NOT NULL DEFAULT 1", "created_at TEXT", "updated_at TEXT"):
        add_column(connection, "courses", definition)
    for definition in ("course_section_id INTEGER", "registered_units INTEGER", "status TEXT NOT NULL DEFAULT 'enrolled'", "enrolled_at TEXT", "dropped_at TEXT", "created_at TEXT", "updated_at TEXT"):
        add_column(connection, "enrollments", definition)


def migrate_data(connection: sqlite3.Connection) -> None:
    now = utc_now()
    connection.execute("INSERT OR IGNORE INTO departments (code, name, is_active, created_at, updated_at) VALUES (?, ?, 1, ?, ?)", ("GENERAL", "General Department", now, now))
    department_id = connection.execute("SELECT id FROM departments WHERE code = 'GENERAL'").fetchone()[0]
    connection.execute("INSERT OR IGNORE INTO classrooms (building, room_number, capacity, is_active, created_at, updated_at) VALUES (?, ?, ?, 1, ?, ?)", ("Legacy", "ONLINE-1", 1000, now, now))
    classroom_id = connection.execute("SELECT id FROM classrooms WHERE building = 'Legacy' AND room_number = 'ONLINE-1'").fetchone()[0]
    connection.execute("INSERT OR IGNORE INTO semesters (code, title, start_date, end_date, registration_start, registration_end, status, max_units_default, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, 'active', 20, ?, ?)", ("LEGACY-CURRENT", "Migrated Current Semester", "2026-01-01", "2030-12-31", "2026-01-01", "2030-12-31", now, now))
    semester_id = connection.execute("SELECT id FROM semesters WHERE code = 'LEGACY-CURRENT'").fetchone()[0]

    for user in connection.execute("SELECT * FROM users").fetchall():
        role = user["role"] if user["role"] in {"admin", "professor", "student"} else "student"
        full_name = user["full_name"] or user["username"]
        password_hash = user["password_hash"] or hash_password(user["password"] or "")
        connection.execute("UPDATE users SET role = ?, full_name = ?, password_hash = ?, created_at = COALESCE(created_at, ?), updated_at = COALESCE(updated_at, ?) WHERE id = ?", (role, full_name, password_hash, now, now, user["id"]))

    for student in connection.execute("SELECT * FROM students").fetchall():
        user_id = student["user_id"] if "user_id" in student.keys() else None
        if not user_id or not connection.execute("SELECT 1 FROM users WHERE id = ?", (user_id,)).fetchone():
            username = student["username"] or f"student_{student['id']}"
            existing = connection.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if existing:
                user_id = existing[0]
            else:
                cursor = connection.execute("INSERT INTO users (username, password, role, full_name, password_hash, is_active, created_at, updated_at) VALUES (?, ?, 'student', ?, ?, 1, ?, ?)", (username, None, student["fullname"] or username, hash_password(student["password"] or ""), now, now))
                user_id = cursor.lastrowid
        connection.execute("UPDATE students SET user_id = ?, student_number = COALESCE(student_number, ?), department_id = COALESCE(department_id, ?), major = COALESCE(major, 'Undeclared'), entry_year = COALESCE(entry_year, 1405), academic_status = COALESCE(academic_status, 'active'), created_at = COALESCE(created_at, ?), updated_at = COALESCE(updated_at, ?) WHERE id = ?", (user_id, f"LEGACY-{student['id']}", department_id, now, now, student["id"]))

    for professor in connection.execute("SELECT * FROM professors").fetchall():
        user_id = professor["user_id"] if "user_id" in professor.keys() else None
        if not user_id:
            username = f"professor_{professor['id']}"
            cursor = connection.execute("INSERT OR IGNORE INTO users (username, role, full_name, password_hash, is_active, created_at, updated_at) VALUES (?, 'professor', ?, ?, 1, ?, ?)", (username, professor["fullname"], hash_password(""), now, now))
            user_id = connection.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()[0]
        connection.execute("UPDATE professors SET user_id = ?, department_id = COALESCE(department_id, ?), personnel_code = COALESCE(personnel_code, ?), department = COALESCE(department, 'General Department'), employment_status = COALESCE(employment_status, 'active'), created_at = COALESCE(created_at, ?), updated_at = COALESCE(updated_at, ?) WHERE id = ?", (user_id, department_id, f"LEGACY-P-{professor['id']}", now, now, professor["id"]))

    for course in connection.execute("SELECT * FROM courses").fetchall():
        connection.execute("UPDATE courses SET department_id = COALESCE(department_id, ?), is_active = COALESCE(is_active, 1), created_at = COALESCE(created_at, ?), updated_at = COALESCE(updated_at, ?) WHERE id = ?", (department_id, now, now, course["id"]))
        count = connection.execute("SELECT COUNT(*) FROM enrollments WHERE course_id = ? AND status = 'enrolled'", (course["id"],)).fetchone()[0]
        capacity = max((course["capacity"] or 0) + count, 1)
        connection.execute("INSERT OR IGNORE INTO course_sections (course_id, semester_id, classroom_id, section_number, capacity, status, created_at, updated_at) VALUES (?, ?, ?, '01', ?, 'open', ?, ?)", (course["id"], semester_id, classroom_id, capacity, now, now))
        section_id = connection.execute("SELECT id FROM course_sections WHERE course_id = ? AND semester_id = ? AND section_number = '01'", (course["id"], semester_id)).fetchone()[0]
        connection.execute("UPDATE enrollments SET course_section_id = COALESCE(course_section_id, ?), registered_units = COALESCE(registered_units, ?), enrolled_at = COALESCE(enrolled_at, ?), created_at = COALESCE(created_at, ?), updated_at = COALESCE(updated_at, ?) WHERE course_id = ?", (section_id, course["units"], now, now, now, course["id"]))

    connection.executescript(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_students_user_id ON students(user_id);
        CREATE UNIQUE INDEX IF NOT EXISTS ux_students_student_number ON students(student_number);
        CREATE UNIQUE INDEX IF NOT EXISTS ux_professors_user_id ON professors(user_id);
        CREATE UNIQUE INDEX IF NOT EXISTS ux_professors_personnel_code ON professors(personnel_code);
        CREATE UNIQUE INDEX IF NOT EXISTS ux_courses_course_code ON courses(course_code);
        CREATE UNIQUE INDEX IF NOT EXISTS ux_enrollments_student_section ON enrollments(student_id, course_section_id);
        CREATE INDEX IF NOT EXISTS ix_students_department_status ON students(department_id, academic_status);
        CREATE INDEX IF NOT EXISTS ix_professors_department ON professors(department);
        CREATE INDEX IF NOT EXISTS ix_courses_department_active ON courses(department_id, is_active);
        CREATE INDEX IF NOT EXISTS ix_sections_semester_status ON course_sections(semester_id, status);
        CREATE INDEX IF NOT EXISTS ix_sections_professor ON course_sections(professor_id);
        CREATE INDEX IF NOT EXISTS ix_schedules_section_day ON schedules(course_section_id, day_of_week);
        CREATE INDEX IF NOT EXISTS ix_enrollments_student_status ON enrollments(student_id, status);
        CREATE INDEX IF NOT EXISTS ix_enrollments_section_status ON enrollments(course_section_id, status);
        """
    )


def run_migrations(path: Path) -> None:
    backup_dir = path.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    backup_path = backup_dir / "university-pre-ums-v2.db"
    if path.exists() and not backup_path.exists():
        shutil.copy2(path, backup_path)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        ensure_legacy_tables(connection)
        create_new_tables(connection)
        if not connection.execute("SELECT 1 FROM schema_migrations WHERE id = ?", (MIGRATION_ID,)).fetchone():
            add_v2_columns(connection)
            migrate_data(connection)
            connection.execute("INSERT INTO schema_migrations (id, applied_at) VALUES (?, ?)", (MIGRATION_ID, utc_now()))
        if not connection.execute("SELECT 1 FROM schema_migrations WHERE id = ?", (PASSWORD_SCRUB_MIGRATION_ID,)).fetchone():
            connection.execute("UPDATE users SET password = NULL")
            connection.execute("UPDATE students SET password = NULL")
            connection.execute("INSERT INTO schema_migrations (id, applied_at) VALUES (?, ?)", (PASSWORD_SCRUB_MIGRATION_ID, utc_now()))
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
