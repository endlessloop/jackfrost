__author__ = 'Usuario'

from lookups import registered_lookups
from core import AutocompleteError
from django.forms.widgets import TextInput, SelectMultiple, Input
from django.utils.safestring import mark_safe
from django.forms import Media
from django.utils.encoding import force_unicode
from django.forms.util import flatatt
from django.forms.widgets import Widget
from django.utils import simplejson
import uuid


class AutocompleteWidgetError(AutocompleteError):
    pass


class AutocompleteWidget(Widget):

    class Media:
        css = {}
        js = ('js/JSON.js', 'js/jackfrost.js')

    def __init__(self, lookup_name, attrs=None):
        super(AutocompleteWidget, self).__init__(attrs)
        self._lookup_name = lookup_name

    def _must_have_id(self, attrs=None):
        uniqid = uuid.uuid4()
        if isinstance(attrs, dict):
            if not attrs.has_key('id'):
                attrs['id'] = u'jqbasewidget_id_' + uniqid
            return attrs
        else:
            return dict(id=u'jqbasewidget_id_' + uniqid)

    def _get_lookup(self):
        try:
            global registered_lookups
            return registered_lookups[self._lookup_name]
        except Exception as e:
            raise AutocompleteWidgetError("Unregistered '%s' autocomplete lookup" % self._lookup_name)


class AutocompleteTextInput(AutocompleteWidget, TextInput):
    """
    Simple text-box with jquery AC enabled features.
    """

    def __init__(self, lookup_name, attrs=None):
        TextInput.__init__(self, attrs)
        AutocompleteWidget.__init__(self, lookup_name, attrs)

    def render(self, name, value, attrs=None):
        attrs = self._must_have_id(attrs)
        return TextInput.render(self, name, value, attrs) + self.render_jquery_autocomplete(attrs)

    def render_jquery_autocomplete(self, attrs):
        url = self._get_lookup().reverse_autocomplete_url()
        id = attrs['id']
        autocomplete_textinput_template = u"""
        <script>
          (function($){
            $(function(){
              jackfrost_input($, %s, %s);
            });
          })(jQuery);
        </script>
        """
        texto = autocomplete_textinput_template % (id, url)
        return mark_safe(texto)


class AutocompleteSelect(AutocompleteWidget, Input):
    """
    Simple model choice field whose value comes from a source and validates against it.
    """

    def __init__(self, lookup_name, attrs=None):
        Input.__init__(self, attrs)
        AutocompleteWidget.__init__(self, lookup_name, attrs)

    def render(self, name, value, attrs=None):
        attrs = self._must_have_id(attrs)
        attrs.pop('name', 1)
        return self.render_controls(name, attrs) +\
               self.render_jquery_autocomplete(value, attrs)

    def render_controls(self, name, attrs=None):
        final_attrs = self.build_attrs(attrs)
        #esto para darle id al cuadro de texto y al hidden
        #el nombre no lo usamos ya que no queremos el textbox como elemento
        #del formulario a enviar.
        control_id = final_attrs['id']
        final_attrs['id'] += '-text'
        final_attrs['type'] = 'text'
        textbox = mark_safe(u'<input %s />' % flatatt(final_attrs))
        hidden  = mark_safe(u'<input id="%s" type="hidden" name="%s" />' % (control_id, name))
        return textbox + hidden

    def render_jquery_autocomplete(self, value, attrs):
        url_ac = self._get_lookup().reverse_autocomplete_url()
        url_init = self._get_lookup().reverse_fk_initial_url()
        id = attrs['id']
        before_set = attrs['before_set'] or 'undefined'
        after_set = attrs['after_set'] or 'undefined'
        before_del = attrs['before_del'] or 'undefined'
        after_del = attrs['after_del'] or 'undefined'
        custom_renderer = attrs['renderer'] or 'undefined'
        autocomplete_fk_template = u"""
        <script>
          (function($){
            $(function(){
              JQACSelect($, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            });
          })(jQuery);
        </script>
        """
        return mark_safe(autocomplete_fk_template % (
            simplejson.dumps(id),
            simplejson.dumps(url_ac),
            simplejson.dumps(url_init),
            simplejson.dumps(value),
            before_set,
            after_set,
            before_del,
            after_del,
            custom_renderer
        ))


class AutocompleteSelectMultiple(AutocompleteWidget, Input):
    """
    Multiple model choice field with a select multiple and a text enabled with jquery AC capabilities.
    Validates the list of values against a source.
    """

    def __init__(self, lookup_name, attrs=None):
        Input.__init__(self, attrs)
        AutocompleteWidget.__init__(self, lookup_name, attrs)

    def render(self, name, value, attrs=None):
        attrs = self._must_have_id(attrs)
        attrs.pop('name', 1)
        return self.render_controls(name, attrs) +\
               self.render_jquery_autocomplete(value, attrs)

    def render_controls(self, name, attrs=None):
        final_attrs = self.build_attrs(attrs)
        #esto para darle id al cuadro de texto y al hidden
        #el nombre no lo usamos ya que no queremos el textbox como elemento
        #del formulario a enviar.
        control_id = final_attrs['id']
        final_attrs['id'] += '-text'
        final_attrs['type'] = 'text'
        textbox = mark_safe(u'<input %s />' % flatatt(final_attrs))
        hidden  = mark_safe(u'<input id="%s" type="hidden" name="%s" />' % (control_id, name))
        lista   = mark_safe(u'<select id="%s" multiple="multiple" />' % (control_id + '-list',))
        return textbox + hidden + lista

    def render_jquery_autocomplete(self, values, attrs):
        url_ac = self._get_lookup().reverse_autocomplete_url()
        url_init = self._get_lookup().reverse_m2m_initial_url()
        id = attrs['id']
        before_add = attrs['before_add'] or 'undefined'
        after_add = attrs['after_add'] or 'undefined'
        before_rem = attrs['before_del'] or 'undefined'
        after_rem = attrs['after_del'] or 'undefined'
        custom_renderer = attrs['renderer'] or 'undefined'
        autocomplete_m2m_template = u"""
        <script>
          (function($)
          {
            $(function(){
              JQACSelectMultiple($, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            });
          })
          (jQuery);
        </script>
        """
        return mark_safe(autocomplete_m2m_template % (
            simplejson.dumps(id),
            simplejson.dumps(url_ac),
            simplejson.dumps(url_init),
            simplejson.dumps(values),
            before_add,
            after_add,
            before_rem,
            after_rem,
            custom_renderer
        ))