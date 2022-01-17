def ask(question, addition=' [Y/n]', **choice_mappers):
    choice_mappers = {
        True: ['', 'yes', 'y'],
        False: ['no', 'n']
    } | (choice_mappers or {})
    
    print(question + addition, end=' ')
    
    choice = input().lower().strip()
    for mapping, answers in choice_mappers.items():
        if choice in answers:
            choice = mapping
    
    return choice
