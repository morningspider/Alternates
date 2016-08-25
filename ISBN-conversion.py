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

print(is_valid("9780078250835"))
