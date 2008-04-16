from turbogears import widgets as w
from turbogears import validators as v
from xml.etree import ElementTree as et
from bandradar.imports import google
from bandradar.model import hub

w.register_static_directory("br", "bandradar/widgets")

class ExtJSLink(w.JSLink):
    def update_params(self, d):
        super(ExtJSLink, self).update_params(d)
        d["link"] = self.name

class GoogleMapWidget(w.Widget):
    template = """
    <div xmlns:py="http://purl.org/kid/ns#" py:if="venue.geocode_lat" id="map" style="width: ${width}px; height: ${height}px">
        <script type="text/javascript">
            var map_lat = ${venue.geocode_lat}
            var map_lon = ${venue.geocode_lon}
            addLoadEvent(gmap_load)
            window.onunload = GUnload()
        </script>
    </div>"""
    javascript = [w.mochikit]
    params = ["venue", "key", "width", "height"]

    def __init__(self, width=500, height=350, **kw):
        key = kw.pop("key", "abcdef")
        js1 = ExtJSLink(None, "http://maps.google.com/maps?file=api&v=2&key=%s" % key)
        js2 = w.JSLink("br", 'javascript/googlemap.js')
        self.javascript.append(js1)
        self.javascript.append(js2)
        self.width = width
        self.height = height

googlemap = GoogleMapWidget(key=google.key, width=350, height=300)

class ButtonWidget(w.Widget):
    template = "bandradar.widgets.templates.button"
    params = ['label', 'action']

class ArtistListWidget(w.Widget):
    params = ['artists', 'emph_new']

    emph_new = False

    def display(self, artists, emph_new=False):
        artists = artists.orderBy('name')
        top = et.Element("span")
        top.attrib['class'] ="artistlist"
        if not artists.count():
            top.text = "None"
        else:
            for app_artist in [a for a in artists if a.approved]:
                sub = et.SubElement(top, "a")
                sub.attrib['href'] = "/artists/%s" % app_artist.id
                sub.text = app_artist.name
                sub.tail = ", "
            for unapp_artist in [a for a in artists if not a.approved]:
                if emph_new:
                    sub = et.SubElement(top, "strong")
                else:
                    sub = et.SubElement(top, "span")            
                sub.text = unapp_artist.name
                sub.tail = ", "
            sub.tail = None

        return top

artist_list = ArtistListWidget()

class TrackButtonWidget(w.Widget):
    template = "bandradar.widgets.templates.trackbutton"
    javascript = [w.mochikit, w.JSLink("br", 'javascript/trackbutton.js')]
    params = ["id", "action", "tracked", "text"]
    text = dict(off="Track", on="Untrack")
    
    def track_str(self, tracked):
        if tracked:
            return "tracked"
        return ""

track_button = TrackButtonWidget()

class TextFieldWithDisappearingDefault(w.TextField):
    template = """
    <input xmlns:py="http://purl.org/kid/ns#"
        type="text"
        name="${name}"
        class="${field_class}"
        id="${field_id}"
        value="    Search Band or Venue"
        py:attrs="attrs"
        onclick="this.value=''"
    />
    """


class AutoCompleteValidator(v.Schema):
    def _to_python(self, value, state):
        text = value['text']
        value['text'] = v.NotEmpty(strip=True).to_python(text)
        return value

# BR's base AC widget, with a bunch of params set
class BRAutoCompleteField(w.AutoCompleteField):
    def __init__(self, search_controller, label="", **kw):
        super(BRAutoCompleteField, self).__init__(
            label=label,
            search_controller=search_controller,
            search_param="name",
            result_name="results",
            only_suggest=True,
            validator=AutoCompleteValidator(),
            attrs=dict(size=20), **kw)

# Global search uses custom TextField subwidget
class BRGlobalSearch(BRAutoCompleteField):
    def __init__(self, *args, **kw):
        super(BRGlobalSearch, self).__init__(*args, **kw)
        self.text_field = TextFieldWithDisappearingDefault(name='text', attrs=dict(size=20))

class GlobalSearchBox(w.WidgetsList):
    search = BRGlobalSearch("/dynmultisearch")

global_search_form = w.ListForm(fields=GlobalSearchBox(),
    name="gsearch", submit_text="Go")

# Fix TG CalendarDatePicker, which returns a datetime, not a date
class BRCalendarDatePicker(w.CalendarDatePicker):
    def __init__(self, **kw):
        super(BRCalendarDatePicker, self).__init__(**kw)
        self.validator = v.DateConverter(format=self.format,
            not_empty=self.not_empty)


class TopArtistsWidget(w.Widget):
    template = "bandradar.widgets.templates.topartists"

    def get_list(self):
        conn = hub.getConnection()
        top_artists = conn.queryAll("""
            select a.name, a.id, COUNT(aua.user_acct_id) as count
            from artist a, artist_user_acct aua
            where a.id = aua.artist_id
            group by a.name, a.id
            order by count desc, name
            limit 10
            """)
        return [dict(name=a.decode('utf8'), id=b, count=c) for a, b, c in top_artists]
    
top_artists = TopArtistsWidget()

class TopVenuesWidget(w.Widget):
    template = "bandradar.widgets.templates.topvenues"

    def get_list(self):
        conn = hub.getConnection()
        top_venues = conn.queryAll("""
            select v.name, v.id, COUNT(uav.user_acct_id) as count
            from venue v, user_acct_venue uav
            where v.id = uav.venue_id
            group by v.name, v.id
            order by count desc, name
            limit 10
            """)
        return [dict(name=a.decode('utf8'), id=b, count=c) for a, b, c in top_venues]
    
top_venues = TopVenuesWidget()

