import numpy as np

################################################################################
#                          HTML output tools                                   #
################################################################################
def model_summary(model, solution, html):
    reaction2flux_dict = dict([(model.reactions[i], solution.fluxes[i])
                               for i in range(len(model.reactions))])

    display_exchange_reactions(model, reaction2flux_dict, html)
    
    for m in model.metabolites:
        display_metabolite_reactions(model, m, reaction2flux_dict, html)
    
def display_exchange_reactions(model, reaction2flux_dict, html):
    # metabolite
    html.write('<br />\n')
    html.write('<a name="EXCHANGE"></a>\n')
    html.write('Exchange reactions: <br />\n')
    html.write('<br />\n')
    
    titles = ['Sub System', 'Reaction Name', 'Reaction ID',
              'Reaction', 'LB', 'UB', 'Reaction Flux']

    # fluxes
    rowdicts = []
    for r in model.reactions:
        if r.subsystem not in ['', 'Exchange']:
            continue
        if abs(reaction2flux_dict[r]) < 1e-10:
            continue

        direction = np.sign(reaction2flux_dict[r])
        d = {'Sub System': 'Exchange', 'Reaction Name': r.name,
             'Reaction ID': r.id,
             'Reaction': display_reaction(r, None, direction),
             'LB': '%g' % r.lower_bound,
             'UB': '%g' % r.upper_bound,
             'Reaction Flux': '%.2g' % abs(reaction2flux_dict[r]),
             'sortkey': reaction2flux_dict[r]}

        rowdicts.append(d)
        
    # add a zero row (separating forward and backward) and sort the 
    # rows according to the net flux
    rowdicts.append({'sortkey': 0})
    rowdicts.sort(key=lambda x: x['sortkey'])

    # add color to the rows
    max_flux = max([abs(d['sortkey']) for d in rowdicts])
    rowcolors = [color_gradient(d['sortkey']/max_flux) for d in rowdicts]

    html.write_table(rowdicts, titles, rowcolors=rowcolors)

def display_metabolite_reactions(model, m, reaction2flux_dict, html):

    # metabolite
    html.write('<br />\n')
    html.write('<a name="%s"></a>\n' % m.id)
    html.write('Metabolite name: ' + m.name + '<br />\n')
    html.write('Metabolite ID: ' + m.id + '<br />\n')
    html.write('Compartment: ' + m.compartment + '<br />\n')
    html.write('<br />\n')

    titles = ['Sub System', 'Reaction Name', 'Reaction ID',
              'Reaction', 'LB', 'UB', 'Reaction Flux', 'Net Flux']
    
    # fluxes
    rowdicts = []
    for r in m.reactions:
        if abs(reaction2flux_dict[r]) < 1e-10:
            continue
            
        direction = np.sign(reaction2flux_dict[r])
        net_flux = reaction2flux_dict[r] * r.get_coefficient(m)
        d = {'Sub System': r.subsystem, 'Reaction Name': r.name,
             'Reaction ID': r.id,
             'Reaction': display_reaction(r, m, direction),
             'LB': '%g' % r.lower_bound,
             'UB': '%g' % r.upper_bound,
             'Reaction Flux': '%.2g' % abs(reaction2flux_dict[r]),
             'Net Flux': '%.2g' % net_flux,
             'sortkey': -net_flux}

        rowdicts.append(d)
    
    if rowdicts == []:
        return

    # add a zero row (separating forward and backward) and sort the 
    # rows according to the net flux
    rowdicts.append({'sortkey': 0})
    rowdicts.sort(key=lambda x: x['sortkey'])

    # add color to the rows
    max_flux = max([abs(d['sortkey']) for d in rowdicts])
    rowcolors = [color_gradient(d['sortkey']/max_flux) for d in rowdicts]

    html.write_table(rowdicts, titles, rowcolors=rowcolors)

def display_reaction(r, m_bold=None, direction=1):
    """
        Returns a string representation of a reaction and highlights the
        metabolite 'm' using HTML tags.
    """
    s_left = []
    s_right = []
    for m in r.reactants + r.products:
        if m == m_bold:
            s_met = "<a href='#%s'><b>%s</b></a>" % (m.id, m.id)
        else:
            s_met = "<a href='#%s'>%s</a>" % (m.id, m.id)
        
        coeff = r.get_coefficient(m)
        if abs(coeff) == 1:
            s_coeff = ""
        else:
            s_coeff = "%g " % abs(coeff)
        
        if coeff < 0:
            s_left += [s_coeff + s_met]
        else:
            s_right += [s_coeff + s_met]
    
    if direction == 1:
        return ' + '.join(s_left) + ' &#8651; ' + ' + '.join(s_right)
    else:
        return ' + '.join(s_right) + ' &#8651; ' + ' + '.join(s_left)

def color_gradient(x):
    """
        Returns a color in Hex-RGB format between white and red if x is positive
        or between white and green if x is negative
    """
    grad = int(220 - abs(x)*80)
    if x > 0:
        return '%.2x%.2x%.2x' % (255, grad, grad)
    elif x < 0:
        return '%.2x%.2x%.2x' % (grad, 255, grad)
    else:
        return '%.2x%.2x%.2x' % (100, 100, 100)
