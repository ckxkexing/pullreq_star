from src.utils.languages import (CData, CPPData, CUData, DartData, GoData,
                                 JavaData, JavascriptData, PhpData, PythonData,
                                 RubyData, SassData, ShellData, TypescriptData)


def get_linguist(lang):
    lang_mapping = {
        "javascript": JavascriptData,
        "python": PythonData,
        "dart": DartData,
        "go": GoData,
        "java": JavaData,
        "php": PhpData,
        "ruby": RubyData,
        "sass": SassData,
        "shell": ShellData,
        "typescript": TypescriptData,
        "c": CData,
        "cu": CUData,
        "cpp": CPPData,
    }
    linguist = lang_mapping.get(lang.lower(), None)

    return linguist
