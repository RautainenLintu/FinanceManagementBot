def checkDate(string_date):
    part_list = string_date.split("-")
    if len(part_list) != 3:
        return False
    if (len(part_list[0]) != 4) or (len(part_list[1]) != 2) or (len(part_list[2]) != 2):
        return False
    for item in part_list:
        for letter in item:
            if letter not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                return False
    return True