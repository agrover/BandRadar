import cherrypy

import turbogears
from turbogears import controllers, expose
from turbogears import identity
from turbogears import widgets as w
from turbogears import validators as v

from model import UserAcct, Event, Artist, Attendance, Venue, hub
from widgets import artist_list
from sqlobject import SQLObjectNotFound, LIKE, func
from datetime import date
import formencode
import util
import saved_visit

#
# VALIDATORS
#

class UniqueUsername(formencode.FancyValidator):
    def validate_python(self, value, state):
        try:
            user = UserAcct.byNameI(value)
            raise formencode.Invalid('Sorry, that username exists', value, state)
        except SQLObjectNotFound:
            pass

class UniqueEmail(formencode.FancyValidator):
    def validate_python(self, value, state):
        rows = UserAcct.select(func.LOWER(UserAcct.q.email_address) == value.lower()).count()
        if rows:
            raise formencode.Invalid('Sorry, that email exists', value, state)

class PassMatches(formencode.FancyValidator):
    def validate_python(self, field_dict, state):
        if not field_dict['old_pass']:
            return
        try:
            u = UserAcct.by_user_name(field_dict['user_name'])
            enc_pass = identity.current_provider.encrypt_password(field_dict['old_pass'])
            if enc_pass != u.password:
                raise formencode.Invalid("", field_dict, state,
                    error_dict = {'old_pass':"Old password doesn't match"})
        except SQLObjectNotFound:
            raise formencode.Invalid("", field_dict, state,
                error_dict = {'old_pass':'User not found'})

#
# FORMS
#

class NewUserForm(w.WidgetsList):
#    forward_url = w.HiddenField()
    user_name = w.TextField(label="Login", help_text="letters, numbers, '_' or '-'",
        attrs=dict(size=16, maxlength=16),
        validator=v.All(UniqueUsername, v.PlainText(strip=True), v.NotEmpty))
    email = w.TextField(label="Email", help_text="to notify you of your tracked events/bands/venues",
        validator=v.All(UniqueEmail, v.NotEmpty, v.Email(strip=True)))
    zip_code = w.TextField(label="Zip Code", help_text="track bands in your area",
        attrs=dict(size=10, maxlength=10),
        validator=v.PostalCode(strip=True))
    pass1 = w.PasswordField(label="Password", help_text="Length 6-40 chars",
        attrs=dict(maxlength=40),
        validator=v.All(v.MinLength(6), v.NotEmpty))
    pass2 = w.PasswordField(label="Password again",
        attrs=dict(maxlength=40),
        validator=v.NotEmpty)

class NewUserSchema(v.Schema):
    chained_validators = [v.FieldsMatch("pass1", "pass2")]

newuser_form = w.TableForm(fields=NewUserForm(), name="newuser",
                 submit_text="Create", validator=NewUserSchema())

class UserForm(w.WidgetsList):
    user_name = w.HiddenField()
    email_address = w.TextField(label="Email", validator=v.Email(strip=True))
    zip_code = w.TextField(label="Zip Code",
        attrs=dict(size=10, maxlength=10),
        validator=v.PostalCode(strip=True))
    url = w.TextField(label="Website", attrs=dict(size=50),
        validator=v.URL)
    myspace = w.TextField(label="MySpace", attrs=dict(maxlength=40),
        help_text="either myspace.com/abc or abc")
    description = w.TextArea(label="About Me", rows=3, cols=60)
    event_email = w.CheckBox(label="Upcoming Events Email",
        help_text="email about upcoming events for tracked artists", default=False)
    other_email = w.CheckBox(label="Suggested Events Email",
        help_text="event emails for other artists, based on your current choices",
        default=False)
    old_pass = w.PasswordField(label="Old Password",
        help_text="only needed if changing password")
    pass1 = w.PasswordField(label="New Password", validator=v.Any(v.MinLength(6), v.Empty))
    pass2 = w.PasswordField(label="New Password again")

class UserSchema(v.Schema):
    chained_validators = [v.FieldsMatch("pass1", "pass2"), PassMatches]

user_form = w.TableForm(fields=UserForm(), name="user", submit_text="Save",
                        validator=UserSchema())

class LostPasswdForm(w.WidgetsList):
    email = w.TextField(label="Email",
        validator=v.All(v.NotEmpty, v.Email(strip=True)))

lost_passwd_form = w.TableForm(fields=LostPasswdForm(), submit_text="Send")

#
# CONTROLLER
#

class UserController(controllers.Controller, util.RestAdapter):

    @expose(template=".templates.user.login")
    def login(self, *args, **kw):

        if not identity.current.anonymous and identity.was_login_attempted():
            util.redirect(kw['forward_url'])

        forward_url = None
        previous_url = cherrypy.request.path

        if identity.was_login_attempted():
            msg = _("Login incorrect.")
        elif identity.get_identity_errors():
            msg = _("Login error.")
        else:
            msg = _("Please log in.")
            forward_url = cherrypy.request.headers.get("Referer", "/")
        cherrypy.response.status = 403
        form_vals = dict(forward_url=forward_url)
        return dict(message=msg, previous_url=previous_url, logging_in=True,
                    original_parameters=cherrypy.request.params,
                    forward_url=forward_url,
                    newuser_form=newuser_form, form_vals=form_vals)

    @expose()
    @turbogears.validate(form=newuser_form)
    @turbogears.error_handler(login)
    def usercreate(self, user_name, email, zip_code, pass1, pass2,
             forward_url=None, previous_url=None):
        u = UserAcct(user_name=user_name, email_address=email,
            password=pass1)
        turbogears.flash("Account created!")
        identity.current_provider.validate_identity(user_name, pass1,
            identity.current.visit_key)
        util.redirect_previous()

    @expose()
    def logout(self):
        saved_visit.forget()
        identity.current.logout()
        turbogears.flash("Logged out")
        util.redirect("/")

    @expose(template=".templates.user.list")
    @identity.require(identity.in_group("admin"))
    def list(self):
        u = UserAcct.select(orderBy=UserAcct.q.created).reversed()
        return dict(users=u)

    @expose(template=".templates.user.show")
    def show(self, user_name):
        try:
            u = UserAcct.by_user_name(user_name)
            artists = u.artists.orderBy(Artist.q.name)
            venues = u.venues.orderBy(Venue.q.name)
            attendances = Attendance.selectBy(user=u)

            viewing_self = False
            if identity.current.user and identity.current.user.user_name == user_name:
                viewing_self = True
        except SQLObjectNotFound:
            turbogears.flash("User not found")
            util.redirect("/")

        return dict(user=u, artists=artists, venues=venues,
            attendances=attendances, viewing_self=viewing_self,
            description=util.desc_format(u.description))

    @expose(template=".templates.user.showtracked")
    def showtracked(self, user_name):
        try:
            u = UserAcct.by_user_name(user_name)
            artists = u.artists.orderBy(Artist.q.name)

            viewing_self = False
            if identity.current.user and identity.current.user.user_name == user_name:
                viewing_self = True
        except SQLObjectNotFound:
            turbogears.flash("User not found")
            util.redirect("/")

        return dict(user=u, artists=artists, viewing_self=viewing_self,
            artist_list=artist_list)

    @expose(template=".templates.user.edit")
    @identity.require(identity.not_anonymous())
    def edit(self, user_name):
        if not (identity.current.user.user_name == user_name
                or "admin" in identity.current.groups):
            raise identity.IdentityFailure("Not authorized")
        try:
            u = UserAcct.by_user_name(user_name)
        except SQLObjectNotFound:
            turbogears.flash("Invalid username")
            util.redirect("/")
        return dict(user_name=user_name, user_form=user_form,
            form_vals=u)

    @expose()
    @turbogears.validate(form=user_form)
    @turbogears.error_handler(edit)
    @identity.require(identity.not_anonymous())
    def save(self, user_name, old_pass, pass1, **kw):
        if not (identity.current.user.user_name == user_name
                or "admin" in identity.current.groups):
            raise identity.IdentityFailure("Not authorized")

        try:
            u = UserAcct.by_user_name(user_name)
            u.set(**u.clean_dict(kw))
            # old pw checked by validator, if present
            if (old_pass or "admin" in identity.current.groups) and pass1:
                # model does hash, not us
                u.password = pass1
            turbogears.flash("Saved")
        except SQLObjectNotFound:
            turbogears.flash("Error saving changes")
        util.redirect("/users/%s" % u.user_name)

    @expose(template=".templates.user.lost_passwd")
    def lost_passwd(self):
        return dict(lost_passwd_form=lost_passwd_form);

    @expose()
    @turbogears.validate(form=lost_passwd_form)
    @turbogears.error_handler(lost_passwd)    
    def lost_passwd_send(self, email):
        try:
            u = UserAcct.by_email_address(email)
            import smtplib
            import pkg_resources
            from email.MIMEText import MIMEText

            msg_to = u.email_address
            msg_from = "BandRadar Help <help@bandradar.com>"
            body = pkg_resources.resource_string(__name__, 
                        'templates/user/lost_passwd_email.txt')
            body  = body % {'password': u.password,
                'user_name': u.user_name}
            msg = MIMEText(body)
            msg['Subject'] = "bandradar.com password reminder"
            msg['From'] = msg_from
            msg['To'] = msg_to

            s = smtplib.SMTP()
            s.connect()
            s.sendmail(msg_from, [msg_to], msg.as_string())
            s.close()

            turbogears.flash("Email sent to %s." % email)
        except SQLObjectNotFound:
            turbogears.flash("Email unknown - no email sent.")
        util.redirect("/")

    #delete. display confirmation
