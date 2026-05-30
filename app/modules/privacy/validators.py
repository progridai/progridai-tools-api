import re

def validate_cpf(cpf: str) -> bool:
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) != 11:
        return False
    
    if cpf == cpf[0] * 11:
        return False

    def calc_digit(cpf_substr):
        length = len(cpf_substr)
        sum_val = sum(int(digit) * weight for digit, weight in zip(cpf_substr, range(length + 1, 1, -1)))
        rem = sum_val % 11
        return 0 if rem < 2 else 11 - rem

    d1 = calc_digit(cpf[:9])
    d2 = calc_digit(cpf[:9] + str(d1))

    return cpf[-2:] == f"{d1}{d2}"

def validate_cnpj(cnpj: str) -> bool:
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) != 14:
        return False

    if cnpj == cnpj[0] * 14:
        return False

    def calc_digit(cnpj_substr, weights):
        sum_val = sum(int(digit) * weight for digit, weight in zip(cnpj_substr, weights))
        rem = sum_val % 11
        return 0 if rem < 2 else 11 - rem

    w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    d1 = calc_digit(cnpj[:12], w1)
    
    w2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    d2 = calc_digit(cnpj[:12] + str(d1), w2)

    return cnpj[-2:] == f"{d1}{d2}"
