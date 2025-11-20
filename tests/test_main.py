import csv
import os.path
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from src import main
from src.main import Developer, PerformanceReport


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


@pytest.fixture
def developers_list(establish_content) -> list[Developer]:
    dev_list = []
    for dev in establish_content:
        dev_list.append(main.parse_developer(dev))
    return dev_list


def test_parse_developer(developers_list):
    assert developers_list[0].name == "Olga Kuznetsova"
    assert developers_list[1].position == "Backend Developer"


def test_performance_report(developers_list):
    report = PerformanceReport.generate(developers_list)
    assert report["Frontend Developer"] == "4.60"
    assert report["Backend Developer"] == "4.85"


def test_display_report(capsys):
    report = {"Mobile Developer": "4.6", "Frontend Developer": "4.33", "Data Engineer": "4.7"}
    main.display_report(report, ["position", "performance"])
    captured = capsys.readouterr()
    assert "Mobile Developer" in captured.out
    assert "4.60" in captured.out
    assert "4.33" in captured.out