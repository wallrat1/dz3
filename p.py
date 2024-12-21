import re
import argparse
import toml


class ConfigParser:
    def __init__(self):
        self.constants = {}  # Для хранения констант

    def parse(self, text):
        """Парсит входной текст конфигурации."""
        lines = text.splitlines()
        result = {}
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):  # Пропуск пустых строк и комментариев
                continue
            if line.startswith("var"):
                self.handle_constant(line)
            elif "=" in line:
                key, value = self.parse_assignment(line)
                result[key] = value
            else:
                raise ValueError(f"Invalid syntax: {line}")
        return result

    def handle_constant(self, line):
        """Обрабатывает объявление констант."""
        match = re.match(r"var\s+([a-zA-Z][a-zA-Z0-9]*)\s*:=\s*(.+)", line)
        if not match:
            raise ValueError(f"Invalid constant declaration: {line}")
        name, value = match.groups()
        self.constants[name] = self.evaluate(value)

    def parse_assignment(self, line):
        """Обрабатывает присваивание переменных."""
        match = re.match(r"([a-zA-Z][a-zA-Z0-9]*)\s*=\s*(.+)", line)
        if not match:
            raise ValueError(f"Invalid assignment: {line}")
        key, value = match.groups()
        return key, self.parse_value(value.strip())

    def parse_value(self, value):
        """Парсит значение (числа, массивы или выражения)."""
        if re.match(r"^\d+$", value):  # Числа
            return int(value)
        elif value.startswith("(") and value.endswith(")"):  # Массивы
            items = value.strip("()").split(",")
            return [self.parse_value(item.strip()) for item in items]
        elif re.match(r"^\$\{.+\}$", value):  # Выражения
            return self.evaluate(value)
        else:
            raise ValueError(f"Invalid value: {value}")

    def evaluate(self, expression):
        """Вычисляет выражение в постфиксной форме."""
        expression = expression.strip("${}")
        tokens = expression.split()
        stack = []
        for token in tokens:
            if token.isdigit():
                stack.append(int(token))
            elif token in self.constants:
                stack.append(self.constants[token])
            elif token in {"+", "-", "*"}:
                if len(stack) < 2:
                    raise ValueError(f"Invalid expression: {expression}")
                b = stack.pop()
                a = stack.pop()
                if token == "+":
                    stack.append(a + b)
                elif token == "-":
                    stack.append(a - b)
                elif token == "*":
                    stack.append(a * b)
            elif token == "min()":
                if not stack:
                    raise ValueError(f"Invalid expression: {expression}")
                stack.append(min(stack))
            elif token == "len()":
                if not stack:
                    raise ValueError(f"Invalid expression: {expression}")
                stack.append(len(stack))
            else:
                raise ValueError(f"Unknown token: {token}")
        if len(stack) != 1:
            raise ValueError(f"Invalid expression: {expression}")
        return stack[0]


def main():
    parser = argparse.ArgumentParser(description="Config language to TOML converter.")
    parser.add_argument("input", help="Path to input file.")
    args = parser.parse_args()

    try:
        # Чтение входного файла
        with open(args.input, "r") as f:
            config_text = f.read()

        # Парсинг конфигурации
        config_parser = ConfigParser()
        config = config_parser.parse(config_text)

        # Преобразование в TOML
        toml_output = toml.dumps(config)

        # Вывод результата в стандартный вывод
        print(toml_output)
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()

