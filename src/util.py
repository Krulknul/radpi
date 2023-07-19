def format_large_number(n):
    if n >= 10**9:
        return str(n // 10**9) + "B"
    elif n >= 10**6:
        return str(n // 10**6) + "M"
    elif n >= 10**3:
        return str(n // 10**3) + "K"
    else:
        return str(n)
