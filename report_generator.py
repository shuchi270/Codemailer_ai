from jinja2 import Environment, FileSystemLoader
import markdown

def generate_report(analysis):

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report.html")

    html_analysis = markdown.markdown(analysis, extensions=['fenced_code', 'codehilite'])
    html = template.render(analysis=html_analysis)

    with open("report.html","w") as f:
        f.write(html)
    return html