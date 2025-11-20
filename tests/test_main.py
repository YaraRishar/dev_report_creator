import csv
import os.path
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from src import main


def test_parse_arguments():
    test_args = ["--files", "employees1.csv employees2.csv", "--report", "performance"]
    with patch("sys.argv", ["src/dev_report_creator/main.py"] + test_args):
        files, report = main.parse_arguments()
        assert files == ["employees1.csv", "employees2.csv"]
        assert report == "performance"


@pytest.fixture
def establish_content():
    content = [
        {"name": "Olga Kuznetsova", "position": "Frontend Developer", "completed_tasks": "42",
         "performance": "4.6", "skills": "Vue.js, JavaScript, Webpack, Sass",
         "team": "Web Team", "experience_years": "3"},
        {"name": "Elena Popova", "position": "Backend Developer", "completed_tasks": "43",
         "performance": "4.8", "skills": "Java, Spring Boot, MySQL, Redis",
         "team": "API Team", "experience_years": "4"},
        {"name": "Tom Anderson", "position": "Backend Developer", "completed_tasks": "49",
         "performance": "4.9", "skills": "Go, Microservices, gRPC, PostgreSQL",
         "team": "API Team", "experience_years": "7"}
    ]
    return content


@pytest.fixture
def sample_csv_file(establish_content):
    fieldnames = establish_content[0].keys()
    temp_file = tempfile.NamedTemporaryFile(mode="w", newline="", suffix=".csv", delete=False)
    writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
    writer.writeheader()
    for item in establish_content:
        row = {key: value for key, value in item.items()}
        writer.writerow(row)

    temp_file.close()
    yield os.path.abspath(temp_file.name)
    Path(temp_file.name).unlink()


def test_read_csv_files(sample_csv_file, establish_content):
    result = main.read_csv_files([sample_csv_file])
    assert result == establish_content


def test_get_unique_position_dict(establish_content):
    result = main.get_unique_position_dict(establish_content)
    assert "Frontend Developer" in result.keys()
    assert "Backend Developer" in result.keys()
    assert len(result["Frontend Developer"]) == 1
    assert len(result["Backend Developer"]) == 2


def test_get_report_for():
    content = {
        "Mobile Developer": [
            {"name": "David Chen", "completed_tasks": "36", "performance": "4.6",
             "skills": "Swift, Kotlin, React Native, iOS", "team": "Mobile Team", "experience_years": "3"},
            {"name": "Lisa Wang", "completed_tasks": "33", "performance": "4.6",
             "skills": "Flutter, Dart, Android, Firebase",
             "team": "Mobile Team", "experience_years": "2"}
        ],
        "Backend Developer": [
            {"name": "Elena Popova", "completed_tasks": "43", "performance": "4.8",
             "skills": "Java, Spring Boot, MySQL, Redis", "team": "API Team", "experience_years": "4"},
            {"name": "Tom Anderson", "completed_tasks": "49", "performance": "4.9",
             "skills": "Go, Microservices, gRPC, PostgreSQL",
             "team": "API Team", "experience_years": "7"}]}

    report = main.get_report_for(content, "performance")
    assert report["Mobile Developer"] == "4.60"
    assert report["Backend Developer"] == "4.85"


def test_display_report(capsys):
    report = {"Mobile Developer": "4.6", "Frontend Developer": "4.33", "Data Engineer": "4.7"}
    main.display_report(report, "performance")
    captured = capsys.readouterr()
    assert "Mobile Developer" in captured.out
    assert "4.60" in captured.out
    assert "4.33" in captured.out