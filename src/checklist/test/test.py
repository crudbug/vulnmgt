import sys
sys.path.append('../../../')
from owndb.checklist import generate_checklist
import webbrowser

CHECKLIST_HTML_FILENAME = 'checklist.html'
OUTPUT_HTML = """
<html>
<head>
    <script type="text/javascript" src="../../static/admin/js/jquery.local.js"></script>
    <script type="text/javascript" src="../../static/admin/js/checklist.js"></script>
    <link rel="stylesheet" type="text/css" href="../../static/admin/css/checklist.css" media="all" />
</head>
<body>
    {0}
</body>
</html>
"""
STATE_BUTTONS_HTML = """
<div class="buttons">
    <button id="save_button" class="button">Save state</button>
    <button id="load_button" class="button">Load state</button>
</div>
<div>
    <textarea id="checklist_state_area"></textarea>
</div>
"""

def main():
    html_content = generate_checklist()
    html_content += STATE_BUTTONS_HTML
    html_output = OUTPUT_HTML.format(html_content)
    with open(CHECKLIST_HTML_FILENAME, 'w') as f:
        f.write(html_output)
    webbrowser.open(CHECKLIST_HTML_FILENAME)



if __name__ == '__main__':
    main()