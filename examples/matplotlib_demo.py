""" This example shows how to embed matplotlib plots over the web by passing 
the plots in svg format over the jigna bridge.
"""

#### Imports ####

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from StringIO import StringIO
from traits.api import HasTraits, CInt, Str, Property, Enum
from jigna.api import View

def get_svg_plot():
    """Return SVG string of a matplotlib plot.
    """
    stream = StringIO()
    plt.savefig(stream, format='svg')
    stream.seek(0)
    return stream.buf

def get_png_plot():
    """Return PNG string of a matplotlib plot after base64 encoding it.
    """
    stream = StringIO()
    plt.savefig(stream, format='png')
    stream.seek(0)
    return stream.buf.encode('base64')

#### Domain model ####

class MyPlot(HasTraits):
    scaling_factor = CInt(1)

    format = Enum('png', 'svg')

    plot_output = Property(Str, depends_on='scaling_factor')

    def _get_plot_output(self):
        x = np.linspace(-2*np.pi, 2*np.pi, 200)
        y = np.sin(self.scaling_factor*x)/x
        plt.clf()
        plt.plot(x, y)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title("sin(%s x)/x"%self.scaling_factor)
        
        get_plot_output = dict(svg=get_svg_plot, png=get_png_plot)

        return get_plot_output[self.format]()        

#### UI layer ####

body_html_png = """
    <div>
        Scaling factor: <input type="range" ng-model="model.scaling_factor"
                        min=0 max=30><br>
        Plot:<br>
        <div><img src="data:image/png;base64,{{model.plot_output}}"></div>
    </div>
"""

body_html_svg = """
    <div>
        Scaling factor: <input type="range" ng-model="model.scaling_factor"
                        min=0 max=30><br>
        Plot:<br>
        <div ng-bind-html-unsafe="model.plot_output">{{model.plot_output}}</div>
    </div>
"""

#### Entry point ####

def main():
    model = MyPlot(format='svg')
    view = View(body_html=body_html_svg)
    view.serve(model=model)

if __name__ == '__main__':
    main()
