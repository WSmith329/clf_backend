from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
import json


class ListTextInputWidget(Widget):
    template_name = None

    def render(self, name, value, attrs=None, renderer=None):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                value = []

        if value is None:
            value = []

        html = '<div id="list-input-container" class="form-field flex-col gap-y-2 justify-end">'
        for i, item in enumerate(value):
            html += f'<div class="flex items-center gap-x-1"><p>#{i+1}</p><input type="text" name="{name}" value="{item}" class="form-input" /></div>'
        html += f'<input type="text" name="{name}" class="form-input" />'
        html += f'''
                    <button type="button" onclick="addListInput()" class="create-button order-last">
                        Add more
                    </button>
                </div>
                <script>
                    function addListInput() {{
                        const container = document.getElementById('list-input-container');
                        const input = document.createElement('input');
                        input.type = 'text';
                        input.name = '{name}';
                        input.classList.add('form-input')
                        container.appendChild(input);
                    }}
                </script>
                '''
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        values = data.getlist(name)
        cleaned = [v for v in values if v.strip()]
        return json.dumps(cleaned)
