# Standard library imports
import json

# Enthought library imports
from traits.api import Instance, on_trait_change, HasTraits
from traitsui.api import Menu
from pyface.action.api import Action, Separator, Group
from pyface.qt import QtGui

def serialize(obj):
    """ Convert a python object to JS by serialization/deserialization. If one
    of the traits could not be converted, it's possibly a HasTraits object,
    in which case, it is serialized by repeating the process for that trait.
    """
    try:
        serialized = json.dumps(obj)
    except TypeError:
        serialized = json.dumps(None)
    return serialized

def get_value(obj, extended_trait_name):
    """ Obtain the value of given extended_trait_name of obj. An `extended_trait_name`
    should be same as the python syntax that is used to refer to the concerned
    variable.
    """
    return eval('obj.'+extended_trait_name, {'obj': obj})

###############################################################################
# Utility functions to generate TraitsUI menus from native menus.
###############################################################################

class _QAction(Action):
    """ A pyface Action class wrapping a native Qt QAction. """
    qaction = Instance(QtGui.QAction)

    def __init__(self, qaction):
        self.qaction = qaction
        super(_QAction, self).__init__(name=qaction.text(),
                                      id=qaction.text(),
                                      visible=qaction.isVisible(),
                                      enabled=qaction.isEnabled(),
                                      accelerator=qaction.shortcut().toString(),
                                      on_perform=qaction.trigger,
                                      )
        if qaction.isCheckable():
            self.style = 'toggle'
            self.checked = qaction.isChecked()

    # Fixme: trait change methods added as per requirement.
    @on_trait_change('visible')
    def _on_visible_changed(self, value):
        self.qaction.setVisible(value)

    @on_trait_change('enabled')
    def _on_enabled_changed(self, value):
        self.qaction.setEnabled(value)

def Action_from_QAction(qaction):
    """ Create a pyface action from a QAction. """
    if qaction.isSeparator():
        return Separator()
    else:
        return _QAction(qaction)

def Menu_from_QMenu(qmenu):
    """ Create a TraitsUI Menu from a native Qt QMenu.
    Submenus are currently not supported, separators are supported.
    """
    qactions = qmenu.actions()
    groups = []
    grp_actions = []
    for action in reversed(qactions):
        action = Action_from_QAction(action)
        if isinstance(action, Separator):
            if len(grp_actions) > 0:
                groups.append(Group(*reversed(grp_actions)))
                grp_actions = []
            else:
                continue
        else:
            grp_actions.append(action)
    if len(grp_actions) > 0:
        groups.append(Group(*reversed(grp_actions)))
    menu = Menu(*groups)
    # Keep a reference to the original menu to prevent actions from being
    # destroyed then the menu is deleted.
    menu._qmenu = qmenu
    return menu
