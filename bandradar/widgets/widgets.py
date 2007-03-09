from turbogears import widgets as w
from turbogears import validators as v
from turbogears import config
from cgi import escape

w.register_static_directory("br", "bandradar/widgets")

class ExtJSLink(w.JSLink):
    def update_params(self, d):
        super(ExtJSLink, self).update_params(d)
        d["link"] = self.name

class GoogleMapWidget(w.Widget):
    template = """
        <div id="map" style="width: ${width}px; height: ${height}px">
    </div>"""
    javascript = [w.mochikit]
    params = ["key", "width", "height"]

    def __init__(self, width=500, height=350, **kw):
        key = kw.pop("key", "abcdef")
        js1 = ExtJSLink(None, "http://maps.google.com/maps?file=api&v=2&key=%s" % key)
        js2 = w.JSLink("br", 'javascript/googlemap.js')
        self.javascript.append(js1)
        self.javascript.append(js2)
        self.width = width
        self.height = height

localhost_key = "ABQIAAAAl6v2YpcT3a-0chb1euUaRRR4EqRj3RNZnoYuzojShxUjcPQKRRSqdkDEb-kjqUA2B3UAs66NGlvjOA" 
real_key = "ABQIAAAAl6v2YpcT3a-0chb1euUaRRRIOcczJVkwMVJxSoSbKoEvbYERDxTrKIpffL5C_3zzzlk1QmARAtbL2A"

if config.get("server.environment", "development") == "development":
    key = localhost_key
else:
    key = real_key

googlemap = GoogleMapWidget(key=key, width=350, height=300)

class ButtonWidget(w.Widget):
    template = "bandradar.widgets.templates.button"
    params = ['label', 'action']

class ArtistListWidget(w.Widget):
    template = "bandradar.widgets.templates.artistlist"
    params = ['artists']

    def get_list(self, artists):
        if not artists:
            artisthtml = "<strong>None</strong>"
        else:
            htmlstr = "<a href=\"/artists/%s\">%s</a>"
            artist_html_list = []
            artist_html_list.extend([ htmlstr % (a.id, escape(a.name)) for a in artists if a.approved])
            artist_html_list.extend([escape(a.name) for a in artists if not a.approved])
            artisthtml = ", ".join(artist_html_list)
        return artisthtml

artist_list = ArtistListWidget()

class TrackButtonWidget(w.Widget):
    template = "bandradar.widgets.templates.trackbutton"
    javascript = [w.mochikit, w.JSLink("br", 'javascript/trackbutton.js')]
    params = ["id", "action", "tracked"]

    def track_str(self, tracked):
        if tracked:
            return "tracked"
        return ""

track_button = TrackButtonWidget()

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

