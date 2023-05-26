from commandExec import execute
import re


def get_view():
    focus_index = [3,6]
    # focus_index= [4,8]
    out = execute('dumpsys SurfaceFlinger | grep -i focus -A 10')
    a = out.split('\n')
    view = ""
    for index in focus_index:
        if a[index][-2] == '*':
            view = a[index-2]
            view = a[index-1]
            break
    view = view.strip()
    print(f'current view:{view}')

    out = execute('dumpsys SurfaceFlinger --list')
    a = out.split('\n')
    # pattern = r'SurfaceView\[com\.miHoYo\.Yuanshen\/com\..*?\.GetMobileInfo\.MainActivity\]\(BLAST\)#0'
    escaped_text = re.escape(view)
    pattern = escaped_text.replace(re.escape('[...]'), '.*?')
    print(pattern)

    result = re.findall(pattern, out)

    print(f'current result is {result}')
    return re.escape(result[0])
