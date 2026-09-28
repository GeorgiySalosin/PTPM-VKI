import logging
import math
import os
import sys
import traceback

def setup_logging(log_dir: str = "logs", log_file: str = "file_txt.log") -> logging.Logger:
    """
    Setup logger (console + file)
    """
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_path, encoding="utf-8"),
        ],
        force=True,  # reconfigure at next call
    )

    logger = logging.getLogger(__name__)
    logger.info("Logger configured")
    logger.info("App started")
    return logger



def solve(s1: str, s2: str, s3: str):
    """
    Defines triangle type, calculates vertex coordinates. \n\n
    Return coordinates: \n\t NaN: [(-2, -2), (-2, -2), (-2, -2)] ; 
    \n\t Invalid number values: [(-1, -1), (-1, -1), (-1, -1)] ; 
    """
    logger = logging.getLogger(__name__)

    nan_coords = [(-2, -2), (-2, -2), (-2, -2)]
    invalid_coords = [(-1, -1), (-1, -1), (-1, -1)]

# NaN 

    try:
        a = float(s1)
        b = float(s2)
        c = float(s3)
    except (ValueError, TypeError) as e:
        logger.warning(
            "Input data is NaN (not a number): s1=%r, s2=%r, s3=%r | Ошибка: %s",
            s1, s2, s3, e,
        )
        logger.debug("Traceback:\n%s", traceback.format_exc())
        return "", nan_coords

# Infinity + naturality 

    if math.isnan(a) or math.isnan(b) or math.isnan(c):
        logger.warning("NaN values parsed: a=%s, b=%s, c=%s", a, b, c)
        return "", nan_coords

    if not (math.isfinite(a) and math.isfinite(b) and math.isfinite(c)):
        logger.warning("Inf/not finite values parsed: a=%s, b=%s, c=%s", a, b, c)
        return "Not a triangle", invalid_coords

    if a <= 0 or b <= 0 or c <= 0:
        logger.warning(
            "Non-positive values: a=%s, b=%s, c=%s", a, b, c,
        )
        return "Not a triangle", invalid_coords

# Triangle equality principle 

    if (a + b <= c ) or (a + c <= b) or (b + c <= a):
        logger.warning(
            "Triangle equality is not respected: a=%s, b=%s, c=%s",
            a, b, c,
        )
        return "Not a triangle", invalid_coords

# Define triangle type

    if a == b and b == c:
        tri_type = "Equilateral (равносторонний)"
    elif a==b or b==c or a==c:
        tri_type = "Isosceles (равнобедренный)"
    else:
        tri_type = "Scalene (разносторонний)"


 # --- 5. Calculate coordinates ---

    margin = 10
    field_size = 100
    available = field_size - 2 * margin

    max_side = max(a, b, c)
    scale = available / max_side
    sa, sb, sc = a * scale, b * scale, c * scale

    x1, y1 = float(margin), float(field_size - margin)
    x2, y2 = x1 + sa, y1

    x3_local = (sb ** 2 + sa ** 2 - sc ** 2) / (2 * sa)
    y3_local_sq = sb ** 2 - x3_local ** 2
    y3_local = math.sqrt(max(0.0, y3_local_sq))

    x3 = x1 + x3_local
    y3 = y1 - y3_local

    coords = [
        (int(round(x1)), int(round(y1))),
        (int(round(x2)), int(round(y2))),
        (int(round(x3)), int(round(y3))),
    ]

    return tri_type, coords




def main():
    logger = setup_logging()

    tests = [
        ("3", "3", "3"),
        ("3", "3", "4"),
        ("3", "4", "5"),
        ("1", "2", "10"),
        ("-1", "2", "3"),
        ("abc", "2", "3"),
        ("1.5", "2.5", "3.0"),
        ("0", "1", "1"),
        ("inf", "1", "1"),
        ("nan", "1", "1")
    ]

    for s1, s2, s3 in tests:
        params = {"string1": s1, "string2": s2, "string3": s3}
        try:
            tri_type, coords = solve(s1, s2, s3)
        
            logger.info(
                "Success | Params: %s | Result: Type='%s', Coords=%s",
                params, tri_type, coords,
            )
        except Exception as e:
            
            logger.error(
                "Failed | Params: %s | Exception: %s",
                params, e,
            )
            logger.debug("Traceback:\n%s", traceback.format_exc())

    while True:

        a = input()
        b = input()
        c = input()

        params = {"string1": a, "string2": b, "string3": c}
        try:
            tri_type, coords = solve(a, b, c)
        
            logger.info(
                "Success | Params: %s | Result: Type='%s', Coords=%s",
                params, tri_type, coords,
            )
        except Exception as e:
            
            logger.error(
                "Failed | Params: %s | Exception: %s",
                params, e,
            )
            logger.debug("Traceback:\n%s", traceback.format_exc())

            

if __name__ == "__main__":
    main()