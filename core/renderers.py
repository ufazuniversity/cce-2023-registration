from django.forms import renderers


class BootstrapFormRenderer(renderers.TemplatesSetting):
    form_template_name = "snippets/bootstrap_form_snippet.html"
