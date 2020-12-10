from configparser import ConfigParser  # импортируем библиотеку


def get_congif_path():
    import os, sys
    filename = 'settings.ini'
    app_dir = sys.path[0] or os.path.dirname(os.path.realpath(sys.argv[0])) or os.getcwd() 
    filepath = os.path.join(app_dir,filename)

    return filepath


def save_config(self):
    # screen area widgets
    all_widgets = self.children[0].children[1].children[0]

    # get school name
    school_name = all_widgets.children[-2].text

    # get teacher data
    teacher_list = all_widgets.children[-4]

    teacher = {
                'name': teacher_list.children[2].text,
                'rank': teacher_list.children[1].text,
                'post': teacher_list.children[0].text
                }

    # create config
    config = ConfigParser()

    # scholl settings
    config['SCHOOL'] = {'name': school_name}

    # teacher settings
    config['TEACHER'] = teacher

    # panels
    exps = reversed(all_widgets.children[1].children)
    
    for exp in exps:
        exp_box = exp.children[1]

        # number of classes group
        group = exp_box.children[-1].children[1].text
        # validate group
        if not group:
            continue

        # add group section
        config.add_section(group.title())

        # add classes in group
        for item in reversed(exp.items_list.children):
            class_name = item.children[1].children[1].text
            # validate
            if not class_name:
                continue

            config[group.title()][class_name] = str(item.students)

    # save congfig
    path = get_congif_path()
    with open(path, "w") as config_file:
        config.write(config_file)
        config_file.close()
    

def get_config():
    # create config
    config = ConfigParser()
    path = get_congif_path()
    config.read(path)

    # school
    school_name = config['SCHOOL']['name']

    # teacher
    teacher = dict(config['TEACHER'].items())

    # get all sections exclude school and teacher
    sections = config.sections()[2:]
    
    # get group-classes-students
    groups = {}
    for group in sections:
        groups.update({group: []})

        for class_item in config[group].items():
            # str to list
            cls = [class_item[0], class_item[1]]
            cls[1] = cls[1].replace("'", '')
            cls[1] = cls[1][1:-1].split(', ')

            groups[group].append(cls)

    return {
            'school_name': school_name, 
            'teacher': teacher, 
            'groups': groups
            }

