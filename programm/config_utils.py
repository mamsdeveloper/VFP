def get_config_path():
    import os, sys
    app_dir = sys.path[0] or os.path.dirname(os.path.realpath(sys.argv[0])) or os.getcwd()
    filepath = os.path.join(app_dir, 'config.pkl')
    return filepath


def save_config(self):
    import pickle
    # screen area widgets
    all_widgets = self.children[0].children[1].children[0]

    # get school name
    school_name = self.children[0].children[1].children[0].children[-2].text

    # get teacher data
    teacher_list = all_widgets.children[-4]

    teacher = {
                'name': teacher_list.children[2].text,
                'rank': teacher_list.children[1].text,
                'post': teacher_list.children[0].text
                }

    # classes
    groups = {}
    exps = self.classes_exps
    for exp in exps:
        exp_box = exp.children[1]

        # number of classes group
        group = exp_box.children[-1].children[1].text
        # validate group
        if not group:
            continue

        # add group section
        groups.update({group.title():[]})

        # add classes in group
        for item in reversed(exp.items_list.children):
            class_name = item.children[1].children[1].text
            # validate
            if not class_name:
                continue

            groups[group.title()].append([class_name, list(item.students)])

    # exercises
    exercises = {}
    exps = self.exercises_exps
    for exp in exps:
        exp_box = exp.children[1]

        # number of classes group
        exercise = exp_box.children[-1].children[1].text
        # validate group
        if not exercise:
            continue

        # add group section
        exercises.update({exercise:[]})

        # add classes in group
        for item in reversed(exp.items_list.children):
            group_name = item.children[1].children[1].text
            print(group_name)
            # validate
            if not group_name:
                continue

            exercises[exercise].append([group_name.title(), list(item.standards)])

    config = {
        'school_name': school_name,
        'teacher': teacher,
        'groups': groups,
        'exercises': exercises
    }

    with open(get_config_path(), 'wb') as file:
        pickle.dump(config, file)


def get_config():
    import pickle

    with open(get_config_path(), 'rb') as file:
        config = pickle.load(file)
    
    return config