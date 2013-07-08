from numpy import arange, pi, cos, sin

from traits.api import HasTraits, Range, Instance, \
        on_trait_change
from traitsui.api import View, Item, Group

from mayavi.core.api import PipelineBase
from mayavi.core.ui.api import MayaviScene, SceneEditor, \
                MlabSceneModel


dphi = pi/1000.
phi = arange(0.0, 2*pi + 0.5*dphi, dphi, 'd')

def curve(n_mer, n_long):
    mu = phi*n_mer
    x = cos(mu) * (1 + cos(n_long * mu/n_mer)*0.5)
    y = sin(mu) * (1 + cos(n_long * mu/n_mer)*0.5)
    z = 0.5 * sin(n_long*mu/n_mer)
    t = sin(mu)
    return x, y, z, t

class MyModel(HasTraits):
    n_meridional    = Range(0, 30, 6, )
    n_longitudinal  = Range(0, 30, 11, )

    scene = Instance(MlabSceneModel, ())

    plot = Instance(PipelineBase)

    # The layout of the dialog created
    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=250, width=300, show_label=False),
                Group(
                        '_', 'n_meridional', 'n_longitudinal',
                     ),
                resizable=True,
                )

    # When the scene is activated, or when the parameters are changed, we
    # update the plot.
    @on_trait_change('n_meridional,n_longitudinal,scene.activated')
    def update_plot(self):
        x, y, z, t = curve(self.n_meridional, self.n_longitudinal)
        if self.plot is None:
            self.plot = self.scene.mlab.plot3d(x, y, z, t,
                                tube_radius=0.025, colormap='Spectral')
        else:
            self.plot.mlab_source.set(x=x, y=y, z=z, scalars=t)

my_model = MyModel()
#my_model.configure_traits()
#ui = my_model.edit_traits()

from jigna.html_view import HTMLView
from jigna.session import show_simple_view

from jigna.editor_factories import _TU_RangeEditor
from jigna.editors.mayavi_editors import TUMayaviEditor

layout = View(Group(Item('scene', editor=TUMayaviEditor()),
                    Item('n_meridional', editor=_TU_RangeEditor()),
                    Item('n_longitudinal', editor=_TU_RangeEditor()),
                    ),
                    )

view = HTMLView(model=my_model, layout=layout)
show_simple_view(view)