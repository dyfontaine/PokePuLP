import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_table_experiments import DataTable
import plotly.graph_objs as go
 
import pandas as pd
from itertools import compress
import pulp as plp
import boto3
import io


##########################################
# prepare data
##########################################


s3 = boto3.client('s3')
obj = s3.get_object(Bucket='pokepulp-assets', Key='data/pokeSTATS.csv')
data_pokes = pd.read_csv(io.BytesIO(obj['Body'].read()))
data_pokes = data_pokes.set_index('Pokemon', drop=False)

initial_constraints = pd.DataFrame(columns=['LEFT HAND SIDE', 'SIGN', 'RIGHT HAND SIDE'],
                                   data=[['# OF POKEMON', '>=', '1'],
                                         ['# OF POKEMON', '<=', '6'],
                                         ['', '', ''], ['', '', ''],
                                         ['', '', ''], ['', '', '']
                                        ],
                                   index=['a','b','c','d','e','f'])

# add total stat
data_pokes['Total'] = data_pokes.HP + data_pokes.ATTACK + data_pokes.DEFENSE + data_pokes.SPEED + data_pokes.SPECIAL

# create list of unique pokemon, types, and statss
pokes = data_pokes.Pokemon
data_pokes['Type 1'] = data_pokes['Type 1'].str.upper()
data_pokes['Type 2'] = data_pokes['Type 2'].str.upper()
poke_types = pd.unique(data_pokes[['Type 1', 'Type 2']].values.ravel('K'))
poke_types = poke_types[~pd.isnull(poke_types)]
poke_stats = ['HP', 'ATTACK', 'DEFENSE', 'SPEED', 'SPECIAL']

# poke stats parameters
param_stats = {(p,s): data_pokes.get_value(p,s) for p in pokes for s in poke_stats}

# poke types parameters (1 hot encode the types)
type_1_dummies = pd.get_dummies(data_pokes['Type 1'])
type_2_dummies = pd.get_dummies(data_pokes['Type 2'])
for t in poke_types:
    if t not in list(type_1_dummies):
        type_1_dummies[t] = 0
    if t not in list(type_2_dummies):
        type_2_dummies[t] = 0 
type_1_dummies = type_1_dummies.sort_index(axis=1)
type_2_dummies = type_2_dummies.sort_index(axis=1)
type_dummies = pd.concat([type_1_dummies, type_2_dummies]).max(level=0)
param_types = {(p,t): type_dummies.get_value(p,t) for p in pokes for t in poke_types}
   
# decision variables
x_vars  = {p: plp.LpVariable(cat=plp.LpInteger, lowBound=0, upBound=1, name="x_{0}".format(p)) for p in pokes}

##########################################
# DASH app
##########################################

# constants
url_pokeball = 'https://s3.us-east-2.amazonaws.com/pokepulp-assets/pngs/pokeball.png'


app = dash.Dash(__name__, static_folder='assets')
server = app.server

app.layout = html.Div(id = 'full_page', children=[
    html.Table(children=[
        html.Tr(children=[html.Td(children=[html.H1(children='PokePuLP', className='page_Title')], colSpan='6')]),
    
        # objective section
        html.Tr(children=[
            html.Td(children=[
                html.Table(id='obj_table', children=[
                    html.Tr(children=[
                        html.Td(children=html.Div(children='Objective', className='section_Heading'), style={'width': '200px'}),
                        html.Td(colSpan='1', style={'width': '200px'}),
                        html.Td(colSpan='1', style={'width': '200px'}),
                        html.Td(colSpan='1', style={'width': '200px'})]),
                    html.Tr(children=[
                        html.Td(children=[
                            dcc.Dropdown(id='dd_obj_type', clearable=False, value='MAXIMIZE', style={'width': '180px'},
                                         options=[{'label': 'MAXIMIZE', 'value': 'MAXIMIZE'},{'label': 'MINIMIZE', 'value': 'MINIMIZE'}])], 
                            colSpan='1'),
                        html.Td(children=[html.Button('UPDATE OBJECTIVE', id='btn_update_objective')], 
                            colSpan='1'),
                        html.Td(id='obj_function_equals', children='Objective Function = ', colSpan='1'),
                        html.Td(children=[html.Div(id='div_objective', children='MAXIMIZE TOTAL HP')], colSpan='1')]),
                    html.Tr(children=[
                            html.Td(children=[dcc.Dropdown(id='dd_obj_func', clearable=False, value='TOTAL HP', style={'width': '180px'},
                                         options=[{'label': 'TOTAL HP', 'value': 'TOTAL HP'},
                                                  {'label': 'TOTAL ATTACK', 'value': 'TOTAL ATTACK'},
                                                  {'label': 'TOTAL DEFENSE', 'value': 'TOTAL DEFENSE'},
                                                  {'label': 'TOTAL SPEED', 'value': 'TOTAL SPEED'},
                                                  {'label': 'TOTAL SPECIAL', 'value': 'TOTAL SPECIAL'}])], colSpan='1'),
                            html.Td(children=[], colSpan='1'),
                            html.Td(id='obj_value_equals', children=['Objective Value = '], colSpan='1'),
                            html.Td(children=[html.Div(id='div_obj_value')], colSpan='1')])])],
                    colSpan='4', rowSpan='1', style={'width': '800px'}),
             html.Td(children=[
                     html.Table(id='tbl_pokes', children=[
                             html.Tr(children=[
                                     html.Td(children=html.Img(id='img_poke_1', src=url_pokeball, width=50, height=50)),
                                     html.Td(children=html.Img(id='img_poke_2', src=url_pokeball, width=50, height=50)),
                                     html.Td(children=html.Img(id='img_poke_3', src=url_pokeball, width=50, height=50)),
                                     html.Td(children=html.Img(id='img_poke_4', src=url_pokeball, width=50, height=50)),
                                     html.Td(children=html.Img(id='img_poke_5', src=url_pokeball, width=50, height=50)),
                                     html.Td(children=html.Img(id='img_poke_6', src=url_pokeball, width=50, height=50))
                                     ]),
                            html.Tr(children=[
                                    html.Td(id='txt_poke_1', className='name_text', children=''),
                                    html.Td(id='txt_poke_2', className='name_text', children=''),
                                    html.Td(id='txt_poke_3', className='name_text', children=''),
                                    html.Td(id='txt_poke_4', className='name_text', children=''),
                                    html.Td(id='txt_poke_5', className='name_text', children=''),
                                    html.Td(id='txt_poke_6', className='name_text', children='')
                                    ])
                             ])],
                    colSpan='2', rowSpan='1')]),
        html.Tr(children=['']),
    

        # constraints section
        html.Tr(children=[
            html.Td(children=[
                html.Table(id='const_table',
                    children=[
                    html.Tr(children=[
                        html.Td(children='Constraints', className='section_Heading'), 
                        html.Td(colSpan='3')]),
                    html.Tr(children=[
                        html.Td(children=[
                            dcc.Dropdown(id='dd_const_type', clearable=False, value='TEAM SIZE',
                                options=[{'label': 'TEAM SIZE', 'value': 'TEAM SIZE'},
                                         {'label': 'STATS', 'value': 'STATS'},
                                         {'label': 'POKE TYPES', 'value': 'POKE TYPES'}],
                                style={'width': '180px'})]),
                        html.Td(children=[
                            html.Div(children=[
                               DataTable(id='dt_constraints', sortable=False, editable=False, rows=[{}],
                                   row_selectable=True, columns=['LEFT HAND SIDE','SIGN','RIGHT HAND SIDE'])],
                               style={'width': '600px', 'display': 'inline-block'})],
                            rowSpan='6', colSpan='3')]),
                    html.Tr(children=[
                        html.Td(children=dcc.Dropdown(id='dd_const_lhs', clearable=False, value='# OF POKEMON', style={'width': '180px'},
                                  options=[{'label': '# OF POKEMON', 'value': '# OF POKEMON'}]))]),
                    html.Tr(children=[
                        html.Td(children=dcc.Dropdown(id = 'dd_const_sign', clearable=False, value='<=', style={'width': '180px'},
                     options=[{'label': '≤', 'value': '<='},{'label': '≥', 'value': '>='}]))]),
                    html.Tr(children=[
                        html.Td(children=dcc.Input(id='txtbox_const_rhs', placeholder='',type='number', value=0, max=9999, min=0, style={'width': '180px'}))]),
                    html.Tr(children=[
                        html.Td(html.Button('ADD CONSTRAINT', id='btn_add_constraint'))]),
                    html.Tr(children=
                        [html.Td(html.Button('REMOVE CONSTRAINT', id='btn_remove_constraint', style={'background-color': 'lightgray'}))])])],
                colSpan='4', rowSpan='7', style={'width': '800px'}),
    
            # stats graph
            html.Td(children= dcc.Graph(id='graph_team_stats',
                        figure={'data': [{'x': ['HP', 'Attack', 'Defense', 'Speed', 'Special'], 'y': [0, 0, 0, 0, 0], 'type': 'bar'}],
                               'layout': {'plot_bgcolor': 'white', 'paper_bgcolor': 'WhiteSmoke', 'font': {'color': 'black'},
                                          'margin': {'l': 25, 'b': 20, 't': 25, 'r': 5}, 'showlegend':False, 'title':'Team Stats',
                                          'yaxis': {'range': [0, 100]}}},
                        style={'width': 300, 'height':300},
                        config={'displayModeBar': False}),
                    colSpan='2', rowSpan='7')]),
        html.Tr(),
        html.Tr(),
        html.Tr(),
        html.Tr(),
        html.Tr(),
        html.Tr(),      
        html.Tr(children=[
            html.Td(colSpan='1'),
            html.Td(colSpan='3'),
            html.Td(colSpan='1'),
            html.Td(colSpan='1')]),
        html.Tr(children=[
            html.Td(children=[
                html.Table(id='controls_table', children=[
                    html.Tr(children=[
                        html.Td(children=html.Button('SOLVE!', id='btn_solve'), rowSpan='2', style={'width': '200px'}),
                        html.Td(id='problem_status', children='Problem Status:', style={'width': '200px'}),
                        html.Td(id='message', children='Message:', style={'width': '400px'}, colSpan='2')]),     
                    html.Tr(children=[
                        html.Td(children=[html.Div(id='div_obj_status', children='obj status........')]),
                        html.Td(children=[html.Div(id='div_message', children='Welcome to PokePuLP! Set up your optimization problem and then click SOLVE!')], colSpan='2')])], style={'height': '70px'})],
                colSpan='4', style={'width': '800px'}),
            html.Td(colSpan='3')])]),
    
        # STORAGE  ############  
        dcc.Store(id='opt_results'),
        dcc.Store(id='const_df')],
    style={'width': 1250})
    
    
# update objective function when user presses Update Objective
@app.callback(
    Output('div_objective', 'children'),
    [Input('btn_update_objective', 'n_clicks_timestamp')],
    [State('dd_obj_type', 'value'),
     State('dd_obj_func', 'value')])
def update_objective_function(btn_obj_ncts, obj_type, obj_stat):
    # split objective column into two words
    obj_string = obj_type + ' ' + obj_stat
    return(obj_string)
    
# update the constraint LHS options when the user
# changes the selected constraint type
@app.callback(
    Output('dd_const_lhs', 'options'),
    [Input('dd_const_type', 'value')])
def update_dd_const_lhs_choices(const_type):
    if const_type == 'TEAM SIZE':
        dd_const_lhs_options = [{'label': '# OF POKEMON', 'value': '# OF POKEMON'}]
    if const_type == 'STATS':
        dd_const_lhs_options = [{'label': 'TOTAL HP', 'value': 'TOTAL HP'},
                             {'label': 'TOTAL ATTACK', 'value': 'TOTAL ATTACK'},
                             {'label': 'TOTAL DEFENSE', 'value': 'TOTAL DEFENSE'},
                             {'label': 'TOTAL SPEED', 'value': 'TOTAL SPEED'},
                             {'label': 'TOTAL SPECIAL', 'value': 'TOTAL SPECIAL'}]
    if const_type == 'POKE TYPES':
        dd_const_lhs_options = [{'label': '# OF BUG TYPES', 'value': '# OF BUG TYPES'},
                             {'label': '# OF DRAGON TYPES', 'value': '# OF DRAGON TYPES'},
                             {'label': '# OF ELECTRIC TYPES', 'value': '# OF ELECTRIC TYPES'},
                             {'label': '# OF FIGHTING TYPES', 'value': '# OF FIGHTING TYPES'},
                             {'label': '# OF FIRE TYPES', 'value': '# OF FIRE TYPES'},
                             {'label': '# OF FLYING TYPES', 'value': '# OF FLYING TYPES'},
                             {'label': '# OF GHOST TYPES', 'value': '# OF GHOST TYPES'},
                             {'label': '# OF GRASS TYPES', 'value': '# OF GRASS TYPES'},
                             {'label': '# OF GROUND TYPES', 'value': '# OF GROUND TYPES'},
                             {'label': '# OF ICE TYPES', 'value': '# OF ICE TYPES'},
                             {'label': '# OF NORMAL TYPES', 'value': '# OF NORMAL TYPES'},
                             {'label': '# OF POISON TYPES', 'value': '# OF POISON TYPES'},
                             {'label': '# OF PSYCHIC TYPES', 'value': '# OF PSYCHIC TYPES'},
                             {'label': '# OF ROCK TYPES', 'value': '# OF ROCK TYPES'},
                             {'label': '# OF WATER TYPES', 'value': '# OF WATER TYPES'}]
    return(dd_const_lhs_options)

# change the selected constraint LHS value when the user
# changes the selected constraint type
@app.callback(
    Output('dd_const_lhs', 'value'),
    [Input('dd_const_type', 'value')])
def update_dd_const_lhs_value(const_type):
    if const_type == 'TEAM SIZE':
        dd_const_lhs_value = '# OF POKEMON'
    if const_type == 'STATS':
        dd_const_lhs_value = 'TOTAL HP'
    if const_type == 'POKE TYPES':
        dd_const_lhs_value = '# OF BUG TYPES'
    return(dd_const_lhs_value)

# add/remove a constraint when the respective button is clicked 
@app.callback(
    Output('const_df', 'data'),
    [Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp')],
    [State('const_df', 'data'), State('dd_const_lhs', 'value'),
     State('dd_const_sign', 'value'), State('txtbox_const_rhs', 'value'),
     State('dt_constraints', 'selected_row_indices')])
def add_constraint(btn_add_ncts, btn_rem_ncts, const_df, my_lhs, my_sign, my_rhs, selected_rows):
    const_df = pd.DataFrame.from_dict(const_df)
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    # check which button was clicked most recently (based on time stamp)
    if int(btn_add_ncts) > int(btn_rem_ncts): 
        if btn_add_ncts is not None and good_rhs(my_rhs):
            new_const_df = pd.DataFrame(columns=['LEFT HAND SIDE', 'SIGN', 'RIGHT HAND SIDE'], data=[[my_lhs, my_sign, my_rhs]], index=['g'])
            const_df = const_df.append(new_const_df, ignore_index=False)
            blank_row_indices = const_df[const_df.SIGN==''].index.values
            const_df = const_df.drop(sorted(blank_row_indices)[-1])
            const_df = sort_constraints(const_df)
        else:
            const_df = initial_constraints
    elif int(btn_rem_ncts) > int(btn_add_ncts):
        selected_rows = [s for s in selected_rows if s > 1]
        const_df = const_df.drop(const_df.index[selected_rows])
        new_const_df = pd.DataFrame(columns=['LEFT HAND SIDE', 'SIGN', 'RIGHT HAND SIDE'], data=[['', '', '']])
        for r in selected_rows:
            const_df = const_df.append(new_const_df, ignore_index=True)
        const_df = sort_constraints(const_df)
    else:
        const_df = initial_constraints
    output = const_df.to_dict()
    return output


# update the constraints shown in the datatable whenever
# the user changes them
@app.callback(
    Output('dt_constraints', 'rows'),
    [Input('const_df', 'data')])
def display_constraint_table(const_df):
    const_df = pd.DataFrame.from_dict(const_df)
    return const_df.to_dict('records')

# disable add constraint button when there are 6 constraints
@app.callback(
    Output('btn_add_constraint', 'disabled'),
    [Input('const_df', 'data')])
def disable_add_constraint(const_df):
    const_df = pd.DataFrame.from_dict(const_df)
    const_count = 6 - len(const_df[const_df['LEFT HAND SIDE'] == ''])
    if const_count == 6:
        off = True
    else:
        off = False
    return off

@app.callback(
    Output('btn_add_constraint', 'style'),
    [Input('const_df', 'data')])
def style_btn_add_constraint(const_df):
    const_df = pd.DataFrame.from_dict(const_df)
    const_count = 6 - len(const_df[const_df['LEFT HAND SIDE'] == ''])
    if const_count == 6:
        myStyle = {'background-color': 'lightgray'}
    else:
        myStyle = {'background-color': 'white'}
    return myStyle

# disable remove constraint button if none are selected
@app.callback(
    Output('btn_remove_constraint', 'style'),
    [Input('dt_constraints', 'selected_row_indices')])
def style_btn_remove_constraint(selected_rows):
    if len(selected_rows) == 0:
        myStyle = {'background-color': 'lightgray'}
    else:
        myStyle = {'background-color': 'white'}
    return myStyle

# disable remove constraint button whenever const_df changes
@app.callback(
    Output('dt_constraints', 'selected_row_indices'),
    [Input('const_df', 'data')])
def style_btn_remove_constraint2(myStyle):
    # (I already have a callback for btn_remove_constraint style so I must
    # use this callbback to update df_constraints selected_row_indices which in turn
    # calls the callback for btn_remove_constraint style)
    return []


# solve the optimization problem when the user clicks solve
@app.callback(
    Output('opt_results', 'data'),
    [Input('btn_solve', 'n_clicks')],
    [State('const_df', 'data'),
     State('div_objective', 'children')])
def solve_opt(n_clicks, const_df, obj_function):
    if n_clicks is not None:
        opt_model = plp.LpProblem(name="pokemon_picker")
        opt_model = add_decision_vars(opt_model)
        obj_list = parse_objective(obj_function)
        opt_model = add_objective(opt_model, obj_list[0], obj_list[1])
        const_df = pd.DataFrame.from_dict(const_df)
        opt_model = add_constraints(opt_model, const_df)
        opt_model.solve()
        opt_df = pd.DataFrame(list(x_vars.items()), columns=['Pokemon', 'VarName'])
        opt_df["solution_value"] = opt_df["VarName"].apply(lambda item: item.varValue)
        selected_pokes = opt_df.loc[opt_df.solution_value == 1,'Pokemon']
        obj_val = opt_model.objective.value()
        opt_status = plp.LpStatus[opt_model.status]
        if opt_status != 'Optimal':
            selected_pokes = []
        output = {'poke_list': selected_pokes, 'obj_value': obj_val, 'status': opt_status}
        return(output)
        
def parse_objective(obj_string):
    obj_string_list = obj_string.split()
    obj_type = obj_string_list[0]
    obj_stat = obj_string_list[1] + ' ' + obj_string_list[2]
    return([obj_type, obj_stat])
    
# add decision variables to the optimization model
def add_decision_vars(opt_model):
    for key, value in x_vars.items():
        opt_model += value
    return(opt_model)

# add objective to the optimization model,
# based on user's selections
def add_objective(opt_model, obj_type, obj_func):
    my_obj_stat = list(compress(poke_stats, [s in obj_func for s in poke_stats]))[0]
    my_obj = plp.lpSum(x_vars[p] * param_stats.get((p, my_obj_stat)) for p in pokes)
    if obj_type == 'MAXIMIZE':
        opt_model.sense = plp.LpMaximize
    else:
        opt_model.sense = plp.LpMinimize
    opt_model.setObjective(my_obj)
    return(opt_model)

# add constraints to the optimization model,
# based on user's selections  
def add_constraints(opt_model, const_df):
    const_count = 0
    for index, row in const_df.iterrows():
        const_count += 1
        if row['SIGN'] == '':
            continue
        elif row['SIGN'] == '<=': 
            const_sign = plp.LpConstraintLE
        else:
            const_sign = plp.LpConstraintGE
        if row['LEFT HAND SIDE'] == '# OF POKEMON':
            new_const = plp.LpConstraint(
                             e=plp.lpSum(x_vars[p] for p in pokes),
                             sense=const_sign,
                             rhs=int(row['RIGHT HAND SIDE']),
                             name="constraint_{0}".format(const_count))
        elif 'TOTAL' in row['LEFT HAND SIDE']:
            my_const_stat = list(compress(poke_stats, [s in row['LEFT HAND SIDE'] for s in poke_stats]))[0]
            new_const = plp.LpConstraint(
                             e=plp.lpSum(x_vars[p] * param_stats.get((p, my_const_stat)) for p in pokes),
                             sense=const_sign,
                             rhs=int(row['RIGHT HAND SIDE']),
                             name="constraint_{0}".format(const_count))
        elif 'TYPE' in row['LEFT HAND SIDE']:
            my_type = list(compress(poke_types, [t in row['LEFT HAND SIDE'] for t in poke_types]))[0]
            new_const = plp.LpConstraint(
                             e=plp.lpSum(x_vars[p] * param_types.get((p, my_type)) for p in pokes),
                             sense=const_sign,
                             rhs=int(row['RIGHT HAND SIDE']),
                             name="constraint_{0}".format(const_count))
        opt_model += new_const
    return(opt_model)

# update poke_1 GIF when optimization model is solved
@app.callback(
    Output('img_poke_1', 'src'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_poke_1(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_url = url_pokeball
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 1:
                my_poke = poke_list[0]
                my_url = 'https://s3.us-east-2.amazonaws.com/pokepulp-assets/gifs/' + my_poke + '_gif.gif'
    return my_url

# update poke_2 GIF when optimization model is solved
@app.callback(
    Output('img_poke_2', 'src'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_poke_2(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_url = url_pokeball
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 2:
                my_poke = poke_list[1]
                my_url = 'https://s3.us-east-2.amazonaws.com/pokepulp-assets/gifs/' + my_poke + '_gif.gif'
    return my_url

# update poke_3 GIF when optimization model is solved
@app.callback(
    Output('img_poke_3', 'src'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_poke_3(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_url = url_pokeball
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 3:
                my_poke = poke_list[2]
                my_url = 'https://s3.us-east-2.amazonaws.com/pokepulp-assets/gifs/' + my_poke + '_gif.gif'
    return my_url

# update poke_4 GIF when optimization model is solved
@app.callback(
    Output('img_poke_4', 'src'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_poke_4(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_url = url_pokeball
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 4:
                my_poke = poke_list[3]
                my_url = 'https://s3.us-east-2.amazonaws.com/pokepulp-assets/gifs/' + my_poke + '_gif.gif'
    return my_url

# update poke_5 GIF when optimization model is solved
@app.callback(
    Output('img_poke_5', 'src'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_poke_5(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_url = url_pokeball
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 5:
                my_poke = poke_list[4]
                my_url = 'https://s3.us-east-2.amazonaws.com/pokepulp-assets/gifs/' + my_poke + '_gif.gif'
    return my_url

# update poke_6 GIF when optimization model is solved
@app.callback(
    Output('img_poke_6', 'src'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_poke_6(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_url = url_pokeball
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 6:
                my_poke = poke_list[5]
                my_url = 'https://s3.us-east-2.amazonaws.com/pokepulp-assets/gifs/' + my_poke + '_gif.gif'
    return my_url

# update poke_1 text when optimization model is solved
@app.callback(
    Output('txt_poke_1', 'children'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_txt_1(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_poke = ''
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 1:
                my_poke = poke_list[0]
    return my_poke

# update poke_2 text when optimization model is solved
@app.callback(
    Output('txt_poke_2', 'children'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_txt_2(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_poke = ''
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 2:
                my_poke = poke_list[1]
    return my_poke

# update poke_3 text when optimization model is solved
@app.callback(
    Output('txt_poke_3', 'children'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_txt_3(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_poke = ''
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 3:
                my_poke = poke_list[2]
    return my_poke

# update poke_4 text when optimization model is solved
@app.callback(
    Output('txt_poke_4', 'children'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_txt_4(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_poke = ''
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 4:
                my_poke = poke_list[3]
    return my_poke

# update poke_5 text when optimization model is solved
@app.callback(
    Output('txt_poke_5', 'children'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_txt_5(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_poke = ''
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 5:
                my_poke = poke_list[4]
    return my_poke

# update poke_6 text when optimization model is solved
@app.callback(
    Output('txt_poke_6', 'children'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_txt_6(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_poke = ''
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 6:
                my_poke = poke_list[5]
    return my_poke

# show objective value on page when optimization model is solved
@app.callback(
    Output('div_obj_value', 'children'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp')])
def show_obj_value(opt_res, btn_add_ncts, btn_rem_ncts, btn_solve_ncts, btn_obj_ncts):
    obj_val = '?'
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            opt_status = opt_res.get('status')
            if opt_status == 'Infeasible':
                return obj_val
            obj_val = opt_res.get('obj_value')
    return obj_val

# show status of optimization model when it is solved
@app.callback(
    Output('div_obj_status', 'children'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp')])
def show_obj_status(opt_res, btn_add_ncts, btn_rem_ncts, btn_solve_ncts, btn_obj_ncts):
    opt_status = ''
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            opt_status = opt_res.get('status')
    return opt_status

# update message box when model is solved
@app.callback(
    Output('div_message', 'children'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp')],
     [State('dt_constraints', 'selected_row_indices'),
      State('txtbox_const_rhs', 'value')])
def show_obj_status(opt_res, btn_add_ncts, btn_rem_ncts, btn_solve_ncts, btn_obj_ncts, selected_rows, my_rhs):
    msg = 'Welcome to PokePuLP! Set up your optimization problem and then click SOLVE!'
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):    
        opt_status = opt_res.get('status')
        if opt_status == 'Optimal':
            msg = 'You found the optimal pokemon team!'
        elif opt_status == 'Infeasible':
            msg = 'The problem is infeasible. Try adjusting the constraints and re-solving.'
    else:
        if int(btn_add_ncts) > 0 or int(btn_rem_ncts) > 0 or int(btn_obj_ncts) > 0:
            msg = 'Click SOLVE once you are finished adjusting the model.'
            if int(btn_rem_ncts) > int(btn_add_ncts) and int(btn_rem_ncts) > int(btn_obj_ncts) and min(selected_rows) <= 1:
                msg = 'WARNING: The first two constraints cannot be removed.'
            if int(btn_add_ncts) > int(btn_rem_ncts) and int(btn_add_ncts) > int(btn_obj_ncts) and good_rhs(my_rhs) == False:
                msg = 'WARNING: Constraint RHS value must be an integer >= 0.'
    return msg

# update team stats graph
@app.callback(
    Output('graph_team_stats', 'figure'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_team_stats_graph(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    graph_default = {'data': [{'x': ['HP', 'Attack', 'Defense', 'Speed', 'Special'], 'y': [0, 0, 0, 0, 0], 'type': 'bar'}],
                     'layout': {'plot_bgcolor': 'white', 'paper_bgcolor': 'WhiteSmoke', 'font': {'color': 'black'},
                                'margin': {'l': 25, 'b': 20, 't': 25, 'r': 5}, 'showlegend':False, 'title':'Team Stats',
                                'yaxis': {'range': [0, 100]}}}
    graph_output = graph_default
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            opt_status = opt_res.get('status')
            if opt_status == 'Optimal':
                poke_list = opt_res.get('poke_list')
                stat_hp = sum([param_stats.get((p, 'HP')) for p in poke_list])
                stat_attack = sum([param_stats.get((p, 'ATTACK')) for p in poke_list])
                stat_defense = sum([param_stats.get((p, 'DEFENSE')) for p in poke_list])
                stat_speed = sum([param_stats.get((p, 'SPEED')) for p in poke_list])
                stat_special = sum([param_stats.get((p, 'SPECIAL')) for p in poke_list])
                graph_output = {'data': [{'x': ['HP', 'Attack', 'Defense', 'Speed', 'Special'], 'y': [stat_hp, stat_attack, stat_defense, stat_speed, stat_special], 'type': 'bar', 'name': 'SF'}],
                                 'layout': {'plot_bgcolor': 'white', 'paper_bgcolor': 'WhiteSmoke', 'font': {'color': 'black'},
                                            'margin': {'l': 25, 'b': 20, 't': 25, 'r': 5}, 'showlegend':False, 'title':'Team Stats'}}
    return graph_output

# helper function to sort constraints df by moving blanks to end
def sort_constraints(constraint_df):
    const_present = constraint_df[constraint_df.SIGN!='']
    const_blank = constraint_df[constraint_df.SIGN=='']
    const_sorted = const_present.append(const_blank, ignore_index=True).reset_index(drop=True)
    const_sorted.index = ['a','b','c','d','e','f']
    return(const_sorted)

# helper function to check if RHS constraint value is ok
def good_rhs(val):
    try: 
        val_int = int(val)
        if val_int >= 0:
            return True
        else:
            return False
    except ValueError:
        return False


if __name__ == '__main__':
    app.run_server(debug=False)

    
    