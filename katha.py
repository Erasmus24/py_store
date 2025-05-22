def return_negative(a):
    if a >= 0:
        return a * (-1)
    else:
        return a

print(return_negative(4))
print(return_negative(15))
print(return_negative(-4))
print(return_negative(0))
print()
def get_sum_of_elements(elements):
    result = 0
    for element in elements:
        result += element
    return result

print(get_sum_of_elements([2, 7, 4]))
print(get_sum_of_elements([45, 3, 0]))
print(get_sum_of_elements([-2, 84, 23]))
