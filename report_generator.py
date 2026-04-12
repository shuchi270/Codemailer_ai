from jinja2 import Environment, FileSystemLoader

def generate_report(analysis):

    env = Environment(loader=FileSystemLoader("templates"))

    template = env.get_template("report.html")

    html = template.render(analysis=analysis)

    with open("report.html","w") as f:
        f.write(html)