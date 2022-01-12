def ask(question, **custom_choice_mappers):
    choice_mappers = {
        True: ["", "yes", "y"],
        False: ["no", "n"]
    }
    choice_mappers.update(custom_choice_mappers or {})
    print(question + " [Y/n] ", end="")
    
    choice = input().lower().strip()
    for mapping, answers in choice_mappers.items():
        if choice in answers:
            choice = mapping
    
    return choice
