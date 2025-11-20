import csv
import argparse
from tabulate import tabulate


def parse_arguments() -> (list, str):
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
    file_names: list = args.files.split(" ")
    report_parameter: str = args.report.strip()

    return file_names, report_parameter


def read_csv_files(file_names: list) -> list[dict]:
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


def get_unique_position_dict(input_csv: list) -> dict:
    """
    Получить словарь структуры {должность: [данные о сотрудниках на этой должности]}
    :param input_csv: лист строк csv-файлов с повторяющимися должностями
    :return: dict
    """
    unique_positions: dict = {}
    for row in input_csv:
        position = row.get("position")
        if not position:
            continue
        filtered_row = {key: value for key, value in row.items() if key != "position"}
        if position not in unique_positions:
            unique_positions[position] = []
        unique_positions[position].append(filtered_row)
    return unique_positions


def get_report_for(unique_positions: dict,
                   column_name: str="performance") -> dict:
    """
    Посчитать среднее значение статистики column_name
    для сотрудников на каждой должности в unique_positions.keys().
    :param unique_positions: словарь структуры
    {должность: [данные о сотрудниках на этой должности]}
    :param column_name: параметр, по которому составляем отчёт.
    Параметр должен быть числовым
    :return: финальный отчёт
    """
    report: dict = {}
    for position, employees_list in unique_positions.items():
        average_stat: float = 0.0
        for row in employees_list:
            average_stat += float(row[column_name])
        average_stat /= len(employees_list)
        report[position] = f"{average_stat:.2f}"
    return report


def display_report(report: dict, column_name: str) -> None:
    """
    Отобразить отчёт в виде таблицы.
    :param column_name: заголовок колонки со средним параметром
    :param report: финальный отчёт: {должность: среднее значение}
    :return: None
    """
    sorted_report = sorted(report.items(), key=lambda x: float(x[1]), reverse=True)
    table = [[position, average] for position, average in sorted_report]

    headers = ["position", column_name]
    print(tabulate(table, headers=headers, floatfmt="#.3g"))


if __name__ == "__main__":
    names, report_stat = parse_arguments()
    csv_list = read_csv_files(names)
    unique_pos = get_unique_position_dict(csv_list)
    final_report = get_report_for(unique_pos, report_stat)
    display_report(final_report, report_stat)
