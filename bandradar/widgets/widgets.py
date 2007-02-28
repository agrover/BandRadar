from turbogears import widgets as w
from turbogears import validators as v
from cgi import escape

class ButtonWidget(w.Widget):
    template = "bandradar.widgets.templates.button"
    params = ['label', 'action']

class ArtistListWidget(w.Widget):
    template = "bandradar.widgets.templates.artistlist"
    params = ['event']

    def get_list(self, event):
        if not event or not event.artists.count():
            artisthtml = "<strong>None</strong>"
        else:
            htmlstr = "<a href=\"/artists/%s\">%s</a>"
            artist_html_list = [ htmlstr % (a.id, escape(a.name)) for a in event.artists ]
            artisthtml = ", ".join(artist_html_list)
        return artisthtml

artistlist = ArtistListWidget()

class AutoCompleteValidator(v.Schema):
    def _to_python(self, value, state):
        text = value['text']
        value['text'] = v.NotEmpty(strip=True).to_python(text)
        return value

class BRAutoCompleteField(w.AutoCompleteField):
    def __init__(self, search_controller, label=""):
        super(w.AutoCompleteField, self).__init__(
            label=label,
            search_controller=search_controller,
            search_param="name",
            result_name="results",
            only_suggest=True,
            validator=AutoCompleteValidator(),
            attrs=dict(size=20))

# Fix TG CalendarDatePicker, which returns a datetime, not a date
class BRCalendarDatePicker(w.CalendarDatePicker):
    def __init__(self, **kw):
        super(BRCalendarDatePicker, self).__init__(**kw)
        self.validator = v.DateConverter(format=self.format,
            not_empty=self.not_empty)    
