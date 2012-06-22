# -*- coding: utf-8 -*-

import os, sys

from log import logging
import out

COMMANDS_DICT = {
    # User
    "user": {
        "help": "Create note",
        "flags": {
            "--full": {"help": "Add tag to note", "value": True, "default": False},
        }
    },
    "login": {
        "help": "Create note",
    },
    "logout": {
        "help": "Create note",
        "flags": {
            "--force": {"help": "Add tag to note", "value": True, "default": False},
        }
    },

    # Notes
    "create": {
        "help": "Create note",
        "arguments": {
            "--title": {"help": "Set note title", "required": True},
            "--content": {"help": "Set note content", "required": True},
            "--tags": {"help": "Add tag to note"},
            "--notebook": {"help": "Add location marker to note"}
        }
    },
    "edit": {
        "help": "Create note",
        "firstArg": "--note",
        "arguments": {
            "--note": {"help": "Set note title"},
            "--title": {"help": "Set note title"},
            "--content": {"help": "Set note content"},
            "--tags": {"help": "Add tag to note"},
            "--notebook": {"help": "Add location marker to note"}
        }
    },
    "remove": {
        "help": "Create note",
        "firstArg": "--note",
        "arguments": {
            "--note": {"help": "Set note title"},
        },
        "flags": {
            "--force": {"help": "Add tag to note", "value": True, "default": False},
        }
    },
    "show": {
        "help": "Create note",
        "firstArg": "--note",
        "arguments": {
            "--note": {"help": "Set note title"},
        }
    },
    "find": {
        "help": "Create note",
        "firstArg": "--search",
        "arguments": {
            "--search": {"help": "Add tag to note"},
            "--tags": {"help": "Add tag to note"},
            "--notebooks": {"help": "Add location marker to note"},
            "--date": {"help": "Add location marker to note"},
            "--count": {"help": "Add location marker to note", "type": int},
        },
        "flags": {
            "--exact-entry": {"help": "Add tag to note", "value": True, "default": False},
            "--content-search": {"help": "Add tag to note", "value": True, "default": False},
            "--url-only": {"help": "Add tag to note", "value": True, "default": False},
        }
    },

    # Notebooks
    "list-notebook": {
        "help": "Create note",
    },
    "create-notebook": {
        "help": "Create note",
        "arguments": {
            "--title": {"help": "Set note title"},
        }
    },
    "edit-notebook": {
        "help": "Create note",
        "firstArg": "--notebook",
        "arguments": {
            "--notebook": {"help": "Set note title"},
            "--title": {"help": "Set note title"},
        }
    },
    "remove-notebook": {
        "help": "Create note",
        "firstArg": "--notebook",
        "arguments": {
            "--notebook": {"help": "Set note title"},
        },
        "flags": {
            "--force": {"help": "Add tag to note", "value": True, "default": False},
        }
    },
}
class argparser(object):

    COMMANDS = COMMANDS_DICT

    def __init__(self, sys_argv):
        self.LVL = len(sys_argv)
        self.INPUT = sys_argv

        #список команд
        self.CMD_LIST = self.COMMANDS.keys()
        # введенная команда
        self.CMD = None if self.LVL == 0 else self.INPUT[0]
        # список возможных аргументов введенной команды
        self.CMD_ARGS  = self.COMMANDS[self.CMD]['arguments'] if self.LVL > 0 and self.COMMANDS.has_key(self.CMD) and self.COMMANDS[self.CMD].has_key('arguments') else {}
        # список возможных флагов введенной команды
        self.CMD_FLAGS = self.COMMANDS[self.CMD]['flags'] if self.LVL > 0 and self.COMMANDS.has_key(self.CMD) and self.COMMANDS[self.CMD].has_key('flags') else {}
        # список введенных аргументов и их значений
        self.INP = [] if self.LVL <= 1 else self.INPUT[1:]

        logging.debug("CMD_LIST : %s", str(self.CMD_LIST))
        logging.debug("CMD: %s", str(self.CMD))
        logging.debug("CMD_ARGS : %s", str(self.CMD_ARGS))
        logging.debug("CMD_FLAGS : %s", str(self.CMD_FLAGS))
        logging.debug("INP : %s", str(self.INP))

    def parse(self):
        self.INP_DATA = {}

        if self.CMD == "--help":
            self.printHelp()
            return False

        if self.CMD is None or not self.COMMANDS.has_key(self.CMD):
            self.printErrorCommand()
            return False

        if "--help" in self.INP:
            self.printHelp()
            return False

        # подготовка к парсингу
        for arg, params in (self.CMD_ARGS.items() + self.CMD_FLAGS.items()):
            # установка значений по умолчаеию
            if params.has_key('default'):
                self.INP_DATA[arg] = params['default']

        activeArg = None
        # проверяем и подставляем первый адгумент по умолчанию
        if self.COMMANDS[self.CMD].has_key('firstArg'):
            firstArg = self.COMMANDS[self.CMD]['firstArg']
            if len(self.INP) > 0:
                # смотрим что первое знаение не аршумент по умолчанию, а другой аргумент
                if self.INP[0] != firstArg and self.INP[0] in (self.CMD_ARGS.keys() + self.CMD_FLAGS.keys()):
                    self.printErrorReqArgument(firstArg)
                    return False
                elif self.INP[0] != firstArg:
                    self.INP = [firstArg, ] + self.INP
            else:
                self.INP = [firstArg, ]
        

        for item in self.INP:
            # Проверяем что ожидаем аргумент
            if activeArg is None:
                # Действия для аргумента
                if self.CMD_ARGS.has_key(item):
                    activeArg = item

                # Действия для флага
                elif self.CMD_FLAGS.has_key(item):
                    self.INP_DATA[item] = self.CMD_FLAGS[item]["value"]

                # Ошибка параметр не найден
                else:
                    self.printErrorArgument(item)
                    return False

            else:
                # Ошибка значения является параметром
                if self.CMD_ARGS.has_key(item) or self.CMD_FLAGS.has_key(item):
                    self.printErrorArgument(activeArg, item)
                    return False

                if self.CMD_ARGS[activeArg].has_key("type"):
                    convType = self.CMD_ARGS[activeArg]['type']
                    if convType not in ('int', 'str'):
                        logging.error("Unsupported argument type: %s", convType)
                        return False

                    try:
                        item = convType(item)
                    except:
                        self.printErrorArgument(activeArg, item)
                        return False

                self.INP_DATA[activeArg] = item
                activeArg = None

        if activeArg is not None:
            self.printErrorArgument(activeArg, "")
            return False

        # проверка, присутствует ли необходимый аргумент запросе
        for arg, params in (self.CMD_ARGS.items() + self.CMD_FLAGS.items()):
            if params.has_key('required') and arg not in self.INP:
                self.printErrorReqArgument(arg)
                return False

        # trim -- and ->_
        self.INP_DATA = dict([key.lstrip("-").replace("-", "_"), val] for key, val in self.INP_DATA.items() )
        return self.INP_DATA


    def printAutocomplete(self):

        # последнее веденное значение
        LAST_VAL = self.INP[-1] if self.LVL > 1 else None
        PREV_LAST_VAL = self.INP[-2] if self.LVL > 2 else None
        ARGS_FLAGS_LIST = self.CMD_ARGS.keys()+self.CMD_FLAGS.keys()

        # печатаем корневые команды
        if self.CMD is None:
            self.printGrid(CMD_LIST)

        # работа с корневыми командами
        elif not self.INP:

            # печатаем аргументы если команда найдена
            if self.CMD in self.CMD_LIST:
                self.printGrid(ARGS_FLAGS_LIST)

            # автозаполнение для неполной команды
            else:
                # фильтруем команды подходящие под введенный шаблон
                self.printGrid([item for item in self.CMD_LIST if item.startswith(self.CMD)])

        # обработка аргументов
        else:

            # фильтруем аргументы которые еще не ввели
            if self.CMD_ARGS.has_key(PREV_LAST_VAL) or self.CMD_FLAGS.has_key(LAST_VAL) :
                printGrid([item for item in ARGS_FLAGS_LIST if item not in INP]) 

            # автозаполнение для неполной команды
            elif not self.CMD_ARGS.has_key(PREV_LAST_VAL):
                self.printGrid([item for item in ARGS_FLAGS_LIST if item not in INP and item.startswith(LAST_VAL)])

            # обработка аргумента
            else:
                print "" #"Please_input_%s" % INP_ARG.replace('-', '')

    def printGrid(self, list):
        out.printLine(" ".join(list))

    def printErrorCommand(self):
        out.printLine('Unexpected command "%s"' % (self.CMD))
        self.printHelp()

    def printErrorReqArgument(self, errorArg):
        out.printLine('Not found required argument "%s" for command "%s" ' % (errorArg, self.CMD))
        self.printHelp()

    def printErrorArgument(self, errorArg, errorVal=None):
        if errorVal is None:
            out.printLine('Unexpected argument "%s" for command "%s"' % (errorArg, self.CMD))
        else:
            out.printLine('Unexpected value "%s" for argument "%s"' % (errorVal, errorArg))
        self.printHelp()

    def printHelp(self):
        if self.CMD is None or not self.COMMANDS.has_key(self.CMD):
            tab = len(max(self.COMMANDS.keys(), key=len))
            out.printLine("Available commands:")
            for cmd in self.COMMANDS:
                out.printLine("%s : %s" % (cmd.rjust(tab, " "), self.COMMANDS[cmd]['help']))

        else:

            tab = len(max(self.CMD_ARGS.keys()+self.CMD_FLAGS.keys(), key=len))

            out.printLine("Options for: %s" % self.CMD)
            out.printLine("Available arguments:")
            for arg in self.CMD_ARGS:
                out.printLine("%s : %s" % (arg.rjust(tab, " "), self.CMD_ARGS[arg]['help']))

            if self.CMD_FLAGS:
                out.printLine("Available flags:")
                for flag in self.CMD_FLAGS:
                    out.printLine("%s : %s" % (flag.rjust(tab, " "), self.CMD_FLAGS[flag]['help']))
