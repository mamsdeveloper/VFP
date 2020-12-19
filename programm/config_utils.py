def get_congif_path(filename):
    import os, sys
    app_dir = sys.path[0] or os.path.dirname(os.path.realpath(sys.argv[0])) or os.getcwd() 
    filepath = os.path.join(app_dir,filename)

    return filepath


def save_config(self):
    from configparser import ConfigParser
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

    # create config
    main_config = ConfigParser()

    # scholl settings
    main_config['SCHOOL'] = {'name': school_name}

    # teacher settings
    main_config['TEACHER'] = teacher

    # save main configs
    path = get_congif_path('main.ini')
    with open(path, "w") as config_file:
        main_config.write(config_file)
        config_file.close()


    # exercises
    classes_config = ConfigParser()

    exps = self.classes_exps
    for exp in exps:
        exp_box = exp.children[1]

        # number of classes group
        group = exp_box.children[-1].children[1].text
        # validate group
        if not group:
            continue

        # add group section
        classes_config.add_section(group.title())

        # add classes in group
        for item in reversed(exp.items_list.children):
            class_name = item.children[1].children[1].text
            # validate
            if not class_name:
                continue

            classes_config[group.title()][class_name] = str(item.students)
    
    # save classes configs
    path = get_congif_path('classes.ini')
    with open(path, "w") as config_file:
        classes_config.write(config_file)
        config_file.close()
    
    # classes
    exercises = ConfigParser()

    exps = self.exercises_exps
    for exp in exps:
        exp_box = exp.children[1]

        # number of classes group
        exercise = exp_box.children[-1].children[1].text
        # validate group
        if not exercise:
            continue

        # add group section
        exercises.add_section(exercise)

        # add classes in group
        for item in reversed(exp.items_list.children):
            exercise_name = item.children[1].children[1].text
            # validate
            if not exercise_name:
                continue

            exercises[exercise][exercise_name] = str(item.standarts)
    
    # save classes configs
    path = get_congif_path('exercises.ini')
    with open(path, "w") as config_file:
        exercises.write(config_file)
        config_file.close()
    

def get_config():
    from configparser import ConfigParser
    # open main config
    main_config = ConfigParser()
    path = get_congif_path('main.ini')
    main_config.read(path)

    # school
    school_name = main_config['SCHOOL']['name']

    # teacher
    teacher = dict(main_config['TEACHER'].items())

    # open classes config
    classes_config = ConfigParser()
    path = get_congif_path('classes.ini')
    classes_config.read(path)

    # get group-classes-students
    groups = {}
    for group in classes_config.sections():
        groups.update({group: []})
        for class_item in classes_config[group].items():
            # str to list
            cls = [class_item[0], class_item[1]]
            cls[1] = cls[1].replace("'", '')
            cls[1] = cls[1][1:-1].split(', ')
            cls[1] = list(filter(lambda student: student!='', cls[1]))

            groups[group].append(cls)
    
    
    # open exercises config
    exercises_config = ConfigParser()
    path = get_congif_path('exercises.ini')
    exercises_config.read(path)

    # get group-classes-students
    exercises = {}
    for exercise in exercises_config.sections():
        exercises.update({exercise: []})
        for exercise_item in exercises_config[exercise].items():
            # str to list
            exr = [exercise_item[0], exercise_item[1]]
            exr[1] = exr[1].replace("'", '')
            exr[1] = exr[1][1:-1].split(', ')
            exr[1] = list(filter(lambda student: exercise!='', exr[1]))

            exercises[exercise].append(exr)

    return {
            'school_name': school_name, 
            'teacher': teacher, 
            'groups': groups,
            'exercises': exercises,
            }

