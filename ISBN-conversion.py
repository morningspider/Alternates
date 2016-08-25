def is_valid(ISBN):
    if len(ISBN) not in (10,13):
        return False

    if len(ISBN) == 10:
        s = 0
        if ISBN[-1] == 'X' or ISBN[-1] == 'x':
            isbn = int(ISBN[:-1])
            i = 2
            s += 10
        else:
            isbn = int(ISBN)
            i = 1

        while i < 11:
            d = isbn%10
            s += i*d
            isbn //= 10
            print(i, s, d)
            i+=1

        if s % 11 == 0:
            return True
        else:
            return False

    if len(ISBN) == 13:
        s = 0
        isbn = int(ISBN)

        for i in range(1,14):
            d = isbn%10
            if i % 2 == 0:
                s+= d*3
            else:
                s += d
            isbn //= 10
            print(i, s, d)

        if s % 10 == 0:
            return True
        else:
            return False

def ISBN13_to_10(ISBN):
    truncated = int(ISBN[3:-1])
    s = 0
    for i in range(2,11):
        digit = truncated%10
        s += i*digit
        truncated //= 10
    check = (-s) % 11
    if check == 10:
        check = 'X'
    output = "{}{}".format(ISBN[3:-1], check)
    return output

print(ISBN13_to_10("9780078951152"))
