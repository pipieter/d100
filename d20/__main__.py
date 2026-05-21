import os
import time

from d20 import roll, distribution

try:
    import readline  # type: ignore
except:
    pass  # readline not found, don't support history

quit_words = ["quit", "stop", "halt", "exit"]
max_width = 64


def handle_roll(expr: str) -> None:
    result = roll(expr)
    print(result.result)


def handle_distribution(expr: str) -> None:
    dist = distribution(expr)
    timer_start = time.time()
    timer_end = time.time()

    mean = f"{dist.mean():.2f}"
    stdev = f"{dist.stdev():.2f}"
    duration = timer_end - timer_start
    mean_padding = max(len(mean), len(stdev))

    line_width = min(os.get_terminal_size().columns, max_width)

    keys = dist.keys()
    values = dist.values()

    if any(not isinstance(key, int) for key in keys):  # type: ignore # specific case in expression like 0.5 * 1d8, where the values are converted to floats
        raise ValueError("Distribution contains non-integer keys, and cannot be visualized.")

    min_key = min(keys)
    max_key = max(keys)
    max_value = max(values)
    key_lengths = [len(str(key)) for key in keys]
    value_lengths = [len(f"{100 * value:.3f}") for value in values]

    key_print_width = max(key_lengths)
    value_print_width = max(value_lengths)

    def format_entry(key: int, value: float) -> str:
        key_str = str(key)
        val_str = f"{(100*value):.3f}"
        return f"{key_str.rjust(key_print_width)}.  {val_str.rjust(value_print_width)}%"

    total_width_for_bars = line_width - len(format_entry(max(key_lengths), max(value_lengths))) - 2

    # Only print the bars if sufficient space
    print_chart_bars = total_width_for_bars >= 10
    white_square = "\u2588"

    print(f"Calculation time: {duration:.2f} seconds")
    print(f"Mean:  {mean.rjust(mean_padding)}")
    print(f"Stdev: {stdev.rjust(mean_padding)}")
    print()

    for key in range(min_key, max_key + 1):
        value = dist.get(key)

        number_of_bars = 0
        if print_chart_bars:
            number_of_bars = int(total_width_for_bars * value / max_value)
        bars = number_of_bars * white_square

        print(f"{format_entry(key, value)}  {bars}")


while True:
    try:
        expr = input("> ").strip().lower()

        if expr == "":
            continue

        if expr in quit_words:
            break

        try:
            if expr.startswith("roll"):
                expr = expr.lstrip("roll").strip()
                handle_roll(expr)

            elif expr.startswith("distribution"):
                expr = expr.lstrip("distribution").strip()
                handle_distribution(expr)

            else:
                print(f"Unsupported command: '{expr}'")

        except Exception as e:
            print(f"Could not parse '{expr}': {str(e)}")

    # Graciously exit on CTRL+C
    except KeyboardInterrupt:
        print()
        break

    # Graciously exit on CTRL+D
    except EOFError:
        print()
        break

    except Exception as e:
        print(f"Error: {str(e)}")

    print()