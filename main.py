from cobra.io.sbml import create_cobra_model_from_sbml_file
from html_writer import HtmlWriter
import analysis_toolbox

main_html = HtmlWriter('res/fba.html')
main_html.write('<title>FBA</title>')
main_html.write('<h1>FBA</h1>\n')

model = create_cobra_model_from_sbml_file('data/iJO1366.xml')

main_html.write('</ul>\n')

print("Running standard FBA...")
solution = model.optimize()

if solution.status is not None:
    # write the flux summary for the knockout model as HTML
    analysis_toolbox.model_summary(model, solution, main_html)

main_html.close()
