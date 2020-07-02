#! /usr/bin/python3
import os
import sys
import json
from colorama import Fore, Back, Style 
from enum import Enum

#task = [
#    {
#        "name": "refactor src directory",
#        "status": "in progress",
#        "subtasks": [
#            {
#                "name": "refactor main.cpp",
#                "status": "completed", 
#                "subtasks": [
#                    {
#                        "name": "compile main.cpp",
#                        "status": "completed",
#                        "subtasks": []
#                    }
#                ] 
#            },
#
#            {
#                "name": "refactor main.h",
#                "status": "todo",
#                "subtasks" : []
#            }  
#        ]
#    },
#    {
#        "name": "refactor src directory",
#        "status": "in progress",
#        "subtasks": [
#            {
#                "name": "refactor main.cpp",
#                "status": "completed", 
#                "subtasks": [
#                    {
#                        "name": "compile main.cpp",
#                        "status": "completed",
#                        "subtasks": []
#                    }
#                ] 
#            },
#
#            {
#                "name": "refactor main.h",
#
#                "status": "todo",
#                "subtasks" : []
#            }  
#         ]
#    }
#]

class Status(Enum):

        TO_DO = 0
        IN_PROGRESS = 1
        COMPLETED = 2

class Task:
    
    def __init__(self, name, subtasks=[], status=Status.TO_DO):
        self.name = name

        if status == Status.TO_DO:
            self.status = status
        else:
            if status == "in progress":
                self.status = Status.IN_PROGRESS
            else:
                self.status = Status.COMPLETED

        if subtasks is not None:
            self.subtasks = {
                subtask["name"]: Task(subtask["name"], subtask["subtasks"], subtask["status"]) for subtask in subtasks   
            }
    
    def display(self, recurse=True, pre=""):
        color = None
        if self.status == Status.TO_DO:
            color = Fore.RED
        elif self.status == Status.IN_PROGRESS:
            color = Fore.YELLOW
        else:
            color = Fore.GREEN
        print(color + pre  + self.name)
        
        if recurse:
            for subtask in self.subtasks.values():
                subtask.display(pre=pre + "\t")

def initialize(cwd):
    """
    this function checks if there is already a taskr directory in the current working directory,
    and created one of not
    """
    taskr_dir = os.path.join(cwd, ".taskr")
    try:
        os.makedirs(taskr_dir)    
    except FileExistsError:
        print("Taskr already initialized for this directory")
        return
    default_props = {
        'selected': 0
    }
    with open(os.path.join(taskr_dir, 'taskr.props'), 'w+') as taskr_json:
        json.dump(default_props, taskr_json, indent=4)

def load_tasks(cwd):
    tasks = None
    with open(os.path.join(cwd, '.taskr', 'tasks.json')) as tasks_json:
        tasks = json.load(tasks_json)
    return tasks

def update_tasks(cwd, new_tasks):
    with open(os.path.join(cwd, '.taskr', 'tasks.json'), 'w+') as tasks_json:
        json.dump(new_tasks, tasks_json, indent=4)

def load_props(cwd):
    tasks = None
    with open(os.path.join(cwd, '.taskr', 'taskr.props')) as tasks_json:
        tasks = json.load(tasks_json)
    return tasks

def update_props(cwd, new_tasks):
    with open(os.path.join(cwd, '.taskr', 'taskr.props'), 'w+') as tasks_json:
        json.dump(new_tasks, tasks_json, indent=4)

def add_task(taskr_dir, task_args):
    print(task_args)
    
    task = { # default values for a new task
        'status': 'todo',
        'subtasks' : []
    }

    for arg in task_args:
        arg_split = arg.split("=")
        task[arg_split[0]] = arg_split[1]
    tasks = load_tasks(taskr_dir)
    tasks.append(task)
    update_tasks(taskr_dir, tasks)

def add_subtask(taskr_dir, task_args, parent_task=0):
    tasks = load_tasks(taskr_dir)
    props = load_props(taskr_dir)
    if props['selected'] == 0 and parent_task == 0:
        print("no sepected task. See 'taskr select' or use '--parent-task' flag")
        return

    task = { # default values for a new task
        'status': 'todo',
        'subtasks' : []
    }

    for arg in task_args:
        arg_split = arg.split("=")
        task[arg_split[0]] = arg_split[1]

    selected_id = props['selected'].split('.')
    selected = tasks[int(selected_id[0]) - 1]
    if len(selected_id) > 1:
        for num in selected_id[1::]:
            selected = selected['subtasks'][int(num) - 1]

    selected['subtasks'].append(task)
    update_tasks(taskr_dir, tasks)

def select_task(taskr_dir, task_id, absolute=False):
    """
    this function is used by 'taskr select'
    """

    task_id_arr = task_id.split('.')
    props = load_props(taskr_dir)
    tasks = load_tasks(taskr_dir) # load tasks.json
    selected = None
    try:
        if props['selected'] == 0 or not absolute: #if using absolute ID, load tasks.json and get task by absolute ID, then update props
            selected = tasks[int(task_id[0]) - 1]
            for num in task_id_arr[1::]:
                selected = selected['subtasks'][int(num) - 1]
            props['selected'] = task_id
    
        #otherwise get the current task ID and go from there
        else:
            current = props['selected'].split('.')
            selected = tasks[int(current[0]) - 1]
            for num in current[1::]:
                selected = selected['subtasks'][int(num) - 1]
    except:
        print('Invalid task id')
    
    update_props(taskr_dir, props)

if __name__ == "__main__":
    #t = Task(task["name"], task["subtasks"])
    argc = len(sys.argv)
    taskr_dir = os.getcwd()
    if argc > 1:
        if sys.argv[1] == 'init':
            print("initializing task in directory", taskr_dir)
            initialize(taskr_dir)
        if sys.argv[1] == 'add':
            #add_task(taskr_dir, sys.argv[2::])
            if sys.argv[2] == 'subtask':
                add_subtask(taskr_dir, sys.argv[3::])
            else:
                add_task(taskr_dir, sys.argv[2::])

        if sys.argv[1] == 'select':
            select_task(taskr_dir, sys.argv[2])
              
    #t = Task(task["name"], task["subtasks"])

    #t.display()


    #if sys.argv[1] == '--list':
    #   print(Fore.YELLOW + task["name"])
    #   for subtask in task["subtasks"]:
    #       if subtask["completed"]:
    #           print(Fore.GREEN + "\t" + subtask["name"])
    #       else:
    #           print(Fore.RED + "\t" + subtask["name"]) 
