import cherrypy

import turbogears
from turbogears import controllers, expose, redirect
from turbogears import identity
from turbogears import widgets as w
from turbogears import validators as v

from model import UserAcct, Event, Artist, hub
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
        rows = UserAcct.select(UserAcct.q.user_name == value).count()
        if rows:
            raise formencode.Invalid('Sorry, that username exists', value, state)

class UniqueEmail(formencode.FancyValidator):
    def validate_python(self, value, state):
        rows = UserAcct.select(UserAcct.q.email_address == value).count()
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
    email = w.TextField(label="Email",
        validator=v.All(UniqueEmail, v.NotEmpty, v.Email(strip=True)))
    zip = w.TextField(label="Zip Code",
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
    url = w.TextField(label="Website", attrs=dict(size=60),
        validator=v.Any(v.URL, v.Empty))
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

class Users(controllers.Controller, util.RestAdapter, identity.SecureResource):

    @expose(template=".templates.user.login")
    def login(self, *args, **kw):

        if not identity.current.anonymous and identity.was_login_attempted():
            redirect(kw['forward_url'])

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
    def usercreate(self, user_name, email, zip, pass1, pass2,
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
        redirect("/")

    @expose(template=".templates.user.list")
    def list(self):
        u = None
        if 'admin' in identity.current.groups:
            u = UserAcct.select(orderBy=UserAcct.q.user_name)
        return dict(users=u)

    @expose(template=".templates.user.show")
    def show(self, user_name):
        try:
            u = UserAcct.by_user_name(user_name)
            art_list = []
            for a in u.artists:
                old = 0
                new = 0
                for e in a.events:
                    if e.date < date.today():
                        old += 1
                    else:
                        new += 1
                art_list.append((a.name, a.id, old, new))
            if identity.current.user and identity.current.user.user_name == user_name:
                viewing_self = True
            else:
                viewing_self = False
        except SQLObjectNotFound:
            turbogears.flash("User not found")
            redirect(turbogears.url("/"))

        art_list.sort()

        return dict(user=u, art_list=art_list, viewing_self=viewing_self)

    @expose(template=".templates.user.edit")
    def edit(self, user_name, **kw):
        if not ((identity.current.user
                and identity.current.user.user_name == user_name)
                or "admin" in identity.current.groups):
            raise identity.IdentityFailure("Not authorized")
        form_vals = {}
        try:
            u = UserAcct.by_user_name(user_name)
            form_vals = dict(user_name=u.user_name,
                email_address=u.email_address, zip_code=u.zip_code, url=u.url,
                event_email=u.event_email, other_email=u.other_email)
        except SQLObjectNotFound:
            pass
        form_vals.update(kw)
        return dict(user_name=user_name, user_form=user_form,
            form_vals=form_vals)

    @expose()
    @turbogears.validate(form=user_form)
    @turbogears.error_handler(edit)
    def save(self, user_name, email_address, zip_code=None, url=None,
            description=None, event_email=False, other_email=False,
            old_pass=None, pass1=None, pass2=None):
        if not ((identity.current.user
                and identity.current.user.user_name == user_name)
                or "admin" in identity.current.groups):
            raise identity.IdentityFailure("Not authorized")

        try:
            u = UserAcct.by_user_name(user_name)
            u.email_address = email_address
            u.zip_code = zip_code
            u.url = url
            u.description = description
            u.event_email = event_email
            u.other_email = other_email
            # old pw checked by validator, if present
            if (old_pass or "admin" in identity.current.groups) and pass1:
                # model does hash, not us
                u.password = pass1
            turbogears.flash("Saved")
        except SQLObjectNotFound:
            turbogears.flash("Error saving changes")
        redirect(turbogears.url("/users/%s" % u.user_name))

    @expose(template=".templates.user.lost_passwd")
    def lost_passwd(self):
        return dict(lost_passwd_form=lost_passwd_form);

    @expose(template=".templates.output")
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

            return dict(output="Email sent to %s." % email)
        except SQLObjectNotFound:
            return dict(output="Email unknown - no email sent.")

    #delete. display confirmation
