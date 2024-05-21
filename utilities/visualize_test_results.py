from IPython.display import display_html
import pandas as pd
from tabulate import tabulate
from IPython import get_ipython


def visualize_in_terminal(sequences_results, INDEX_TO_SEQUENCE):
    tables = []

    for result in sequences_results:
        df = pd.DataFrame(result)

        table = df.pivot(index='Image', columns='Type', values='Error')
        tables.append(table)

    for i, table in enumerate(tables):
        print(INDEX_TO_SEQUENCE[i])
        print(tabulate(table, headers='keys', tablefmt='psql'))


def visualize_in_jupyter(sequences_results):
    tables = []

    for result in sequences_results:
        df = pd.DataFrame(result)

        table = df.pivot(index='Image', columns='Type', values='Error')
        tables.append(table)
        
    df1_styler = tables[0].style.set_table_attributes(
        "style='display:inline'").set_caption('20%')
    df2_styler = tables[1].style.set_table_attributes(
        "style='display:inline'").set_caption('16%')
    df3_styler = tables[2].style.set_table_attributes(
        "style='display:inline'").set_caption('15%')
    df4_styler = tables[3].style.set_table_attributes(
        "style='display:inline'").set_caption('5%')
    df5_styler = tables[4].style.set_table_attributes(
        "style='display:inline'").set_caption('3%')
    df6_styler = tables[5].style.set_table_attributes(
        "style='display:inline'").set_caption('0%')
    df7_styler = tables[6].style.set_table_attributes(
        "style='display:inline'").set_caption('New cam')

    display_html(df1_styler._repr_html_() + df2_styler._repr_html_() + df3_styler._repr_html_() +
                    df4_styler._repr_html_() + df5_styler._repr_html_() + df6_styler._repr_html_() + df7_styler._repr_html_(), raw=True)


def visualize_test_results(sequences_results, INDEX_TO_SEQUENCE):
    def is_notebook() -> bool:
        try:
            shell = get_ipython().__class__.__name__
            if shell == 'ZMQInteractiveShell':
                return True   # Jupyter notebook or qtconsole
            elif shell == 'TerminalInteractiveShell':
                return False  # Terminal running IPython
            else:
                return False  # Other type (?)
        except NameError:
            return False      # Probably standard Python interpreter

    if is_notebook():
        visualize_in_jupyter(sequences_results)
    else:
        visualize_in_terminal(sequences_results, INDEX_TO_SEQUENCE)
