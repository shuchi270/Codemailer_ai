from jinja2 import Environment, FileSystemLoader
import markdown

def generate_report(analysis):

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report.html")

    html_analysis = markdown.markdown(
        analysis, 
        extensions=['fenced_code', 'codehilite'],
        extension_configs={
            'codehilite': {
                'noclasses': True,
                'pygments_style': 'default'
            }
        }
    )
    
    # Make the default #f8f8f8 grey background into pure white as requested
    html_analysis = html_analysis.replace('background: #f8f8f8', 'background: #ffffff')

    html = template.render(analysis=html_analysis)

    with open("report.html","w") as f:
        f.write(html)
    return html