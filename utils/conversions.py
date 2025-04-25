
# Função para converter ascensão reta (RA) em graus decimais
def ra_to_deg(ra_str):
    sep = ':' if ':' in ra_str else ' '
    h, m, s = ra_str.replace('h', '').replace('m', '').replace('s', '').split(sep)
    return 15 * (float(h) + float(m) / 60 + float(s) / 3600)

# Função para converter declinação (Dec) em graus decimais
def dec_to_deg(dec_str):
    dec_str = (dec_str.strip()
        .replace(u'\xa0', u'')
        .replace('−', '-')  # sinal de menos especial
        .replace('+', '')   # remove o sinal de mais
        .replace('°', ' ')
        .replace('′', ' ')
        .replace('″', ' '))
    
    parts = dec_str.split()
    d = float(parts[0])
    m = float(parts[1])
    s = float(parts[2])
    
    sign = 1 if d >= 0 else -1
    return d + sign * (m / 60) + sign * (s / 3600)