import csv
import argparse
from dataclasses import dataclass
from tabulate import tabulate


@dataclass
class Developer:
    """
    Предполагается, что поля не изменятся в вводных csv и данные валидны
    """
    name: str
    position: str
    completed_tasks: int
    performance: float
    skills: list[str]
    team: str
    experience_years: int

def parse_developer(row: dict) -> Developer:
    """
    Превратить каждую строку csv-файла в объект Developer
    :param row:
    :return:
    """
    return Developer(
        name=row.get("name").strip(),
        position=row.get("position").strip(),
        completed_tasks=int(row.get("completed_tasks")),
        performance=float(row.get("performance")),
        skills=[s.strip() for s in row.get("skills").split(",") if s.strip()],
        team=row.get("team").strip(),
        experience_years=int(row.get("experience_years")),
    )


class Report:
    """
    Шаблон для всех классов отчётов
    """
    name: str
    description: str
    header_names: list[str]
    def generate(self, developers: list[Developer]) -> dict[str, str]:
        pass


REPORTS: dict[str, Report] = {}


def register_report(report_implementation) -> None:
    """
    Зарегистрировать класс отчёта для дальнейшего использования
    :param report_implementation:
    :return:
    """
    REPORTS[report_implementation.name] = report_implementation


def parse_arguments() -> (list[str], str):
    """
    Получить relative-пути к файлам и сравниваемый параметр из командной строки.
    :return: tuple(файлы, параметр)
    """
    parser = argparse.ArgumentParser(
        prog="dev_report_creator",
        description="Скрипт читает csv-файлы с данными и формирует отчёты.")
    parser.add_argument("--files",
                        help="Relative-пути к читаемым файлам")
    parser.add_argument("--report",
                        help="Параметр из файлов, по которому будет составляться отчёт")
    args = parser.parse_args()
    file_names: list[str] = args.files.split(" ")
    report_parameter: str = args.report.strip()
    return file_names, report_parameter


def read_csv_files(file_names: list[str]) -> list[dict]:
    """
    Прочитать содержимое всех файлов из [file_names] и записать его построчно в [input_csv]
    :param file_names: relative-пути к csv файлам
    :return: список строк csv-файлов
    """
    input_csv = []
    for file_name in file_names:
        with open(file_name, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                input_csv.append(row)
    return input_csv


def display_report(report: dict[str, str], headers: list[str]) -> None:
    """
    Отобразить отчёт в виде таблицы.
    :param report: финальный отчёт: {должность: среднее значение}
    :param headers: заголовок таблицы
    :return: None
    """
    sorted_report = sorted(report.items(), key=lambda x: float(x[1]), reverse=True)
    table = [[position, average] for position, average in sorted_report]
    print(tabulate(table, headers=headers, floatfmt="#.3g"))

# ----------------------------------

class PerformanceReport:
    """
    Пример класса отчёта. Чтобы добавить новый, скопируйте этот класс и поменяйте логику в generate
    для нового класса, а также замените атрибуты name, description и header_names (если нужно).
    После зарегистрируйте класс с помощью вызова функции register_report(ReportClassName())
    """
    name = "performance"
    description = "Среднее арифметическое показателя performance по должностям"
    header_names = ["position", "performance"]

    @staticmethod
    def generate(developers: list[Developer]) -> (dict[str, str]):
        grouped_by: dict[str, list[Developer]] = {}
        for dev in developers:
            new_item = grouped_by.setdefault(dev.position, [])
            new_item.append(dev)

        report: dict[str, str] = {}
        for position, developers in grouped_by.items():
            total = sum(d.performance for d in developers)
            average = total / len(developers) if developers else 0.0
            report[position] = f"{average:.2f}"
        return report


register_report(PerformanceReport())


if __name__ == "__main__":
    names, report_stat = parse_arguments()
    csv_list = read_csv_files(names)
    devs = [parse_developer(row) for row in csv_list]

    report_class = REPORTS.get(report_stat)
    if not report_class:
        print("Отчёт не добавлен! Доступные отчёты:")
        for key, value in REPORTS.items():
            print(f" - {key}: {value.description}")
        print("Как добавить новый тип отчёта: "
              "https://github.com/YaraRishar/dev_report_creator?tab=readme-ov-file")
        raise KeyError

    final_report = report_class.generate(devs)
    header_name = report_class.header_names
    display_report(final_report, header_name)
